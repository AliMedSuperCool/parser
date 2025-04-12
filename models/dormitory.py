from sqlalchemy import Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# from models.university import University


class Dormitory(Base):
    """
    Модель для хранения информации об учебном заведении и его общежитиях.
    """
    __tablename__ = "dormitory"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), unique=True, nullable=False)

    # dormitory: Mapped[bool] = mapped_column(nullable=False)
    info: Mapped[str] = mapped_column(Text, nullable=True)
    rating: Mapped[float] = mapped_column(nullable=True)

    university: Mapped["University"] = relationship("University", back_populates="dormitory")

    # __table_args__ = (
    #     Index("ix_dormitory_dormitory", "dormitory"),
    # )

    # id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # vuz_long_name: Mapped[str] = mapped_column(Text, ForeignKey("universities.long_name"), nullable=False, unique=True)
    # # vuz_long_name: Mapped[str] = mapped_column(nullable=False)
    # dormitory: Mapped[bool] = mapped_column(nullable=False)
    # info: Mapped[str] = mapped_column(Text, nullable=True)
    # rating: Mapped[float] = mapped_column(nullable=True)
    # # university:Mapped["University"] = relationship("Dormitory", back_populates="dormitory")
    # university: Mapped["University"] = relationship("University", back_populates="dormitory")


    # university: Mapped["University"] = relationship(
    #     "University",
    #     back_populates="Dormitory",
    #     primaryjoin="Dormitory.vuz_long_name == University.long_name"
    # )
    # university: Mapped["University"] = relationship("University", back_populates="dormitory")
