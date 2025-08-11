"""
Обработчики для отслеживания настроения и привычек
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..services.memory_service import MemoryService

logger = logging.getLogger(__name__)


async def mood_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /mood - логирование настроения"""
    
    # Проверяем, есть ли аргументы
    if context.args:
        try:
            score = int(context.args[0])
            if 1 <= score <= 10:
                await _save_mood(score, update, context)
                return
            else:
                await update.message.reply_text("❌ Оценка настроения должна быть от 1 до 10")
                return
        except ValueError:
            await update.message.reply_text("❌ Оценка настроения должна быть числом от 1 до 10")
            return
    
    # Если аргументов нет, показываем кнопки
    mood_message = """
😊 *Записать настроение*

Как вы себя чувствуете сегодня?

Выберите оценку от 1 до 10:
1-2: Очень плохо 😢
3-4: Плохо 😔
5-6: Нормально 😐
7-8: Хорошо 😊
9-10: Отлично 😍
    """
    
    # Создаем кнопки для оценки настроения
    keyboard = []
    for i in range(1, 11):
        emoji = _get_mood_emoji(i)
        keyboard.append(InlineKeyboardButton(f"{emoji} {i}", callback_data=f"mood_score:{i}"))
    
    # Разбиваем на ряды по 5 кнопок
    rows = [keyboard[i:i+5] for i in range(0, len(keyboard), 5)]
    reply_markup = InlineKeyboardMarkup(rows)
    
    await update.message.reply_text(
        mood_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    logger.info(f"Пользователь {update.effective_user.id} запросил логирование настроения")


async def habits_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /habits - отслеживание привычек"""
    
    # Проверяем, есть ли аргументы
    if context.args:
        habit = " ".join(context.args)
        await _save_habit(habit, update, context)
        return
    
    # Если аргументов нет, показываем популярные привычки
    habits_message = """
✅ *Отслеживание привычек*

Отметьте выполненные привычки или добавьте новую:

*Популярные привычки:*
    """
    
    popular_habits = [
        "exercise", "meditation", "reading", "drinking_water",
        "sleep_early", "healthy_eating", "journaling", "walking"
    ]
    
    keyboard = []
    for habit in popular_habits:
        habit_name = habit.replace("_", " ").title()
        keyboard.append(InlineKeyboardButton(
            f"✅ {habit_name}", 
            callback_data=f"habit_complete:{habit}"
        ))
    
    # Разбиваем на ряды по 2 кнопки
    rows = [keyboard[i:i+2] for i in range(0, len(keyboard), 2)]
    
    # Добавляем кнопку для новой привычки
    rows.append([InlineKeyboardButton("➕ Добавить свою", callback_data="add_custom_habit")])
    
    reply_markup = InlineKeyboardMarkup(rows)
    
    await update.message.reply_text(
        habits_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    logger.info(f"Пользователь {update.effective_user.id} запросил отслеживание привычек")


async def _save_mood(score: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранить настроение"""
    try:
        memory_service = MemoryService()
        await memory_service.save_mood(score)
        
        emoji = _get_mood_emoji(score)
        await update.message.reply_text(f"{emoji} Настроение записано: {score}/10")
        
        logger.info(f"Настроение {score}/10 сохранено пользователем {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении настроения: {e}")
        await update.message.reply_text("❌ Произошла ошибка при записи настроения")


async def _save_habit(habit: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранить привычку"""
    try:
        memory_service = MemoryService()
        await memory_service.save_habit(habit)
        
        await update.message.reply_text(f"✅ Привычка отмечена: {habit}")
        
        logger.info(f"Привычка '{habit}' сохранена пользователем {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении привычки: {e}")
        await update.message.reply_text("❌ Произошла ошибка при отметке привычки")


def _get_mood_emoji(score: int) -> str:
    """Получить эмодзи для настроения"""
    if score >= 9:
        return "😍"
    elif score >= 7:
        return "😊"
    elif score >= 5:
        return "😐"
    elif score >= 3:
        return "😔"
    else:
        return "😢" 