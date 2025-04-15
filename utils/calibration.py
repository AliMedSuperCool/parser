import time

from models import Program
from shema import UniversityFilterParams

from functools import lru_cache
from typing import Optional


# Кэширование часто используемых значений
@lru_cache(maxsize=None)
def get_weight_config() -> dict:
    return {
        "W_ex": 0.5,
        "W_rat": 0.25,
        "W_dorm": 0.05,
        "W_gov": 0.05,
        "W_price": 0.05,
        "W_fill": 0.025,
        "W_free": 0.075
    }


@lru_cache(maxsize=1024)
def normalize_str(text: Optional[str]) -> str:
    return text.strip().lower() if text else ""

#
# def compute_program_score(program: Program, filters: ProgramFilterParams) -> float:
#     weights = get_weight_config()
#     """
#     Вычисляет рейтинг программы с учетом всех параметров из ProgramFilterParams.
#     Больше очков дается программам, где pass_score ближе к user_score.
#     """
#     # ===== P_ex (экзамен) =====
#     try:
#         pass_score = int(program.forms[0]["score"])
#     except (ValueError, TypeError, KeyError):
#         pass_score = 0
#
#     if filters.user_score and pass_score:
#         # Вычисляем абсолютную разницу между user_score и pass_score
#         score_diff = abs(filters.user_score - pass_score)
#         # Максимальная допустимая разница (например, 50 баллов), чтобы рейтинг не обнулился
#         max_diff = 50
#         if score_diff <= max_diff:
#             # Чем меньше разница, тем выше рейтинг (линейное убывание от 1 до 0)
#             P_ex = 1 - (score_diff / max_diff)
#         else:
#             P_ex = 0  # Если разница больше max_diff, рейтинг 0
#     else:
#         P_ex = 0
#
#     # ===== P_rat (рейтинг вуза) =====
#     uni_rating = program.university.rating or 0
#     P_rat = min(max(uni_rating / 100, 0), 1)
#
#     # ===== P_dorm (общежитие) =====
#     P_dorm = 1 if program.university.dormitory.dormitory else 0
#
#     # ===== P_gov (гос. вуз) =====
#     P_gov = 1 if program.university.is_goverment else 0
#     if filters.is_goverment is not None:
#         P_gov *= 1.5 if (P_gov == (1 if filters.is_goverment else 0)) else 0.5
#
#     # ===== P_price (цена) =====
#     try:
#         price = int(program.forms[0]["price"])
#     except (ValueError, TypeError, KeyError):
#         price = 0
#     if price == 0 or (filters.is_free is True and program.forms[0]["score"] != ["Только платное", "no data"]):
#         P_price = 1
#     else:
#         if filters.max_price is not None:
#             max_price = abs(filters.max_price)
#             if price <= max_price:
#                 P_price = 1
#             else:
#                 diff = price - max_price
#                 P_price = max(0, 1 - diff / max_price) if max_price > 0 else 0
#         else:
#             P_price = 1 if price == 0 else 0.5
#     if filters.is_free is True and price > 0:
#         P_price *= 0.5
#     elif filters.is_free is False and price == 0:
#         P_price *= 0.5
#
#     # ===== P_free (наличие бюджетных мест) =====
#     try:
#         free_places = int(program.forms[0]["free_places"])
#     except (ValueError, TypeError, KeyError):
#         free_places = 0
#
#     if filters.is_free is True or filters.is_free is None:
#         if free_places > 0:
#             P_free = min(1.0, free_places / 50)  # Например, 50 мест = максимум 1
#         else:
#             P_free = 0
#     else:  # filters.is_free is False (ищут платное)
#         P_free = 0
#
#     # ===== P_fill (заполненность) =====
#     total_fields = 8
#     filled = 0
#     if program.direction and (not filters.direction or filters.direction.lower() in program.direction.lower()):
#         filled += 1
#     if program.university.geolocation and (
#             not filters.region or filters.region.lower() in program.university.geolocation.lower()):
#         filled += 1
#     if program.university.rating is not None:
#         filled += 1
#     if program.university.is_goverment is not None and (
#             filters.is_goverment is None or program.university.is_goverment == filters.is_goverment):
#         filled += 1
#
#     form = program.forms[0] if program.forms else None
#
#     if not filters.education_form or any(
#             filters.education_form.lower() in form.education_form2.lower()
#             for form in program.forms if form.education_form2
#     ):
#         filled += 1
#
#     if form and form.score is not None:
#         pass_score = form.score
#         if filters.user_score is None or pass_score <= filters.user_score + 10:
#             filled += 1
#     if form and form.price is not None and (filters.max_price is None or form.price <= abs(filters.max_price)):
#         filled += 1
#     if form and form.free_places and form.free_places > 0:
#         filled += 1
#
#     # if "score" in program.forms[0] and (filters.user_score is None or pass_score <= (
#     #         filters.user_score + 10)):  # Учитываем условие <= user_score + 10
#     #     filled += 1
#     # if "price" in program.forms[0] and (filters.max_price is None or price <= abs(filters.max_price)):
#     #     filled += 1
#     # if "free_places" in program.forms[0] and free_places > 0:
#     #     filled += 1
#     P_fill = filled / total_fields
#
#     # Итоговый рейтинг
#     return (
#             weights["W_ex"] * P_ex +
#             weights["W_rat"] * P_rat +
#             weights["W_dorm"] * P_dorm +
#             weights["W_gov"] * P_gov +
#             weights["W_price"] * P_price +
#             weights["W_fill"] * P_fill +
#             weights["W_free"] * P_free
#     )


