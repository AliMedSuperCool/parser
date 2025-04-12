from dataclasses import dataclass

from exception import TaskNotFound
from repository import TaskCache, TaskRepository
from shema import TaskShema, TaskCreateShema


@dataclass
class TaskService:
    task_repository: TaskRepository
    task_cache: TaskCache

    def get_tasks(self, user_id: int) -> list[TaskShema]:
        if tasks := self.task_cache.get_task():  # достаем из редис
            return tasks

        tasks = self.task_repository.get_tasks(user_id=user_id)  # достаем из бд
        tasks_schema = [TaskShema.model_validate(task) for task in tasks]
        self.task_cache.set_task(tasks_schema)  # кладем в редис
        return tasks_schema

    def create_task(self, task: TaskCreateShema, user_id: int) -> TaskShema:
        task_id = self.task_repository.create_task(task, user_id)
        task = self.task_repository.get_task(task_id)
        return TaskShema.model_validate(task)

    def update_task_name(self, task_id: int, name: str, user_id: int) -> TaskShema:
        task = self.task_repository.get_user_task(user_id=user_id, task_id=task_id)
        if task is None:
            raise TaskNotFound

        task = self.task_repository.update_task_name(task_id=task_id, name=name)
        return TaskShema.model_validate(task)

    def delete_task(self, task_id: int, user_id: int) -> None:
        task = self.task_repository.get_user_task(user_id=user_id, task_id=task_id)
        if task is None:
            raise TaskNotFound
        self.task_repository.delete_task(task_id=task_id)
