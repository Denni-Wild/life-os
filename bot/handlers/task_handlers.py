"""
Обработчики для работы с задачами
"""

import logging
from datetime import datetime
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..services.todoist_service import TodoistService
from ..services.memory_service import MemoryService
from ..config import Config

logger = logging.getLogger(__name__)


async def capture_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /capture"""
    if not context.args:
        await update.message.reply_text(
            "📝 Использование: /capture <текст задачи>\n\n"
            "Пример: /capture Позвонить маме завтра"
        )
        return
    
    content = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    try:
        # Создаем экземпляры сервисов
        config = Config()
        memory_service = MemoryService()
        todoist_service = TodoistService(config) if config.todoist_api_token else None
        
        # Сохраняем задачу
        await memory_service.save_task(content)
        
        # Если настроен Todoist, создаем задачу там
        if todoist_service:
            await todoist_service.create_task(content)
        
        await update.message.reply_text(f"✅ Задача захвачена: \"{content}\"")
        logger.info(f"Задача захвачена пользователем {update.effective_user.id}: {content}")
        
    except Exception as e:
        logger.error(f"Ошибка при захвате задачи: {e}")
        await update.message.reply_text("❌ Произошла ошибка при захвате задачи")


async def tasks_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /tasks"""
    chat_id = update.effective_chat.id
    
    try:
        config = Config()
        todoist_service = TodoistService(config) if config.todoist_api_token else None
        
        if todoist_service:
            # Получаем задачи из Todoist
            tasks = await todoist_service.get_today_tasks()
            
            if not tasks:
                await update.message.reply_text("📋 На сегодня задач нет. Отличная работа! 🎉")
                return
            
            # Формируем список задач
            task_list = []
            for i, task in enumerate(tasks, 1):
                priority_emoji = ['🔵', '🟢', '🟡', '🔴'][task.priority - 1] if task.priority <= 4 else '⚪'
                due_date = f" ({task.due.date})" if task.due else ""
                labels = f" [{', '.join(task.labels)}]" if task.labels else ""
                
                task_text = f"{i}. {priority_emoji} {task.content}{due_date}{labels}"
                task_list.append(task_text)
            
            tasks_text = "\n".join(task_list)
            message = f"📋 *Задачи на сегодня:*\n\n{tasks_text}"
            
            # Создаем кнопки для завершения задач
            keyboard = []
            for i, task in enumerate(tasks[:5], 1):  # Максимум 5 кнопок
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ {i}. {task.content[:20]}...",
                        callback_data=f"complete_task:{task.id}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
        else:
            # Локальные задачи
            memory_service = MemoryService()
            tasks = await memory_service.get_today_tasks()
            
            if not tasks:
                await update.message.reply_text("📋 На сегодня задач нет. Отличная работа! 🎉")
                return
            
            task_list = []
            for i, task in enumerate(tasks, 1):
                task_list.append(f"{i}. {task['content']}")
            
            tasks_text = "\n".join(task_list)
            message = f"📋 *Задачи на сегодня:*\n\n{tasks_text}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        logger.info(f"Пользователь {update.effective_user.id} запросил список задач")
        
    except Exception as e:
        logger.error(f"Ошибка при получении задач: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении задач")


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status"""
    try:
        memory_service = MemoryService()
        areas = await memory_service.get_life_areas_status()
        
        if not areas:
            # Показываем стандартные области
            areas = [
                {"name": "Здоровье", "score": 7},
                {"name": "Карьера", "score": 8},
                {"name": "Отношения", "score": 9},
                {"name": "Финансы", "score": 6},
                {"name": "Личностный рост", "score": 8}
            ]
        
        status_lines = []
        for area in areas:
            score = area.get('score', 0)
            stars = "⭐" * score
            status_lines.append(f"{area['name']}: {stars} ({score}/10)")
        
        status_text = "\n".join(status_lines)
        message = f"📊 *Статус жизненных областей:*\n\n{status_text}"
        
        # Создаем кнопки для быстрой оценки
        keyboard = []
        for area in areas[:3]:  # Максимум 3 области
            row = []
            for score in range(1, 6):  # Кнопки 1-5
                row.append(InlineKeyboardButton(
                    str(score),
                    callback_data=f"area_score:{area['name']}:{score}"
                ))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        logger.info(f"Пользователь {update.effective_user.id} запросил статус жизненных областей")
        
    except Exception as e:
        logger.error(f"Ошибка при получении статуса: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении статуса") 