#!/usr/bin/env python3
"""
Скрипт для создания файла .env с переменными окружения
"""

import os
from pathlib import Path

def create_env_file():
    """Создает файл .env с переменными окружения"""
    
    env_content = """# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Todoist Configuration (опционально)
TODOIST_API_TOKEN=your_todoist_api_token_here

# Bot Settings
BOT_ADMIN_USER_ID=your_telegram_user_id_here
BOT_DEBUG_MODE=true

# Gmail Configuration (планируется)
GMAIL_CLIENT_ID=your_gmail_client_id_here
GMAIL_CLIENT_SECRET=your_gmail_client_secret_here
GMAIL_REDIRECT_URI=your_gmail_redirect_uri_here
"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  Файл .env уже существует!")
        response = input("Хотите перезаписать его? (y/N): ")
        if response.lower() != 'y':
            print("❌ Файл .env не был изменен")
            return
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Файл .env создан успешно!")
        print("\n📝 Следующие шаги:")
        print("1. Получите токен Telegram бота у @BotFather")
        print("2. Получите ваш User ID у @userinfobot")
        print("3. Замените значения в файле .env")
        print("4. Запустите бота: python run_bot.py")
        
    except Exception as e:
        print(f"❌ Ошибка создания файла .env: {e}")

if __name__ == "__main__":
    create_env_file() 