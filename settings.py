from datetime import timedelta
from pydantic.v1 import BaseSettings
import os

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "db")  # По умолчанию 'db' для Docker
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str =  "povuzam"
    DB_DRIVER: str = "postgresql+psycopg2"  # Синхронный драйвер
    # DB_DRIVER: str = 'postgresql+asyncpg'  # Асинхронный драйвер (если нужен позже)
    DATABASE_URL: str = os.getenv("DATABASE_URL")  # Добавляем возможность использовать полную строку

    CACHE_HOST: str = 'localhost'
    CACHE_PORT: int = 6379
    CACHE_DB: int = 0


    @property
    def db_url(self) -> str:

        return self.DATABASE_URL or f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()  # Создаем экземпляр настроек