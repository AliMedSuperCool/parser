from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy import select, delete, update, and_
from sqlalchemy.orm import Session, selectinload

from models import Program, University
from repository.utils_filter import apply_program_filters
from shema.university import UniversityFilterParams


@dataclass
class UniversityRepository:
    db_session: Session

    def filtering(self, filters: UniversityFilterParams):

        with self.db_session() as session:

            stmt = select(Program).options(
                selectinload(Program.university), selectinload(Program.forms)
            )

            stmt = stmt.join(Program.university)

            conditions = []

            if filters.long_name:
                conditions.append(University.long_name.ilike(f"%{filters.long_name}%"))

            if filters.short_name:
                # stmt = stmt.join(Program.university)
                conditions.append(University.short_name.ilike(f"%{filters.short_name}%"))

            if filters.is_goverment is not None:
                conditions.append(University.is_goverment == filters.is_goverment)
            #
            if filters.has_dormitory is not None:
                # Подтягиваем таблицу University, если еще не джойнили
                # stmt = stmt.join(University.dormitory)
                conditions.append(University.has_dormitory == filters.has_dormitory)
            #

            if filters.has_army is not None:
                # stmt = stmt.join(Program.university)
                conditions.append(University.army == filters.has_army)
            #
            if filters.region:
                # stmt = stmt.join(Program.university)
                conditions.append(University.geolocation.ilike(f"%{filters.region}%"))

            if any(
                    param is not None
                    for param in [
                        filters.direction,
                        filters.education_form,
                        filters.is_free,
                        filters.user_score,
                        filters.max_price,
                        filters.user_exams,
                    ]
            ):
                stmt = apply_program_filters(stmt, filters, conditions)

            # 2) Забираем программы из БД
            stmt = stmt.where(and_(*conditions))
            result = session.execute(stmt)

            return result.scalars().all()
