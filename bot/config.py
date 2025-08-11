"""
Конфигурация для Life OS Telegram Bot
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Конфигурация бота"""
    
    # Telegram
    telegram_token: str
    admin_user_id: Optional[str] = None
    debug_mode: bool = False
    
    # Todoist
    todoist_api_token: Optional[str] = None
    
    # Gmail (планируется)
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    gmail_redirect_uri: Optional[str] = None
    
    # Пути
    memory_path: str = "memory"
    tasks_path: str = "memory/gtd"
    templates_path: str = "templates"
    
    def __post_init__(self):
        """Валидация конфигурации после инициализации"""
        # Создаем необходимые директории
        os.makedirs(self.memory_path, exist_ok=True)
        os.makedirs(self.tasks_path, exist_ok=True)
        os.makedirs(self.templates_path, exist_ok=True)


def load_config() -> Config:
    """Загрузка конфигурации из переменных окружения"""
    
    return Config(
        telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        admin_user_id=os.getenv("BOT_ADMIN_USER_ID"),
        debug_mode=os.getenv("BOT_DEBUG_MODE", "true").lower() == "true", #False
        todoist_api_token=os.getenv("TODOIST_API_TOKEN"),
        gmail_client_id=os.getenv("GMAIL_CLIENT_ID"),
        gmail_client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        gmail_redirect_uri=os.getenv("GMAIL_REDIRECT_URI"),
    ) 