from typing import Optional, List, Dict

from sqlalchemy import Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship


class Program(Base):
    """
    Модель для хранения информации о направлении обучения, профиле, коде программы,
    вузе, факультете, а также вложенных структур (exams, scores, forms).
    """
    __tablename__ = "program"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Текстовые поля
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    profile: Mapped[str] = mapped_column(Text, nullable=False)
    program_code: Mapped[str] = mapped_column(Text, nullable=False)
    vuz_long_name: Mapped[str] = mapped_column(Text, ForeignKey("universities.long_name"), nullable=False)
    faculty: Mapped[str] = mapped_column(Text, nullable=False)

    # Сложные структуры — в формате JSONB
    # exams и scores — списки списков, forms — список словарей
    exams: Mapped[Optional[List[List[str]]]] = mapped_column(JSONB, nullable=True)
    scores: Mapped[Optional[List[List[str]]]] = mapped_column(JSONB, nullable=True)
    forms: Mapped[Optional[List[Dict]]] = mapped_column(JSONB, nullable=True)

    university: Mapped["University"] = relationship("University", back_populates="programs")