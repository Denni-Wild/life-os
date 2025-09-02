"""
Сервис для обработки голосовых сообщений и распознавания речи
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import speech_recognition as sr
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class VoiceService:
    """Сервис для работы с голосовыми сообщениями"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Настройка для русского языка
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    async def download_voice_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Скачивает голосовое сообщение во временный файл"""
        try:
            voice = update.message.voice
            if not voice:
                return None
                
            # Получаем файл
            file = await context.bot.get_file(voice.file_id)
            
            # Создаем временный файл
            temp_dir = Path(tempfile.gettempdir())
            temp_file = temp_dir / f"voice_{voice.file_id}.ogg"
            
            # Скачиваем файл
            await file.download_to_drive(temp_file)
            
            logger.info(f"Голосовое сообщение скачано: {temp_file}")
            return str(temp_file)
            
        except Exception as e:
            logger.error(f"Ошибка при скачивании голосового файла: {e}")
            return None
    
    async def convert_ogg_to_wav(self, ogg_file: str) -> Optional[str]:
        """Конвертирует OGG файл в WAV для распознавания"""
        try:
            # Загружаем аудио
            audio = AudioSegment.from_ogg(ogg_file)
            
            # Создаем WAV файл
            wav_file = ogg_file.replace('.ogg', '.wav')
            audio.export(wav_file, format='wav')
            
            logger.info(f"Аудио конвертировано в WAV: {wav_file}")
            return wav_file
            
        except Exception as e:
            logger.error(f"Ошибка при конвертации аудио: {e}")
            return None
    
    async def recognize_speech(self, audio_file: str) -> Tuple[bool, str]:
        """Распознает речь в аудио файле"""
        try:
            # Загружаем аудио файл
            with sr.AudioFile(audio_file) as source:
                # Настраиваем распознаватель для шумного аудио
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Получаем аудио данные
                audio = self.recognizer.record(source)
                
                # Распознаем речь (пробуем Google Speech Recognition)
                try:
                    text = self.recognizer.recognize_google(
                        audio, 
                        language='ru-RU',
                        show_all=False
                    )
                    logger.info(f"Речь распознана: {text}")
                    return True, text
                    
                except sr.UnknownValueError:
                    logger.warning("Речь не распознана")
                    return False, "Не удалось распознать речь"
                    
                except sr.RequestError as e:
                    logger.error(f"Ошибка сервиса распознавания: {e}")
                    return False, "Ошибка сервиса распознавания речи"
                    
        except Exception as e:
            logger.error(f"Ошибка при распознавании речи: {e}")
            return False, f"Ошибка обработки аудио: {str(e)}"
    
    async def cleanup_files(self, *files):
        """Удаляет временные файлы"""
        for file_path in files:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Временный файл удален: {file_path}")
            except Exception as e:
                logger.warning(f"Не удалось удалить файл {file_path}: {e}")
    
    async def process_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Tuple[bool, str]:
        """Полный процесс обработки голосового сообщения"""
        ogg_file = None
        wav_file = None
        
        try:
            # Скачиваем голосовое сообщение
            ogg_file = await self.download_voice_file(update, context)
            if not ogg_file:
                return False, "Не удалось скачать голосовое сообщение"
            
            # Конвертируем в WAV
            wav_file = await self.convert_ogg_to_wav(ogg_file)
            if not wav_file:
                return False, "Не удалось конвертировать аудио"
            
            # Распознаем речь
            success, text = await self.recognize_speech(wav_file)
            
            return success, text
            
        finally:
            # Очищаем временные файлы
            await self.cleanup_files(ogg_file, wav_file) 