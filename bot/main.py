#!/usr/bin/env python3
"""
Life OS Telegram Bot
Персональный AI-помощник для управления жизнью через Telegram
"""

import asyncio
import logging
import os
import time
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)

from .config import Config, load_config
from .handlers import (
    start_handler, help_handler, capture_handler, tasks_handler,
    status_handler, review_handler, assess_handler, schedule_handler,
    mood_handler, habits_handler, unknown_handler,
    voice_handler, voice_callback_handler, text_edit_handler
)
from .services.todoist_service import TodoistService
from .services.memory_service import MemoryService
from .utils.logger import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Conversation states
CHOOSING, TYPING_REASON = range(2)

class LifeOSBot:
    """Основной класс бота Life OS"""
    
    def __init__(self):
        self.config = load_config()
        self.todoist_service = TodoistService(self.config)
        self.memory_service = MemoryService()
        self.application = None
        
    async def post_init(self, app: Application) -> None:
        """Выполняется после инициализации приложения"""
        commands = [
            BotCommand("start", "🚀 Запуск Life OS Bot"),
            BotCommand("help", "❓ Справка по командам"),
            BotCommand("capture", "📝 Быстрый захват задачи или идеи"),
            BotCommand("tasks", "📋 Задачи на сегодня"),
            BotCommand("status", "📊 Статус жизненных областей"),
            BotCommand("review", "🔍 Ежедневный обзор"),
            BotCommand("assess", "📈 Оценка жизни"),
            BotCommand("schedule", "📅 Расписание на сегодня"),
            BotCommand("mood", "😊 Записать настроение"),
            BotCommand("habits", "✅ Отслеживание привычек"),
        ]
        await app.bot.set_my_commands(commands)
        logger.info("Команды бота настроены")
    
    def setup_handlers(self):
        """Настройка обработчиков сообщений"""
        
        # Основные команды
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("help", help_handler))
        self.application.add_handler(CommandHandler("capture", capture_handler))
        self.application.add_handler(CommandHandler("tasks", tasks_handler))
        self.application.add_handler(CommandHandler("status", status_handler))
        self.application.add_handler(CommandHandler("review", review_handler))
        self.application.add_handler(CommandHandler("assess", assess_handler))
        self.application.add_handler(CommandHandler("schedule", schedule_handler))
        self.application.add_handler(CommandHandler("mood", mood_handler))
        self.application.add_handler(CommandHandler("habits", habits_handler))
        
        # Обработка callback запросов (кнопки)
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Обработка голосовых сообщений
        self.application.add_handler(
            MessageHandler(filters.VOICE, voice_handler)
        )
        
        # Обработка обычных сообщений для быстрого захвата и редактирования
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handle_text_message
            )
        )
        
        # Обработка неизвестных команд
        self.application.add_handler(
            MessageHandler(filters.COMMAND, unknown_handler)
        )
        
        logger.info("Обработчики настроены")
    
    def _can_resolve_api(self) -> bool:
        """Проверить, что api.telegram.org резолвится"""
        try:
            socket.getaddrinfo("api.telegram.org", 443)
            return True
        except Exception as e:
            logger.warning(f"DNS недоступен: {e}")
            return False
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback запросов"""
        try:
            query = update.callback_query
            await query.answer()
            data = query.data
            
            if data.startswith("capture_task:"):
                content = data.split(":", 1)[1]
                await self.capture_task(content, update.effective_chat.id)
                await query.edit_message_text("✅ Задача захвачена")
            elif data.startswith("capture_idea:"):
                content = data.split(":", 1)[1]
                await self.capture_idea(content, update.effective_chat.id)
                await query.edit_message_text("💡 Идея захвачена")
            elif data.startswith("voice_"):
                # Обрабатываем голосовые callback через voice_callback_handler
                await voice_callback_handler(update, context)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {e}")
            await query.edit_message_text("❌ Произошла ошибка при обработке запроса")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных текстовых сообщений для быстрого захвата и редактирования"""
        text = update.message.text
        chat_id = update.effective_chat.id
        
        # Сначала проверяем, не является ли это редактированием голосового сообщения
        try:
            await text_edit_handler(update, context)
            return
        except Exception:
            pass  # Если не редактирование, продолжаем обычную обработку
        
        # Если сообщение короткое, предлагаем захватить
        if len(text) < 100:
            keyboard = [
                [
                    InlineKeyboardButton("📝 Захватить как задачу", 
                                       callback_data=f"capture_task:{text}"),
                    InlineKeyboardButton("💡 Захватить как идею", 
                                       callback_data=f"capture_idea:{text}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💭 Хотите захватить это сообщение?",
                reply_markup=reply_markup
            )
    
    async def capture_task(self, content: str, chat_id: int):
        """Захват задачи"""
        try:
            # Сохраняем в локальный файл
            await self.memory_service.save_task(content)
            
            # Если настроен Todoist, создаем задачу там
            if self.config.todoist_api_token:
                await self.todoist_service.create_task(content)
                
            logger.info(f"Задача захвачена: {content}")
            
        except Exception as e:
            logger.error(f"Ошибка при захвате задачи: {e}")
            raise
    
    async def capture_idea(self, content: str, chat_id: int):
        """Захват идеи"""
        try:
            await self.memory_service.save_idea(content)
            logger.info(f"Идея захвачена: {content}")
            
        except Exception as e:
            logger.error(f"Ошибка при захвате идеи: {e}")
            raise
    
    async def update_life_area_score(self, area: str, score: int, chat_id: int):
        """Обновление оценки жизненной области"""
        try:
            await self.memory_service.save_life_area_score(area, score)
            logger.info(f"Оценка области '{area}' обновлена: {score}")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении оценки: {e}")
            raise
    
    async def complete_task(self, task_id: str, chat_id: int):
        """Завершение задачи"""
        try:
            if self.config.todoist_api_token:
                await self.todoist_service.complete_task(task_id)
            await self.memory_service.complete_task(task_id)
            logger.info(f"Задача {task_id} выполнена")
            
        except Exception as e:
            logger.error(f"Ошибка при завершении задачи: {e}")
            raise
    
    def start(self):
        """Запуск бота (синхронный, с ретраями при сетевых сбоях)"""
        backoff_seconds = 5
        max_backoff = 300
        while True:
            try:
                if not self._can_resolve_api():
                    logger.warning(f"api.telegram.org недоступен. Повтор через {backoff_seconds} сек")
                    time.sleep(backoff_seconds)
                    backoff_seconds = min(backoff_seconds * 2, max_backoff)
                    continue
                
                # Создаем приложение
                self.application = Application.builder().token(self.config.telegram_token).build()
                
                # post_init для асинхронной настройки команд
                self.application.post_init = self.post_init
                
                # Настраиваем обработчики
                self.setup_handlers()
                
                # Запускаем бота (блокирующий вызов)
                logger.info("🤖 Life OS Bot запущен...")
                self.application.run_polling(allowed_updates=Update.ALL_TYPES)
                
                # Если run_polling завершился корректно (остановка пользователем), выходим
                logger.info("Бот остановлен корректно")
                break
                
            except Exception as e:
                logger.error(f"Ошибка запуска бота: {e}")
                logger.info(f"Повторный запуск через {backoff_seconds} сек...")
                time.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2, max_backoff)
                continue


def main():
    """Главная функция (синхронная)"""
    bot = LifeOSBot()
    bot.start() 