"""
Обработчики для отслеживания жизненных показателей
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
    
    # Группируем привычки по категориям
    habit_categories = {
        "🏃‍♂️ Здоровье": [
            "exercise", "meditation", "drinking_water", "sleep_early", 
            "healthy_eating", "walking", "stretching", "vitamins"
        ],
        "📚 Развитие": [
            "reading", "journaling", "learning", "practice_skills", 
            "planning", "goal_review"
        ],
        "💼 Продуктивность": [
            "morning_routine", "evening_routine", "time_tracking", 
            "task_prioritization", "break_taking"
        ],
        "🧘‍♀️ Ментальное здоровье": [
            "gratitude", "mindfulness", "social_connection", "hobby_time"
        ]
    }
    
    keyboard = []
    
    # Добавляем привычки по категориям
    for category, habits in habit_categories.items():
        # Добавляем заголовок категории
        keyboard.append([InlineKeyboardButton(category, callback_data="habit_category_header")])
        
        # Добавляем привычки категории
        for habit in habits:
            habit_name = habit.replace("_", " ").title()
            keyboard.append([InlineKeyboardButton(
                f"✅ {habit_name}", 
                callback_data=f"habit_complete:{habit}"
            )])
        
        # Добавляем пустую строку между категориями
        keyboard.append([])
    
    # Добавляем кнопки управления
    keyboard.append([
        InlineKeyboardButton("➕ Добавить свою", callback_data="add_custom_habit"),
        InlineKeyboardButton("📊 Статистика", callback_data="habits_stats")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
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