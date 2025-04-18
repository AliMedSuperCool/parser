from fastapi import Depends, Request, Security, security, HTTPException
from sqlalchemy.orm import Session

from cache import get_redis_connection
from database import get_db_session
from repository import UniversityRepository, UniversityCache
from service import UniversityService
from settings import Settings


def get_university_cache_repository() -> UniversityCache:
    redis_connection = get_redis_connection()
    return UniversityCache(redis_connection)


def get_university_repository(db_session: Session = Depends(get_db_session)) -> UniversityRepository:
    return UniversityRepository(db_session=db_session)


def get_university_service(
        university_repository: UniversityRepository = Depends(get_university_repository),
        university_cache: UniversityCache = Depends(get_university_cache_repository),
) -> UniversityService:
    return UniversityService(university_repository=university_repository, university_cache=university_cache)
