from fastapi import Depends, Request, Security, security, HTTPException
from sqlalchemy.orm import Session
from database import get_db_session
from repository import TaskRepository, TaskCache, UserRepository
from service import TaskService, UserService, AuthService
from settings import Settings


def get_tasks_repository(db_session: Session = Depends(get_db_session)) -> TaskRepository:
    return TaskRepository(db_session=db_session)



def get_user_repository(db_session: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db_session=db_session)


def get_tasks_service(
        task_repository: TaskRepository = Depends(get_tasks_repository),
) -> TaskService:
    return TaskService(
        task_repository=task_repository,
    )


def get_users_service(
        user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository=user_repository)

