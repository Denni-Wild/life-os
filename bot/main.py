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
    mood_handler, habits_handler, unknown_handler
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
        
        # Отправляем уведомление администратору о запуске
        await self.send_admin_startup_notification()
    
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
        
        # Обработка обычных сообщений для быстрого захвата
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
            elif data.startswith("area_score:"):
                # Обработка оценки жизненных областей (старый формат)
                parts = data.split(":")
                if len(parts) == 3:
                    area = parts[1]
                    score = int(parts[2])
                    await self.update_life_area_score(area, score, update.effective_chat.id)
                    
                    # Обновляем сообщение с подтверждением
                    await query.edit_message_text(
                        f"✅ Оценка области '{area}' обновлена: {score}/10\n\n"
                        f"Продолжайте оценивать другие области или используйте /status для просмотра всех оценок."
                    )
                else:
                    await query.edit_message_text("❌ Ошибка в данных оценки")
            elif data.startswith("area_info:"):
                # Пользователь выбрал область жизни
                area = data.split(":", 1)[1]
                context.user_data['selected_area'] = area
                
                # Показываем сообщение о выбранной области
                await query.edit_message_text(
                    f"🎯 Выбрана область: *{area}*\n\n"
                    f"Теперь выберите оценку от 1 до 10:",
                    parse_mode='Markdown',
                    reply_markup=query.message.reply_markup
                )
                
                # Показываем всплывающее уведомление
                await query.answer(f"Выбрана область: {area}")
            elif data.startswith("score_select:"):
                # Пользователь выбрал оценку
                if 'selected_area' not in context.user_data:
                    await query.edit_message_text(
                        "❌ Сначала выберите область жизни!\n\n"
                        "Используйте /assess для начала оценки."
                    )
                    return
                
                score = int(data.split(":", 1)[1])
                area = context.user_data['selected_area']
                
                # Сохраняем оценку
                await self.update_life_area_score(area, score, update.effective_chat.id)
                
                # Очищаем выбранную область
                del context.user_data['selected_area']
                
                # Показываем всплывающее уведомление
                await query.answer(f"Оценка {area}: {score}/10 сохранена!")
                
                # Обновляем сообщение с подтверждением
                await query.edit_message_text(
                    f"✅ Оценка области '{area}' обновлена: {score}/10\n\n"
                    f"Продолжайте оценивать другие области или используйте /status для просмотра всех оценок.",
                    reply_markup=query.message.reply_markup
                )
            elif data == "show_current_scores":
                # Показываем текущие оценки
                try:
                    scores = await self.memory_service.get_life_area_scores()
                    if scores:
                        scores_text = "📊 *Текущие оценки жизненных областей:*\n\n"
                        for area, score in scores.items():
                            scores_text += f"• {area}: {score}/10\n"
                    else:
                        scores_text = "📊 Пока нет сохраненных оценок.\n\nНачните оценку с помощью /assess"
                    
                    await query.edit_message_text(
                        scores_text,
                        parse_mode='Markdown',
                        reply_markup=query.message.reply_markup
                    )
                    
                    # Показываем всплывающее уведомление
                    await query.answer("Текущие оценки загружены")
                except Exception as e:
                    logger.error(f"Ошибка при получении оценок: {e}")
                    await query.edit_message_text(
                        "❌ Ошибка при получении оценок",
                        reply_markup=query.message.reply_markup
                    )
            elif data.startswith("habit_complete:"):
                # Пользователь отметил выполнение привычки
                habit = data.split(":", 1)[1]
                await self.memory_service.save_habit(habit)
                
                # Показываем всплывающее уведомление
                await query.answer(f"✅ Привычка '{habit}' отмечена!")
                
                # Обновляем сообщение с подтверждением
                await query.edit_message_text(
                    f"✅ Привычка *{habit.replace('_', ' ').title()}* отмечена!\n\n"
                    f"Продолжайте отмечать другие привычки или используйте /habits для повторного просмотра.",
                    parse_mode='Markdown'
                )
                
                logger.info(f"Привычка '{habit}' отмечена пользователем {update.effective_user.id}")
            elif data == "add_custom_habit":
                # Пользователь хочет добавить свою привычку
                await query.edit_message_text(
                    "✍️ *Добавление новой привычки*\n\n"
                    "Отправьте название вашей привычки в следующем сообщении.\n\n"
                    "Например:\n"
                    "• Пить воду\n"
                    "• Делать зарядку\n"
                    "• Читать книги\n\n"
                    "Или используйте /habits для возврата к списку популярных привычек.",
                    parse_mode='Markdown'
                )
                
                # Показываем всплывающее уведомление
                await query.answer("Ожидаю название привычки...")
                
                # Устанавливаем состояние ожидания привычки
                context.user_data['waiting_for_habit'] = True
            elif data == "habit_category_header":
                # Заголовок категории привычек (неактивная кнопка)
                await query.answer("Категория привычек")
            elif data == "habits_stats":
                # Показываем статистику привычек
                try:
                    habits = await self.memory_service.get_habits_stats()
                    if habits:
                        stats_text = "📊 *Статистика привычек:*\n\n"
                        for habit, count in habits.items():
                            stats_text += f"• {habit.replace('_', ' ').title()}: {count} раз\n"
                    else:
                        stats_text = "📊 Пока нет отмеченных привычек.\n\nНачните отслеживать привычки!"
                    
                    await query.edit_message_text(
                        stats_text,
                        parse_mode='Markdown',
                        reply_markup=query.message.reply_markup
                    )
                    
                    # Показываем всплывающее уведомление
                    await query.answer("Статистика загружена")
                except Exception as e:
                    logger.error(f"Ошибка при получении статистики привычек: {e}")
                    await query.edit_message_text(
                        "❌ Ошибка при получении статистики привычек",
                        reply_markup=query.message.reply_markup
                    )
        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {e}")
            await query.edit_message_text("❌ Произошла ошибка при обработке запроса")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных текстовых сообщений для быстрого захвата"""
        text = update.message.text
        chat_id = update.effective_chat.id
        
        # Проверяем, ожидаем ли мы ввод привычки
        if context.user_data.get('waiting_for_habit'):
            # Пользователь вводит название новой привычки
            await self.memory_service.save_habit(text)
            
            # Очищаем состояние ожидания
            del context.user_data['waiting_for_habit']
            
            # Отправляем подтверждение
            await update.message.reply_text(
                f"✅ Новая привычка *{text}* добавлена и отмечена!\n\n"
                f"Используйте /habits для просмотра всех привычек.",
                parse_mode='Markdown'
            )
            
            logger.info(f"Новая привычка '{text}' добавлена пользователем {update.effective_user.id}")
            return
        
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
    
    async def send_admin_startup_notification(self):
        """Отправка уведомления администратору о запуске бота"""
        if not self.config.admin_user_id:
            logger.warning("Admin user ID не настроен, уведомление не отправлено")
            return
            
        try:
            # Получаем информацию о системе
            import platform
            import psutil
            
            system_info = f"🖥️ {platform.system()} {platform.release()}"
            python_version = f"🐍 Python {platform.python_version()}"
            
            # Получаем информацию о памяти
            memory = psutil.virtual_memory()
            memory_info = f"💾 RAM: {memory.used // (1024**3)}GB/{memory.total // (1024**3)}GB"
            
            # Получаем текущее время
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"""
🚀 **Life OS Bot запущен!**

⏰ Время запуска: {current_time}
{system_info}
{python_version}
{memory_info}

✅ Бот готов к работе!
            """.strip()
            
            await self.application.bot.send_message(
                chat_id=self.config.admin_user_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"Уведомление о запуске отправлено администратору {self.config.admin_user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администратору: {e}")

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