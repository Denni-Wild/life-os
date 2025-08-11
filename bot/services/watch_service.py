"""
Сервис для мониторинга времени и изменений в системе
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class WatchService:
    """Сервис для мониторинга времени и изменений"""
    
    def __init__(self, memory_path: str = "memory"):
        self.memory_path = Path(memory_path)
        self.last_check = datetime.now()
        self.file_timestamps = {}
    
    def get_current_time_info(self) -> Dict[str, str]:
        """Получить текущую информацию о времени"""
        now = datetime.now()
        
        days = [
            "Воскресенье", "Понедельник", "Вторник", "Среда",
            "Четверг", "Пятница", "Суббота"
        ]
        
        return {
            "day": days[now.weekday()],
            "date": now.strftime("%d.%m.%Y"),
            "time": now.strftime("%H:%M:%S"),
            "week": f"Неделя {now.isocalendar()[1]}",
            "month": now.strftime("%B"),
            "year": str(now.year),
            "timestamp": now.isoformat()
        }
    
    def format_time_info(self) -> str:
        """Форматировать информацию о времени для отображения"""
        info = self.get_current_time_info()
        
        return f"""
🕐 *Текущее время:*
📅 День: {info['day']}
📆 Дата: {info['date']}
⏰ Время: {info['time']}
📊 Неделя: {info['week']}
🗓️ Месяц: {info['month']} {info['year']}
        """.strip()
    
    def get_file_timestamp(self, file_path: Path) -> float:
        """Получить временную метку файла"""
        try:
            return file_path.stat().st_mtime
        except (OSError, FileNotFoundError):
            return 0
    
    def scan_memory_files(self) -> Dict[str, float]:
        """Сканировать файлы в памяти и получить их временные метки"""
        timestamps = {}
        
        if not self.memory_path.exists():
            logger.warning(f"Путь к памяти не существует: {self.memory_path}")
            return timestamps
        
        # Сканировать все файлы в памяти
        for file_path in self.memory_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = str(file_path.relative_to(self.memory_path))
                timestamps[relative_path] = self.get_file_timestamp(file_path)
        
        return timestamps
    
    def get_changed_files(self) -> List[str]:
        """Получить список измененных файлов с последней проверки"""
        current_timestamps = self.scan_memory_files()
        changed_files = []
        
        for file_path, timestamp in current_timestamps.items():
            if file_path not in self.file_timestamps:
                # Новый файл
                changed_files.append(f"➕ {file_path}")
            elif self.file_timestamps[file_path] != timestamp:
                # Измененный файл
                changed_files.append(f"✏️ {file_path}")
        
        # Проверить удаленные файлы
        for file_path in self.file_timestamps:
            if file_path not in current_timestamps:
                changed_files.append(f"🗑️ {file_path}")
        
        # Обновить временные метки
        self.file_timestamps = current_timestamps
        self.last_check = datetime.now()
        
        return changed_files
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Получить статистику файлов в памяти"""
        if not self.memory_path.exists():
            return {"files": 0, "directories": 0, "total_size": 0}
        
        file_count = 0
        dir_count = 0
        total_size = 0
        
        for item in self.memory_path.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                file_count += 1
                try:
                    total_size += item.stat().st_size
                except OSError:
                    pass
            elif item.is_dir() and not item.name.startswith('.'):
                dir_count += 1
        
        return {
            "files": file_count,
            "directories": dir_count,
            "total_size": total_size
        }
    
    def format_memory_stats(self) -> str:
        """Форматировать статистику памяти для отображения"""
        stats = self.get_memory_stats()
        
        # Конвертировать размер в читаемый формат
        size_mb = stats["total_size"] / (1024 * 1024)
        
        return f"""
📊 *Статистика памяти:*
📁 Файлов: {stats['files']}
📂 Папок: {stats['directories']}
💾 Размер: {size_mb:.2f} МБ
🕐 Последняя проверка: {self.last_check.strftime('%H:%M:%S')}
        """.strip()
    
    def get_system_status(self) -> str:
        """Получить полный статус системы"""
        time_info = self.format_time_info()
        memory_stats = self.format_memory_stats()
        changed_files = self.get_changed_files()
        
        status = f"{time_info}\n\n{memory_stats}"
        
        if changed_files:
            status += "\n\n📝 *Изменения с последней проверки:*\n"
            for file_change in changed_files[:10]:  # Показать только первые 10
                status += f"• {file_change}\n"
            
            if len(changed_files) > 10:
                status += f"• ... и еще {len(changed_files) - 10} изменений\n"
        
        return status
    
    async def monitor_changes(self, interval: int = 60) -> None:
        """Мониторинг изменений в реальном времени"""
        logger.info(f"Запуск мониторинга изменений с интервалом {interval} секунд")
        
        while True:
            try:
                changed_files = self.get_changed_files()
                
                if changed_files:
                    logger.info(f"Обнаружены изменения: {len(changed_files)} файлов")
                    for change in changed_files:
                        logger.info(f"  {change}")
                
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Мониторинг остановлен")
                break
            except Exception as e:
                logger.error(f"Ошибка мониторинга: {e}")
                await asyncio.sleep(interval)


async def main():
    """Основная функция для тестирования"""
    watch_service = WatchService()
    
    print("🕐 Информация о времени:")
    print(watch_service.format_time_info())
    
    print("\n📊 Статистика памяти:")
    print(watch_service.format_memory_stats())
    
    print("\n📝 Изменения файлов:")
    changed_files = watch_service.get_changed_files()
    if changed_files:
        for change in changed_files:
            print(f"  {change}")
    else:
        print("  Изменений не обнаружено")
    
    print("\n🔄 Полный статус системы:")
    print(watch_service.get_system_status())


if __name__ == "__main__":
    asyncio.run(main()) 