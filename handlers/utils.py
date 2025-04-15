from typing import List

from sqlalchemy import and_, or_

from models import Form, Program
from shema import UniversityFilterParams


def apply_program_filters(stmt, filters: UniversityFilterParams) -> List:
    conditions = []

    # ✅ Прямой join без aliased(), если alias не нужен
    stmt = stmt.join(Form, Form.program_id == Program.id)

    if filters.direction:
        conditions.append(Program.direction.ilike(f"%{filters.direction}%"))

    if filters.education_form:
        conditions.append(Form.education_form2 == filters.education_form)

    if filters.is_free is True:
        conditions.append(
            Form.score.isnot(None)
        )  # быстрее, чем сравнение с "Только платное"
    elif filters.is_free is False:
        conditions.append(or_(Form.score.is_(None), Form.price.isnot(None)))

    if filters.user_score is not None:
        conditions.append(Form.score <= filters.user_score + 7)

    if filters.max_price is not None:
        conditions.append(Form.price <= abs(filters.max_price))

    return stmt.where(and_(*conditions))


# def build_forms_subquery():
#     forms = func.jsonb_array_elements(Program.forms)
#     return (
#         select(
#             Program.id.label("program_id"),
#             func.jsonb_extract_path_text(forms, "education_form2").label("education_form2"),
#             func.jsonb_extract_path_text(forms, "score").label("score"),
#             func.jsonb_extract_path_text(forms, "price").label("price"),
#         ).subquery("forms_expanded")
#     )
#
#
# def apply_program_filters(stmt, filters: ProgramFilterParams, forms_subquery) -> List:
#     conditions = []
#     base_condition = forms_subquery.c.program_id == Program.id
#
#     def exists_in_forms(*extra_conditions):
#         return exists(
#             select(1).select_from(forms_subquery).where(
#                 and_(base_condition, *extra_conditions)
#             )
#         )
#
#     # Кэшируем часто используемые выражения
#     score_raw = forms_subquery.c.score
#     score_int = case(
#         (score_raw.notin_(["Только платное", "NEW"]), score_raw.cast(Integer)),
#         else_=None
#     )
#
#     price_raw = forms_subquery.c.price
#     price_int = func.coalesce(func.nullif(price_raw, "no data").cast(Integer), 0)
#
#     # direction
#     if filters.direction:
#         conditions.append(Program.direction.ilike(f"%{filters.direction}%"))
#
#     # education_form
#     if filters.education_form:
#         conditions.append(
#             exists_in_forms(forms_subquery.c.education_form2 == filters.education_form)
#         )
#
#     # is_free
#     if filters.is_free is True:
#         conditions.append(
#             exists_in_forms(score_raw != "Только платное")
#         )
#     elif filters.is_free is False:
#         conditions.append(
#             exists_in_forms(
#                 or_(
#                     score_raw == "Только платное",
#                     price_int > 0
#                 )
#             )
#         )
#
#     # user_score
#     if filters.user_score is not None:
#         conditions.append(
#             exists_in_forms(
#                 score_int <= (filters.user_score + 10)
#             )
#         )
#
#     # max_price
#     if filters.max_price is not None:
#         conditions.append(
#             exists_in_forms(
#                 price_raw != "no data",
#                 price_int <= abs(filters.max_price)
#             )
#         )
#
#     return stmt.where(and_(*conditions)) if conditions else stmt
