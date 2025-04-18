from typing import List, Optional

from sqlalchemy import and_, or_, Text

from models import Form, Program
from shema import UniversityFilterParams


def apply_program_filters(stmt, filters: UniversityFilterParams, conditions: Optional[list] = None) -> List:
    if conditions is None:
        conditions = []

    stmt = stmt.join(Program.forms)

    if filters.direction:
        conditions.append(Program.direction.ilike(f"%{filters.direction}%"))

    if filters.education_form:
        conditions.append(Form.education_form2 == filters.education_form)

    if filters.is_free is True:
        conditions.append(
            Form.free_places.isnot(None)
        )

    elif filters.is_free is False:
        conditions.append(Form.price.isnot(None))

    if filters.user_score is not None:
        conditions.append(Form.score <= filters.user_score + 7)

    if filters.max_price is not None:
        conditions.append(Form.price <= abs(filters.max_price))


    if filters.user_exams:
        user_exams_upper = [e.strip().upper() for e in filters.user_exams]

        # Грубая SQL-фильтрация: ищем хотя бы одно вхождение экзамена
        exam_conditions = [
            Program.exams.cast(Text).ilike(f'%"{exam}"%')  # ищем по строке
            for exam in user_exams_upper
        ]

        conditions.extend(exam_conditions)

    # return conditions
    return stmt.where(and_(*conditions))
