"""
Сервис для работы с локальными файлами памяти
"""

import aiofiles
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    """Сервис для работы с локальными файлами памяти"""
    
    def __init__(self, memory_path: str = "memory"):
        self.memory_path = memory_path
        self.tasks_path = os.path.join(memory_path, "gtd")
        self.assessments_path = os.path.join(memory_path, "assessments")
        
        # Создаем необходимые директории
        os.makedirs(self.memory_path, exist_ok=True)
        os.makedirs(self.tasks_path, exist_ok=True)
        os.makedirs(self.assessments_path, exist_ok=True)
    
    async def save_task(self, content: str, priority: int = 3, due_date: Optional[str] = None) -> None:
        """Сохранить задачу в inbox"""
        inbox_path = os.path.join(self.tasks_path, "inbox.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        task_line = f"- [ ] {content} (захвачено: {timestamp})\n"
        
        async with aiofiles.open(inbox_path, 'a', encoding='utf-8') as f:
            await f.write(task_line)
        
        logger.info(f"Задача сохранена в inbox: {content}")
    
    async def save_idea(self, content: str) -> None:
        """Сохранить идею"""
        ideas_path = os.path.join(self.memory_path, "ideas.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        idea_line = f"- {content} (захвачено: {timestamp})\n"
        
        async with aiofiles.open(ideas_path, 'a', encoding='utf-8') as f:
            await f.write(idea_line)
        
        logger.info(f"Идея сохранена: {content}")
    
    async def save_mood(self, score: int, notes: Optional[str] = None) -> None:
        """Сохранить настроение"""
        mood_path = os.path.join(self.memory_path, "mood.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        mood_line = f"- {score}/10 - {timestamp}"
        if notes:
            mood_line += f" - {notes}"
        mood_line += "\n"
        
        async with aiofiles.open(mood_path, 'a', encoding='utf-8') as f:
            await f.write(mood_line)
        
        logger.info(f"Настроение сохранено: {score}/10")
    
    async def save_habit(self, habit: str) -> None:
        """Сохранить привычку"""
        habits_path = os.path.join(self.memory_path, "habits.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        habit_line = f"- {habit} - {timestamp}\n"
        
        async with aiofiles.open(habits_path, 'a', encoding='utf-8') as f:
            await f.write(habit_line)
        
        logger.info(f"Привычка сохранена: {habit}")
    
    async def get_habits_stats(self) -> Dict[str, int]:
        """Получить статистику привычек (количество выполнений каждой привычки)"""
        habits_path = os.path.join(self.memory_path, "habits.md")
        
        if not os.path.exists(habits_path):
            return {}
        
        try:
            async with aiofiles.open(habits_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            habits_count = {}
            lines = content.strip().split('\n')
            
            for line in lines:
                if line.strip() and line.startswith('- ') and ' - ' in line:
                    # Парсим строку: "- habit_name - timestamp"
                    parts = line.strip().split(' - ')
                    if len(parts) >= 2:
                        habit_name = parts[0].replace('- ', '').strip()
                        habits_count[habit_name] = habits_count.get(habit_name, 0) + 1
            
            return habits_count
            
        except Exception as e:
            logger.error(f"Ошибка при чтении статистики привычек: {e}")
            return {}
    
    async def save_life_area_score(self, area: str, score: int, notes: Optional[str] = None) -> None:
        """Сохранить оценку жизненной области (обновляет существующую или добавляет новую)"""
        assessment_path = os.path.join(self.assessments_path, "current.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Читаем существующий файл
        lines = []
        if os.path.exists(assessment_path):
            async with aiofiles.open(assessment_path, 'r', encoding='utf-8') as f:
                lines = (await f.read()).split('\n')
        
        # Ищем существующую оценку для этой области
        area_updated = False
        new_lines = []
        
        for line in lines:
            if line.strip().startswith(f'- {area}:'):
                # Обновляем существующую оценку
                new_line = f"- {area}: {score}/10 ({timestamp})"
                if notes:
                    new_line += f" - {notes}"
                new_lines.append(new_line)
                area_updated = True
            else:
                new_lines.append(line)
        
        # Если область не найдена, добавляем новую
        if not area_updated:
            new_line = f"- {area}: {score}/10 ({timestamp})"
            if notes:
                new_line += f" - {notes}"
            new_lines.append(new_line)
        
        # Записываем обновленный файл
        async with aiofiles.open(assessment_path, 'w', encoding='utf-8') as f:
            await f.write('\n'.join(new_lines))
        
        logger.info(f"Оценка области '{area}' сохранена: {score}/10")
    
    async def get_today_tasks(self) -> List[Dict]:
        """Получить задачи на сегодня"""
        inbox_path = os.path.join(self.tasks_path, "inbox.md")
        
        if not os.path.exists(inbox_path):
            return []
        
        tasks = []
        async with aiofiles.open(inbox_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            
        for line in content.split('\n'):
            if line.strip().startswith('- [ ]'):
                # Извлекаем текст задачи
                task_text = line.replace('- [ ]', '').strip()
                # Убираем timestamp в скобках
                if '(' in task_text:
                    task_text = task_text.split('(')[0].strip()
                
                tasks.append({
                    'content': task_text,
                    'created_at': datetime.now().isoformat(),
                    'completed': False
                })
        
        return tasks
    
    async def get_life_areas_status(self) -> List[Dict]:
        """Получить статус жизненных областей"""
        assessment_path = os.path.join(self.assessments_path, "current.md")
        
        if not os.path.exists(assessment_path):
            return []
        
        areas = {}
        async with aiofiles.open(assessment_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            
        for line in content.split('\n'):
            if line.strip().startswith('- ') and ':' in line:
                # Парсим строку вида "- Область: 8/10 (2024-01-15 14:30)"
                parts = line.replace('- ', '').split(':')
                if len(parts) >= 2:
                    area_name = parts[0].strip()
                    score_part = parts[1].strip()
                    
                    # Извлекаем оценку
                    if '/' in score_part:
                        score = int(score_part.split('/')[0])
                        areas[area_name] = score
        
        # Преобразуем в список
        return [{"name": name, "score": score} for name, score in areas.items()]
    
    async def get_life_area_scores(self) -> Dict[str, int]:
        """Получить текущие оценки жизненных областей в виде словаря"""
        assessment_path = os.path.join(self.assessments_path, "current.md")
        
        if not os.path.exists(assessment_path):
            return {}
        
        areas = {}
        async with aiofiles.open(assessment_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            
        for line in content.split('\n'):
            if line.strip().startswith('- ') and ':' in line:
                # Парсим строку вида "- Область: 8/10 (2024-01-15 14:30)"
                parts = line.replace('- ', '').split(':')
                if len(parts) >= 2:
                    area_name = parts[0].strip()
                    score_part = parts[1].strip()
                    
                    # Извлекаем оценку
                    if '/' in score_part:
                        score = int(score_part.split('/')[0])
                        areas[area_name] = score
        
        return areas
    
    async def complete_task(self, task_id: str) -> None:
        """Отметить задачу как выполненную"""
        # В локальной версии просто удаляем из inbox
        # В реальной реализации можно перемещать в completed.md
        logger.info(f"Задача {task_id} отмечена как выполненная")
    
    async def save_daily_review(self, review_data: Dict) -> None:
        """Сохранить ежедневный обзор"""
        review_path = os.path.join(self.memory_path, "reviews.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        review_text = f"## Обзор {timestamp}\n\n"
        for key, value in review_data.items():
            review_text += f"**{key}:** {value}\n\n"
        review_text += "---\n\n"
        
        async with aiofiles.open(review_path, 'a', encoding='utf-8') as f:
            await f.write(review_text)
        
        logger.info("Ежедневный обзор сохранен")
    
    async def get_recent_mood(self, days: int = 7) -> List[Dict]:
        """Получить настроение за последние дни"""
        mood_path = os.path.join(self.memory_path, "mood.md")
        
        if not os.path.exists(mood_path):
            return []
        
        moods = []
        async with aiofiles.open(mood_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            
        for line in content.split('\n'):
            if line.strip().startswith('- ') and '/10' in line:
                # Парсим строку вида "- 8/10 - 2024-01-15 14:30"
                parts = line.replace('- ', '').split(' - ')
                if len(parts) >= 2:
                    score = int(parts[0].split('/')[0])
                    timestamp = parts[1]
                    
                    moods.append({
                        'score': score,
                        'timestamp': timestamp
                    })
        
        # Возвращаем последние N записей
        return moods[-days:] if moods else []
    
    async def get_habit_streak(self, habit: str, days: int = 7) -> int:
        """Получить серию выполнения привычки"""
        habits_path = os.path.join(self.memory_path, "habits.md")
        
        if not os.path.exists(habits_path):
            return 0
        
        streak = 0
        async with aiofiles.open(habits_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            
        lines = content.split('\n')
        for line in reversed(lines):  # Идем с конца
            if habit.lower() in line.lower():
                streak += 1
            else:
                break
        
        return min(streak, days) 