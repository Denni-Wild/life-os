#!/usr/bin/env python3
"""
Скрипт запуска Life OS Telegram Bot
"""

import asyncio
import sys
import os
import signal
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from bot.main import main

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print(f"\n🛑 Получен сигнал {signum}, завершение работы...")
    sys.exit(0)

if __name__ == "__main__":
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🤖 Запуск Life OS Telegram Bot...")
        print("Используйте Ctrl+C для остановки")
        
        # Запускаем бота
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1) 