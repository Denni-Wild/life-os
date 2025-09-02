"""
Базовые обработчики команд
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    welcome_message = f"""
🤖 *Добро пожаловать в Life OS Bot, {user.first_name}!*

Я ваш персональный AI-помощник для управления жизнью и достижения целей.

*Основные возможности:*
• 📝 Быстрый захват задач и идей
• 🎤 Распознавание голосовых сообщений
• 📋 Управление задачами через Todoist
• 📊 Отслеживание жизненных областей
• 🔍 Ежедневные обзоры и оценки
• 😊 Логирование настроения
• ✅ Отслеживание привычек

*Команды:*
/help - Показать все команды
/capture - Быстрый захват
/tasks - Задачи на сегодня
/status - Статус жизненных областей

*🎤 Голосовые сообщения:*
Отправьте голосовое сообщение для распознавания речи!

Начните с /help для получения полного списка команд!
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')
    logger.info(f"Пользователь {user.id} запустил бота")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_message = """
📚 *Life OS Bot - Справочник команд*

*Основные команды:*
/start - Запуск бота
/help - Этот справочник

*Захват и управление:*
/capture - Быстрый захват задачи или идеи
/tasks - Показать задачи на сегодня
/status - Статус жизненных областей

*Обзоры и оценки:*
/review - Начать ежедневный обзор
/assess - Начать оценку жизни
/schedule - Показать расписание на сегодня

*Отслеживание:*
/mood - Записать настроение
/habits - Отслеживание привычек

*🎤 Голосовые сообщения:*
Отправьте голосовое сообщение, и бот:
• Распознает речь на русском языке
• Покажет текст для подтверждения
• Позволит отредактировать текст
• Обработает как ответ на предыдущую команду

*Примеры использования:*
• /capture Позвонить маме завтра
• /mood 8 - Отличное настроение
• /habits exercise - Отметить тренировку
• 🎤 Голосовое сообщение "Нужно купить хлеб"

*Быстрый захват:*
Просто отправьте сообщение боту, и он предложит захватить его как задачу или идею!
    """
    
    await update.message.reply_text(help_message, parse_mode='Markdown')
    logger.info(f"Пользователь {update.effective_user.id} запросил справку")


async def unknown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных команд"""
    await update.message.reply_text(
        "❌ Извините, я не понимаю эту команду. Используйте /help для получения списка доступных команд."
    )
    logger.warning(f"Неизвестная команда от пользователя {update.effective_user.id}: {update.message.text}") 