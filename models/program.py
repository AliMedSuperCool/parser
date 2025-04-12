from typing import Optional, List, Dict

from sqlalchemy import Text, ForeignKey, Index
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
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), nullable=False)
    # Текстовые поля
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    profile: Mapped[str] = mapped_column(Text, nullable=False)
    program_code: Mapped[str] = mapped_column(Text, nullable=False)

    # vuz_long_name: Mapped[str] = mapped_column(Text, ForeignKey("universities.long_name"), nullable=False)
    faculty: Mapped[str] = mapped_column(Text, nullable=False)

    # Сложные структуры — в формате JSONB
    # exams и scores — списки списков, forms — список словарей
    exams: Mapped[Optional[List[List[str]]]] = mapped_column(JSONB, nullable=True)
    # forms: Mapped[Optional[List[Dict]]] = mapped_column(JSONB, nullable=True)
    forms: Mapped[List["Form"]] = relationship("Form", back_populates="program", cascade="all, delete-orphan")

    university: Mapped["University"] = relationship("University", back_populates="programs")

    __table_args__ = (
        # Index("ix_program_forms_gin", "forms", postgresql_using="gin"),
        Index("ix_program_exams_gin", "exams", postgresql_using="gin"),
        Index("ix_program_direction", "direction"),

    )



class Form(Base):
    """
    Модель формы обучения: очная/заочная, баллы, цена и др.
    """
    __tablename__ = "form"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("program.id", ondelete="CASCADE"), nullable=False)

    education_form2: Mapped[str] = mapped_column(nullable=False)  # Очная / Заочная и т.д.
    score: Mapped[Optional[int]] = mapped_column(nullable=True)  # None, если "Только платное"
    price: Mapped[Optional[int]] = mapped_column(nullable=True)  # None, если "no data"

    olympic: Mapped[Optional[str]] = mapped_column(nullable=True)
    free_places: Mapped[Optional[int]] = mapped_column( nullable=True)
    average_score: Mapped[Optional[int]] = mapped_column(Text, nullable=True)

    program: Mapped["Program"] = relationship("Program", back_populates="forms")

    __table_args__ = (
        Index("ix_form_education_form2", "education_form2"),
        Index("ix_form_score", "score"),
        Index("ix_form_price", "price"),
    )