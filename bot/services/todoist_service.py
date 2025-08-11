"""
Сервис для интеграции с Todoist API
"""

import aiohttp
import logging
import yaml
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MemoryTask:
    """Модель задачи в памяти"""
    content: str
    created_at: str
    due_date: Optional[str] = None
    priority: Optional[int] = None
    project: Optional[str] = None
    labels: Optional[List[str]] = None
    description: Optional[str] = None
    todoist_id: Optional[str] = None
    completed_at: Optional[str] = None
    to_delete: Optional[bool] = None
    deleted_at: Optional[str] = None
    deleted_from: Optional[str] = None


@dataclass
class TodoistTask:
    """Модель задачи Todoist"""
    id: str
    content: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    parent_id: Optional[str] = None
    order: int = 0
    labels: List[str] = None
    priority: int = 1
    due: Optional[Dict] = None
    url: str = ""
    comment_count: int = 0
    created_at: str = ""
    created_by: str = ""
    assignee: Optional[str] = None
    assigner: Optional[str] = None
    responsible_uid: Optional[str] = None
    sync_id: Optional[str] = None
    completed_at: Optional[str] = None
    added_at: str = ""


class TodoistService:
    """Сервис для работы с Todoist API"""
    
    def __init__(self, config):
        self.api_token = config.todoist_api_token
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.memory_path = Path("memory/tasks")
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Выполнить запрос к Todoist API"""
        if not self.api_token:
            raise ValueError("Todoist API токен не настроен")
        
        url = f"{self.base_url}{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Todoist API ошибка: {response.status} - {error_text}")
                    raise Exception(f"Todoist API ошибка: {response.status}")
    
    async def get_today_tasks(self) -> List[TodoistTask]:
        """Получить задачи на сегодня"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            endpoint = f"/tasks?filter=due:{today}"
            
            tasks_data = await self._make_request("GET", endpoint)
            
            tasks = []
            for task_data in tasks_data:
                task = TodoistTask(
                    id=task_data.get("id"),
                    content=task_data.get("content", ""),
                    description=task_data.get("description"),
                    project_id=task_data.get("project_id"),
                    section_id=task_data.get("section_id"),
                    parent_id=task_data.get("parent_id"),
                    order=task_data.get("order", 0),
                    labels=task_data.get("labels", []),
                    priority=task_data.get("priority", 1),
                    due=task_data.get("due"),
                    url=task_data.get("url", ""),
                    comment_count=task_data.get("comment_count", 0),
                    created_at=task_data.get("created_at", ""),
                    created_by=task_data.get("created_by", ""),
                    assignee=task_data.get("assignee"),
                    assigner=task_data.get("assigner"),
                    responsible_uid=task_data.get("responsible_uid"),
                    sync_id=task_data.get("sync_id"),
                    completed_at=task_data.get("completed_at"),
                    added_at=task_data.get("added_at", "")
                )
                tasks.append(task)
            
            logger.info(f"Получено {len(tasks)} задач на сегодня")
            return tasks
            
        except Exception as e:
            logger.error(f"Ошибка при получении задач на сегодня: {e}")
            return []
    
    async def get_upcoming_tasks(self, days: int = 7) -> List[TodoistTask]:
        """Получить предстоящие задачи"""
        try:
            endpoint = f"/tasks?filter=due:{days} days"
            
            tasks_data = await self._make_request("GET", endpoint)
            
            tasks = []
            for task_data in tasks_data:
                task = TodoistTask(
                    id=task_data.get("id"),
                    content=task_data.get("content", ""),
                    description=task_data.get("description"),
                    project_id=task_data.get("project_id"),
                    section_id=task_data.get("section_id"),
                    parent_id=task_data.get("parent_id"),
                    order=task_data.get("order", 0),
                    labels=task_data.get("labels", []),
                    priority=task_data.get("priority", 1),
                    due=task_data.get("due"),
                    url=task_data.get("url", ""),
                    comment_count=task_data.get("comment_count", 0),
                    created_at=task_data.get("created_at", ""),
                    created_by=task_data.get("created_by", ""),
                    assignee=task_data.get("assignee"),
                    assigner=task_data.get("assigner"),
                    responsible_uid=task_data.get("responsible_uid"),
                    sync_id=task_data.get("sync_id"),
                    completed_at=task_data.get("completed_at"),
                    added_at=task_data.get("added_at", "")
                )
                tasks.append(task)
            
            logger.info(f"Получено {len(tasks)} предстоящих задач")
            return tasks
            
        except Exception as e:
            logger.error(f"Ошибка при получении предстоящих задач: {e}")
            return []
    
    async def create_task(self, content: str, **kwargs) -> TodoistTask:
        """Создать новую задачу"""
        try:
            task_data = {
                "content": content,
                **kwargs
            }
            
            task_data = await self._make_request("POST", "/tasks", task_data)
            
            task = TodoistTask(
                id=task_data.get("id"),
                content=task_data.get("content", ""),
                description=task_data.get("description"),
                project_id=task_data.get("project_id"),
                section_id=task_data.get("section_id"),
                parent_id=task_data.get("parent_id"),
                order=task_data.get("order", 0),
                labels=task_data.get("labels", []),
                priority=task_data.get("priority", 1),
                due=task_data.get("due"),
                url=task_data.get("url", ""),
                comment_count=task_data.get("comment_count", 0),
                created_at=task_data.get("created_at", ""),
                created_by=task_data.get("created_by", ""),
                assignee=task_data.get("assignee"),
                assigner=task_data.get("assigner"),
                responsible_uid=task_data.get("responsible_uid"),
                sync_id=task_data.get("sync_id"),
                completed_at=task_data.get("completed_at"),
                added_at=task_data.get("added_at", "")
            )
            
            logger.info(f"Создана задача в Todoist: {content}")
            return task
            
        except Exception as e:
            logger.error(f"Ошибка при создании задачи: {e}")
            raise
    
    async def complete_task(self, task_id: str) -> bool:
        """Завершить задачу"""
        try:
            endpoint = f"/tasks/{task_id}/close"
            await self._make_request("POST", endpoint)
            
            logger.info(f"Задача {task_id} завершена в Todoist")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при завершении задачи: {e}")
            return False
    
    async def update_task(self, task_id: str, **kwargs) -> TodoistTask:
        """Обновить задачу"""
        try:
            endpoint = f"/tasks/{task_id}"
            task_data = await self._make_request("POST", endpoint, kwargs)
            
            task = TodoistTask(
                id=task_data.get("id"),
                content=task_data.get("content", ""),
                description=task_data.get("description"),
                project_id=task_data.get("project_id"),
                section_id=task_data.get("section_id"),
                parent_id=task_data.get("parent_id"),
                order=task_data.get("order", 0),
                labels=task_data.get("labels", []),
                priority=task_data.get("priority", 1),
                due=task_data.get("due"),
                url=task_data.get("url", ""),
                comment_count=task_data.get("comment_count", 0),
                created_at=task_data.get("created_at", ""),
                created_by=task_data.get("created_by", ""),
                assignee=task_data.get("assignee"),
                assigner=task_data.get("assigner"),
                responsible_uid=task_data.get("responsible_uid"),
                sync_id=task_data.get("sync_id"),
                completed_at=task_data.get("completed_at"),
                added_at=task_data.get("added_at", "")
            )
            
            logger.info(f"Задача {task_id} обновлена в Todoist")
            return task
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении задачи: {e}")
            raise
    
    async def delete_task(self, task_id: str) -> bool:
        """Удалить задачу"""
        try:
            endpoint = f"/tasks/{task_id}"
            await self._make_request("DELETE", endpoint)
            
            logger.info(f"Задача {task_id} удалена из Todoist")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при удалении задачи: {e}")
            return False
    
    async def get_projects(self) -> List[Dict]:
        """Получить список проектов"""
        try:
            projects_data = await self._make_request("GET", "/projects")
            logger.info(f"Получено {len(projects_data)} проектов")
            return projects_data
            
        except Exception as e:
            logger.error(f"Ошибка при получении проектов: {e}")
            return []
    
    async def get_labels(self) -> List[Dict]:
        """Получить список меток"""
        try:
            labels_data = await self._make_request("GET", "/labels")
            logger.info(f"Получено {len(labels_data)} меток")
            return labels_data
            
        except Exception as e:
            logger.error(f"Ошибка при получении меток: {e}")
            return []
    
    def _ensure_memory_directory(self) -> None:
        """Убедиться, что директория памяти существует"""
        self.memory_path.mkdir(parents=True, exist_ok=True)
    
    def _load_memory_tasks(self) -> Dict:
        """Загрузить задачи из памяти"""
        todoist_file = self.memory_path / "todoist.yml"
        
        if todoist_file.exists():
            try:
                with open(todoist_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    return content or {"tasks": []}
            except Exception as e:
                logger.error(f"Ошибка загрузки файла памяти: {e}")
        
        return {"tasks": []}
    
    def _save_memory_tasks(self, content: Dict) -> None:
        """Сохранить задачи в память"""
        self._ensure_memory_directory()
        todoist_file = self.memory_path / "todoist.yml"
        
        try:
            with open(todoist_file, 'w', encoding='utf-8') as f:
                yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Задачи сохранены в {todoist_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения файла памяти: {e}")
    
    async def export_to_todoist(self) -> None:
        """Экспорт задач из памяти в Todoist"""
        try:
            # Получить проекты для создания карты
            projects = await self.get_projects()
            project_map = {project['name']: project['id'] for project in projects}
            
            # Загрузить задачи из памяти
            memory_content = self._load_memory_tasks()
            tasks = memory_content.get("tasks", [])
            
            updated_count = 0
            deleted_count = 0
            
            for task in tasks:
                try:
                    # Обработать удаление
                    if task.get('to_delete') and task.get('todoist_id'):
                        await self.delete_task(task['todoist_id'])
                        task['deleted_at'] = datetime.now().isoformat()
                        task['deleted_from'] = 'memory'
                        deleted_count += 1
                        logger.info(f"Удалена задача: {task['content']}")
                        continue
                    
                    # Подготовить данные для обновления/создания
                    update_data = {
                        "content": task['content'],
                        "priority": task.get('priority', 1)
                    }
                    
                    if task.get('description'):
                        update_data['description'] = task['description']
                    
                    if task.get('due_date'):
                        update_data['due_date'] = task['due_date']
                    
                    if task.get('labels'):
                        update_data['labels'] = task['labels']
                    
                    if task.get('project'):
                        project_id = project_map.get(task['project'])
                        if project_id:
                            update_data['project_id'] = project_id
                    
                    # Создать или обновить задачу
                    if task.get('todoist_id'):
                        await self.update_task(task['todoist_id'], **update_data)
                        logger.info(f"Обновлена задача: {task['content']}")
                    else:
                        new_task = await self.create_task(task['content'], **update_data)
                        task['todoist_id'] = new_task.id
                        logger.info(f"Создана задача: {task['content']}")
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки задачи {task.get('content', 'Unknown')}: {e}")
            
            # Сохранить обновленные данные
            memory_content['last_synced'] = datetime.now().isoformat()
            self._save_memory_tasks(memory_content)
            
            logger.info(f"✅ Экспорт завершен: {updated_count} обновлено, {deleted_count} удалено")
            
        except Exception as e:
            logger.error(f"Ошибка экспорта в Todoist: {e}")
    
    async def import_from_todoist(self) -> None:
        """Импорт задач из Todoist в память"""
        try:
            # Получить активные задачи из Todoist
            all_tasks = await self._make_request("GET", "/tasks")
            projects = await self.get_projects()
            project_map = {project['id']: project['name'] for project in projects}
            
            # Загрузить существующий контент
            memory_content = self._load_memory_tasks()
            existing_tasks = memory_content.get("tasks", [])
            
            # Создать множество текущих Todoist ID
            todoist_ids = {task['id'] for task in all_tasks}
            
            # Проверить удаленные/завершенные задачи
            for task in existing_tasks:
                if task.get('todoist_id') and task['todoist_id'] not in todoist_ids:
                    if not task.get('completed_at'):
                        task['completed_at'] = datetime.now().isoformat()
            
            # Удалить помеченные на удаление задачи
            existing_tasks = [task for task in existing_tasks if not task.get('deleted_at')]
            
            # Конвертировать активные Todoist задачи в формат памяти
            memory_tasks = []
            for task in all_tasks:
                memory_task = {
                    'content': task['content'],
                    'created_at': task['created_at'],
                    'todoist_id': task['id'],
                    'priority': task.get('priority', 1),
                    'project': project_map.get(task.get('project_id')),
                    'labels': task.get('labels', []),
                    'description': task.get('description'),
                    'due_date': task.get('due', {}).get('date') if task.get('due') else None,
                    'completed_at': datetime.now().isoformat() if task.get('is_completed') else None
                }
                memory_tasks.append(memory_task)
            
            # Объединить с существующими завершенными задачами
            completed_tasks = [task for task in existing_tasks if task.get('completed_at')]
            all_tasks = memory_tasks + completed_tasks
            
            # Сохранить в файл памяти
            memory_content = {
                'last_synced': datetime.now().isoformat(),
                'tasks': all_tasks
            }
            
            self._save_memory_tasks(memory_content)
            
            active_count = len([t for t in all_tasks if not t.get('completed_at')])
            completed_count = len(all_tasks) - active_count
            
            logger.info(f"✅ Импорт завершен: {len(all_tasks)} задач ({active_count} активных, {completed_count} завершенных)")
            
        except Exception as e:
            logger.error(f"Ошибка импорта из Todoist: {e}")


async def main():
    """Основная функция для тестирования"""
    import os
    from dotenv import load_dotenv
    
    # Загрузить переменные окружения
    load_dotenv()
    
    # Создать простую конфигурацию только для Todoist
    class TodoistConfig:
        def __init__(self):
            self.todoist_api_token = os.getenv("TODOIST_API_TOKEN")
    
    config = TodoistConfig()
    todoist_service = TodoistService(config)
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "import":
            await todoist_service.import_from_todoist()
        elif command == "export":
            await todoist_service.export_to_todoist()
        else:
            print("Использование: python -m bot.services.todoist_service [import|export]")
    else:
        print("Получение задач на сегодня...")
        tasks = await todoist_service.get_today_tasks()
        
        if tasks:
            print(f"\n📋 Найдено {len(tasks)} задач на сегодня:\n")
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task.content}")
                if task.description:
                    print(f"   📝 {task.description}")
                if task.due:
                    print(f"   📅 {task.due}")
                print()
        else:
            print("Задачи на сегодня не найдены")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 