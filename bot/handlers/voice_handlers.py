"""
Обработчики для голосовых сообщений
"""

import logging
from typing import Dict, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..services.voice_service import VoiceService

logger = logging.getLogger(__name__)

# Глобальный словарь для хранения состояния пользователей
user_states: Dict[int, Dict] = {}


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений"""
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Отправляем сообщение о начале обработки
        processing_msg = await update.message.reply_text(
            "🎤 Обрабатываю голосовое сообщение..."
        )
        
        # Инициализируем сервис распознавания речи
        voice_service = VoiceService()
        
        # Обрабатываем голосовое сообщение
        success, result = await voice_service.process_voice_message(update, context)
        
        if not success:
            await processing_msg.edit_text(f"❌ {result}")
            return
        
        # Сохраняем распознанный текст в состоянии пользователя
        if chat_id not in user_states:
            user_states[chat_id] = {}
        
        user_states[chat_id]['recognized_text'] = result
        user_states[chat_id]['voice_message_id'] = update.message.message_id
        
        # Создаем клавиатуру для подтверждения
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data="voice_confirm"),
                InlineKeyboardButton("❌ Отменить", callback_data="voice_cancel")
            ],
            [
                InlineKeyboardButton("✏️ Редактировать", callback_data="voice_edit")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем результат с кнопками подтверждения
        await processing_msg.edit_text(
            f"🎤 **Распознанный текст:**\n\n"
            f"_{result}_\n\n"
            f"Подтвердите или отредактируйте текст:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"Голосовое сообщение обработано для пользователя {user_id}: {result}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке голосового сообщения: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке голосового сообщения")


async def voice_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback для голосовых сообщений"""
    try:
        query = update.callback_query
        await query.answer()
        
        chat_id = update.effective_chat.id
        data = query.data
        
        if chat_id not in user_states:
            await query.edit_message_text("❌ Состояние пользователя не найдено")
            return
        
        user_state = user_states[chat_id]
        recognized_text = user_state.get('recognized_text')
        
        if data == "voice_confirm":
            # Подтверждаем текст и обрабатываем как ответ на предыдущую команду
            await process_confirmed_text(update, context, recognized_text)
            await query.edit_message_text("✅ Текст подтвержден и обработан")
            
        elif data == "voice_cancel":
            # Отменяем обработку
            await query.edit_message_text("❌ Обработка отменена")
            
        elif data == "voice_edit":
            # Запрашиваем редактирование текста
            await query.edit_message_text(
                f"✏️ **Текущий текст:**\n\n"
                f"_{recognized_text}_\n\n"
                f"Отправьте исправленный текст:",
                parse_mode='Markdown'
            )
            # Устанавливаем состояние ожидания редактирования
            user_state['waiting_for_edit'] = True
            
        # Очищаем состояние
        if data in ["voice_confirm", "voice_cancel"]:
            user_states.pop(chat_id, None)
            
    except Exception as e:
        logger.error(f"Ошибка при обработке voice callback: {e}")
        await query.edit_message_text("❌ Произошла ошибка при обработке запроса")


async def process_confirmed_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает подтвержденный текст как ответ на предыдущую команду"""
    try:
        chat_id = update.effective_chat.id
        
        # Здесь можно добавить логику для определения контекста
        # и обработки текста в зависимости от предыдущей команды
        
        # Пока просто сохраняем как захваченную задачу/идею
        from ..services.memory_service import MemoryService
        memory_service = MemoryService()
        
        # Определяем тип контента по ключевым словам
        if any(word in text.lower() for word in ['задача', 'сделать', 'нужно', 'должен']):
            await memory_service.save_task(text)
            await update.effective_chat.send_message(f"📝 Задача захвачена: {text}")
        else:
            await memory_service.save_idea(text)
            await update.effective_chat.send_message(f"💡 Идея захвачена: {text}")
            
        logger.info(f"Подтвержденный текст обработан: {text}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке подтвержденного текста: {e}")
        await update.effective_chat.send_message("❌ Ошибка при обработке текста")


async def text_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для редактирования распознанного текста"""
    try:
        chat_id = update.effective_chat.id
        
        if chat_id not in user_states:
            return
        
        user_state = user_states[chat_id]
        
        if not user_state.get('waiting_for_edit'):
            return
        
        # Получаем отредактированный текст
        edited_text = update.message.text
        
        # Обновляем текст в состоянии
        user_state['recognized_text'] = edited_text
        user_state['waiting_for_edit'] = False
        
        # Создаем клавиатуру для подтверждения
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data="voice_confirm"),
                InlineKeyboardButton("❌ Отменить", callback_data="voice_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем обновленный результат
        await update.message.reply_text(
            f"✏️ **Отредактированный текст:**\n\n"
            f"_{edited_text}_\n\n"
            f"Подтвердите текст:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"Текст отредактирован: {edited_text}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке редактирования текста: {e}")
        await update.message.reply_text("❌ Ошибка при обработке редактирования") 