from datetime import timedelta
from pydantic.v1 import BaseSettings
import os

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "db")  # По умолчанию 'db' для Docker
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "povuzam")
    DB_DRIVER: str = os.getenv("DB_DRIVER", "postgresql+psycopg2")  # Синхронный драйвер
    # DB_DRIVER: str = 'postgresql+asyncpg'  # Асинхронный драйвер (если нужен позже)

    DATABASE_URL: str = os.getenv("DATABASE_URL")  # Добавляем возможность использовать полную строку

    @property
    def db_url(self) -> str:
        # Если DATABASE_URL задан, используем его, иначе собираем из компонентов
        return self.DATABASE_URL or f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()  # Создаем экземпляр настроек