# from dataclasses import dataclass
# from typing import List, Optional
# from sqlalchemy import select, delete, update
# from sqlalchemy.orm import Session
# from models import Tasks as DBTasks
# from models import Categories as DBCategories
# from shema import UserCreateSchema, TaskCreateShema
# from shema.university import TaskShema
#
#
# @dataclass
# class TaskRepository:
#     db_session: Session
#
#     def get_user_task(self, task_id, user_id: int) -> DBTasks:
#         query = select(DBTasks).where(DBTasks.user_id == user_id, DBTasks.id == task_id)
#         with self.db_session() as session:
#             task = session.execute(query).scalar_one_or_none()
#             return task
#
#     def get_tasks(self, user_id: int) -> List[DBTasks]:
#         query = select(DBTasks).where(DBTasks.user_id == user_id)
#         with self.db_session() as session:
#             tasks = session.execute(query).scalars().all()
#         return tasks
#
#     def get_task(self, task_id: int) -> Optional[DBTasks]:
#         query = select(DBTasks).where(DBTasks.id == task_id)
#         with self.db_session() as session:
#             task = session.execute(query).scalar_one_or_none()
#         return task
#
#     def create_task(self, task: TaskCreateShema, user_id: int) -> int:
#         task_model = DBTasks(name=task.name,
#                              pomodoro_count=task.pomodoro_count,
#                              category_id=task.category_id,
#                              user_id=user_id)
#         with self.db_session() as session:
#             session.add(task_model)
#             session.commit()
#             return task_model.id
#
#     def update_task_name(self, task_id: int, name: str, ) -> DBTasks:
#         query = update(DBTasks).where(DBTasks.id == task_id).values(name=name).returning(
#             DBTasks.id)
#         with self.db_session() as session:
#             task_id = session.execute(query).scalar_one_or_none()
#             session.flush()
#             session.commit()
#             return self.get_task(task_id)
#
#     def delete_task(self, task_id: int, ) -> None:
#         query = delete(DBTasks).where(DBTasks.id == task_id)
#         with self.db_session() as session:
#             session.execute(query)
#             session.commit()
#
#     def get_task_by_category_name(self, category_name: str) -> List[DBTasks]:
#         query = select(DBTasks).join(DBCategories, DBTasks.category_id == DBCategories.id).where(
#             DBCategories.name == category_name)
#         with self.db_session() as session:
#             tasks: List[DBTasks] = session.execute(query).scalars().all()
#             return tasks
