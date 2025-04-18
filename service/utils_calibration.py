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
    P_dorm = 1 if getattr(program.university.has_dormitory, "dormitory", False) else 0

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
        bool(program.direction and (
                    not filters.direction or normalize_str(filters.direction) in normalize_str(program.direction))),
        bool(program.university.geolocation and (not filters.region or normalize_str(filters.region) in normalize_str(
            program.university.geolocation))),
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
