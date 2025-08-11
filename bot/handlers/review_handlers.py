"""
Обработчики для обзоров и оценок
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..services.memory_service import MemoryService

logger = logging.getLogger(__name__)


async def review_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /review - ежедневный обзор"""
    review_message = """
🔍 *Ежедневный обзор*

Давайте проведем быстрый обзор дня:

1. *Что было сделано сегодня?*
2. *Что не удалось сделать?*
3. *Как вы себя чувствуете?*
4. *Что планируете на завтра?*

Отправьте свои ответы, и я помогу их структурировать.

*Или используйте быстрые кнопки ниже:*
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Начать обзор", callback_data="start_review"),
            InlineKeyboardButton("📊 Быстрый чек", callback_data="quick_check")
        ],
        [
            InlineKeyboardButton("😊 Настроение", callback_data="mood_check"),
            InlineKeyboardButton("✅ Привычки", callback_data="habits_check")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        review_message, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    logger.info(f"Пользователь {update.effective_user.id} запросил ежедневный обзор")


async def assess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /assess - оценка жизненных областей"""
    areas = ['Здоровье', 'Карьера', 'Отношения', 'Финансы', 'Личностный рост']
    
    # Создаем кнопки для каждой области
    keyboard = []
    for area in areas:
        row = []
        for score in range(1, 11):  # Шкала 1-10
            row.append(InlineKeyboardButton(
                str(score), 
                callback_data=f"area_score:{area}:{score}"
            ))
            # Разбиваем на ряды по 5 кнопок
            if len(row) == 5:
                keyboard.append(row)
                row = []
        if row:  # Добавляем оставшиеся кнопки
            keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
📈 *Оценка жизненных областей*

Оцените каждую область по шкале от 1 до 10:

*Здоровье* - физическое и психическое состояние
*Карьера* - работа, профессиональный рост
*Отношения* - семья, друзья, социальные связи
*Финансы* - доходы, расходы, финансовые цели
*Личностный рост* - обучение, развитие, хобби

Выберите область и оценку:
    """
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    logger.info(f"Пользователь {update.effective_user.id} запросил оценку жизненных областей")


async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /schedule - расписание на сегодня"""
    try:
        # В будущем здесь будет интеграция с календарем
        # Пока показываем примерное расписание
        
        schedule_message = """
📅 *Расписание на сегодня:*

09:00 - Утренняя рутина
10:00 - Рабочие задачи
12:00 - Обед
13:00 - Продолжение работы
18:00 - Тренировка
20:00 - Ужин
22:00 - Подготовка ко сну

*Свободное время:* 2 часа
*Приоритетные задачи:* 3

*Быстрые действия:*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Задачи", callback_data="show_tasks"),
                InlineKeyboardButton("⏰ Напоминания", callback_data="show_reminders")
            ],
            [
                InlineKeyboardButton("📝 Добавить событие", callback_data="add_event"),
                InlineKeyboardButton("🔄 Синхронизировать", callback_data="sync_calendar")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            schedule_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        logger.info(f"Пользователь {update.effective_user.id} запросил расписание")
        
    except Exception as e:
        logger.error(f"Ошибка при получении расписания: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении расписания") 