from typing import Optional, List
from sqlalchemy import ForeignKey, Text, Float, String, ARRAY, TEXT, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# from models.dormitory import Dormitory


# Определение модели с использованием типизированных полей
class University(Base):
    __tablename__ = 'universities'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    long_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    short_name: Mapped[str] = mapped_column(nullable=False)
    geolocation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_goverment: Mapped[bool] = mapped_column(nullable=True)
    rating: Mapped[int] = mapped_column(nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_admission: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    phone_general: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    email_general: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    email_admission: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    army: Mapped[bool] = mapped_column(nullable=True)
    has_dormitory: Mapped[bool] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    dormitory: Mapped["Dormitory"] = relationship("Dormitory", uselist=False, back_populates="university",
                                                  lazy="selectin")
    programs: Mapped[List["Program"]] = relationship("Program", back_populates="university", lazy="selectin")

    __table_args__ = (
        Index("ix_university_form_long_name", "long_name"),
        Index("ix_university_short_name", "short_name"),
        Index("ix_university_is_goverment", "is_goverment"),
        Index("ix_university_army", "army"),
        Index("ix_university_has_dormitory", "has_dormitory"),
    )
