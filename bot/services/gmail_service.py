"""
Сервис для интеграции с Gmail API
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Paths for credentials
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'token.json')
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'credentials.json')


class GmailService:
    """Сервис для работы с Gmail API"""
    
    def __init__(self):
        self.service = None
        self.creds = None
    
    def _load_saved_credentials(self) -> Optional[Credentials]:
        """Загрузить сохраненные учетные данные"""
        try:
            if os.path.exists(TOKEN_PATH):
                with open(TOKEN_PATH, 'r') as token:
                    creds = Credentials.from_authorized_user_info(
                        json.load(token), SCOPES
                    )
                return creds
        except Exception as e:
            logger.error(f"Ошибка загрузки токена: {e}")
        return None
    
    def _save_credentials(self, creds: Credentials) -> None:
        """Сохранить учетные данные"""
        try:
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
            logger.info("Учетные данные сохранены")
        except Exception as e:
            logger.error(f"Ошибка сохранения токена: {e}")
    
    def _authorize(self) -> Credentials:
        """Авторизация в Gmail API"""
        creds = self._load_saved_credentials()
        
        # Если нет валидных учетных данных, запросить их
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Ошибка обновления токена: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        f"Файл credentials.json не найден по пути: {CREDENTIALS_PATH}\n"
                        "Скачайте его из Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            self._save_credentials(creds)
        
        return creds
    
    async def connect(self) -> None:
        """Подключиться к Gmail API"""
        try:
            self.creds = self._authorize()
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Подключение к Gmail API установлено")
        except Exception as e:
            logger.error(f"Ошибка подключения к Gmail API: {e}")
            raise
    
    async def list_messages(self, max_results: int = 100) -> List[Dict]:
        """Получить список сообщений"""
        if not self.service:
            await self.connect()
        
        try:
            response = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = response.get('messages', [])
            if not messages:
                logger.info("Сообщения не найдены")
                return []
            
            logger.info(f"Найдено {len(messages)} сообщений")
            return messages
            
        except HttpError as error:
            logger.error(f"Ошибка Gmail API: {error}")
            return []
    
    async def get_message_details(self, message_id: str) -> Optional[Dict]:
        """Получить детали сообщения"""
        if not self.service:
            await self.connect()
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            # Извлечь заголовки
            headers = message.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            return {
                'id': message_id,
                'subject': subject,
                'from': sender,
                'date': date,
                'snippet': message.get('snippet', ''),
                'thread_id': message.get('threadId', '')
            }
            
        except HttpError as error:
            logger.error(f"Ошибка получения сообщения {message_id}: {error}")
            return None
    
    async def get_recent_messages(self, max_results: int = 10) -> List[Dict]:
        """Получить последние сообщения с деталями"""
        messages = await self.list_messages(max_results)
        detailed_messages = []
        
        for message in messages:
            details = await self.get_message_details(message['id'])
            if details:
                detailed_messages.append(details)
        
        return detailed_messages
    
    async def search_messages(self, query: str, max_results: int = 50) -> List[Dict]:
        """Поиск сообщений по запросу"""
        if not self.service:
            await self.connect()
        
        try:
            response = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = response.get('messages', [])
            detailed_messages = []
            
            for message in messages:
                details = await self.get_message_details(message['id'])
                if details:
                    detailed_messages.append(details)
            
            logger.info(f"Найдено {len(detailed_messages)} сообщений по запросу: {query}")
            return detailed_messages
            
        except HttpError as error:
            logger.error(f"Ошибка поиска сообщений: {error}")
            return []
    
    def format_message_for_display(self, message: Dict) -> str:
        """Форматировать сообщение для отображения"""
        return f"""
📧 *{message.get('subject', 'Без темы')}*
👤 От: {message.get('from', 'Неизвестно')}
📅 Дата: {message.get('date', 'Неизвестно')}
📝 {message.get('snippet', 'Нет предварительного просмотра')}
        """.strip()


async def main():
    """Основная функция для тестирования"""
    gmail_service = GmailService()
    
    try:
        print("🔍 Получение последних сообщений...")
        messages = await gmail_service.get_recent_messages(5)
        
        if messages:
            print(f"\n📧 Найдено {len(messages)} сообщений:\n")
            for i, message in enumerate(messages, 1):
                print(f"{i}. {gmail_service.format_message_for_display(message)}")
                print("-" * 50)
        else:
            print("Сообщения не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 