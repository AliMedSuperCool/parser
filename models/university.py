from typing import Optional, List
from sqlalchemy import ForeignKey, Text, Float, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# from models.dormitory import Dormitory


# Определение модели с использованием типизированных полей
class University(Base):
    __tablename__ = 'universities'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    long_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    short_name: Mapped[str] = mapped_column(nullable=False)
    geolocation: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_goverment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rating: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phone_admission: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    phone_general: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    email_general: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    email_admission: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # dormitory: Mapped[Optional["Dormitory"]] = relationship(
    #     "Dormitory",
    #     uselist=False,
    #     back_populates="University",
    #     primaryjoin="University.long_name == Dormitory.vuz_long_name"
    # )

    # dormitory: Mapped["Dormitory"] = relationship(
    #     "Dormitory", uselist=False, back_populates="university"
    # )

# class Tasks(Base):
#     __tablename__ = 'VUZ'
#
#     id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
#     name: Mapped[str]
#     pomodoro_count: Mapped[int]
#     category_id: Mapped[int] = mapped_column(nullable=False)
#     user_id: Mapped[int] = mapped_column(ForeignKey("UserProfile.id"), nullable=False)
#
#
# class Categories(Base):
#     __tablename__ = 'Categories'
#
#     id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
#     type: Mapped[Optional[str]]  # либо так mapped_column(nullable=True)
#     name: Mapped[str]