def safe_int(val: Optional[str | int]) -> Optional[int]:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None

def compute_program_score(program: Program, filters: UniversityFilterParams) -> float:
    weights = get_weight_config()
    form = program.forms[0] if program.forms else None

    score = form.score if form else None
    price = form.price if form else None
    free_places = safe_int(form.free_places) if form and form.free_places else 0

    # === P_ex ===
    user_score = filters.user_score
    P_ex = (
        max(0, 1 - abs(user_score - score) / 50)
        if user_score is not None and score is not None and abs(user_score - score) <= 50
        else 0
    )

    # === P_rat ===
    P_rat = min(max((program.university.rating or 0) / 100, 0), 1)

    # === P_dorm ===
    P_dorm = 1 if getattr(program.university.dormitory, "dormitory", False) else 0

    # === P_gov ===
    is_gov = program.university.is_goverment
    P_gov = 1 if is_gov else 0
    if filters.is_goverment is not None:
        P_gov *= 1.5 if is_gov == filters.is_goverment else 0.5

    # === P_price ===
    P_price = 1
    if filters.is_free and (not score or (price and price > 0)):
        P_price = 0.5
    elif filters.is_free is False and (not price or price == 0):
        P_price = 0.5
    elif price and filters.max_price is not None:
        diff = price - abs(filters.max_price)
        P_price = max(0, 1 - diff / abs(filters.max_price)) if diff > 0 else 1

    # === P_free ===
    P_free = min(1.0, free_places / 50) if (filters.is_free is None or filters.is_free) and free_places > 0 else 0

    # === P_fill ===
    total_fields = 8
    filled = sum([
        bool(program.direction and (not filters.direction or normalize_str(filters.direction) in normalize_str(program.direction))),
        bool(program.university.geolocation and (not filters.region or normalize_str(filters.region) in normalize_str(program.university.geolocation))),
        program.university.rating is not None,
        filters.is_goverment is None or is_gov == filters.is_goverment,
        any(
            not filters.education_form or
            normalize_str(filters.education_form) in normalize_str(f.education_form2)
            for f in program.forms if f.education_form2
        ) if program.forms else False,
        score is not None and (filters.user_score is None or score <= filters.user_score + 10),
        price is not None and (filters.max_price is None or price <= abs(filters.max_price)),
        free_places > 0
    ])
    P_fill = filled / total_fields

    # === Финальный рейтинг ===
    return (
        weights["W_ex"] * P_ex +
        weights["W_rat"] * P_rat +
        weights["W_dorm"] * P_dorm +
        weights["W_gov"] * P_gov +
        weights["W_price"] * P_price +
        weights["W_fill"] * P_fill +
        weights["W_free"] * P_free
    )
