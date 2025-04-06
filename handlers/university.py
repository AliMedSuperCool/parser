import math

from fastapi import HTTPException
from typing import List, Annotated, Optional, Any, Dict, Union

from fastapi import APIRouter, status, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy import select, and_, Integer, func, or_, exists
from sqlalchemy.orm import Session, joinedload, selectinload

from database import get_db_session
from models import Program, University
from shema import UniversityShema

router = APIRouter(prefix="/task", tags=["task"])

#------------------------------------------------------------------------------######################################


class ProgramFilterParams(BaseModel):
    university_name: Optional[str] = Field(None, description="Название вуза")
    program_code: Optional[str] = Field(None, description="Код направления")
    profile: Optional[str] = Field(None, description="Профиль")
    faculty: Optional[str] = Field(None, description="Факультет")
    education_form2: Optional[str] = Field(None, description="Форма обучения (из JSONB поля)")




class ProgramOut(BaseModel):
    id: int
    direction: str
    profile: str
    program_code: str
    vuz_long_name: str
    faculty: str
    exams: Optional[List[List[str]]]
    scores: Optional[List[List[str]]]
    forms: Optional[List[Dict]]

    class Config:
        orm_mode = True


class DormitoryOut(BaseModel):
    dormitory: bool
    info: Optional[str] = None
    rating: Optional[Union[float,str]] = None

    @validator("rating", pre=True)
    def replace_nan_with_none(cls, v):
        if isinstance(v, float) and math.isnan(v):
            return None
        return v

    class Config:
        from_attributes = True
        allow_inf_nan = True


class UniversityOut(BaseModel):
    long_name: str
    dormitory: Optional[DormitoryOut]  # или bool, если в модели храним True/False

    class Config:
        from_attributes = True


class ProgramOut(BaseModel):
    id: int
    direction: str
    profile: str
    program_code: str
    vuz_long_name: str
    faculty: str
    exams: Optional[List[List[str]]]
    scores: Optional[List[List[str]]]
    forms: Optional[List[Dict]]
    university: UniversityOut

    class Config:
        from_attributes = True


@router.get("/programs", response_model=List[ProgramOut])
async def get_programs(
        filters: ProgramFilterParams = Depends(),
        session: Session = Depends(get_db_session),
):
    with session() as session:
        stmt = select(Program).options(joinedload(Program.university))
        conditions = []

        if filters.university_name:
            conditions.append(Program.vuz_long_name.ilike(f"%{filters.university_name}%"))

        if filters.program_code:
            conditions.append(Program.program_code == filters.program_code)

        if filters.profile:
            conditions.append(Program.profile.ilike(f"%{filters.profile}%"))

        if filters.faculty:
            conditions.append(Program.faculty.ilike(f"%{filters.faculty}%"))

        if filters.education_form2:
            # PostgreSQL JSONB: forms[0]->>'education_form2'
            conditions.append(
                Program.forms[0]["education_form2"].astext == filters.education_form2
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(filters.offset).limit(filters.limit)

        result = session.execute(stmt)
        programs = result.scalars().all()
        return programs



# ------------------------------------------------------------------------------######################################
from pydantic import BaseModel, Field
from typing import Optional

from pydantic import BaseModel
from typing import List, Optional, Dict

class DormitoryOut(BaseModel):
    dormitory: bool
    info: Optional[str] = None
    rating: Optional[Union[float,str]] = None

    @validator("rating", pre=True)
    def replace_nan_with_none(cls, v):
        if isinstance(v, float) and math.isnan(v):
            return None
        return v

    class Config:
        from_attributes = True
        allow_inf_nan = True

class ProgramShortOut(BaseModel):
    id: int
    direction: str
    profile: str
    program_code: str
    faculty: str
    forms: Optional[List[Dict]]  # Включает баллы, цену, форму обучения

    class Config:
        from_attributes = True

class UniversityWithProgramsOut(BaseModel):
    id: int
    long_name: str
    short_name: str
    geolocation: Optional[str]
    is_goverment: Optional[bool]
    rating: Optional[int]
    dormitory: Optional[DormitoryOut]
    programs: List[ProgramShortOut]

    class Config:
        from_attributes = True



class ProgramFilterParams(BaseModel):
    direction: Optional[str] = Field(None, description="Направление")
    education_form: Optional[str] = Field(None, description="Очная/Заочная")
    is_free: Optional[bool] = Field(None, description="Только бесплатные места")
    user_score: Optional[int] = Field(None, description="Балл пользователя")
    max_price: Optional[int] = Field(None, description="Максимальная цена (отрицательная)")
    is_goverment: Optional[bool] = Field(None, description="Гос или не гос")
    region: Optional[str] = Field(None, description="Регион (по university.geolocation)")
    page_size: int = Field(5, ge=1, le=50, description="Сколько программ вернуть")
    page: int = Field(1, ge=1, description="Пропустить программ")

    class Config:
        from_attributes = True

# Веса для ранжирования
W_ex = 0.5    # Экзамены (близость к user_score) — самый важный
W_rat = 0.25  # Рейтинг университета — второй по важности
W_dorm = 0.05 # Наличие общежития
W_gov = 0.05  # Государственный вуз
W_price = 0.05  # Цена
W_fill = 0.025  # Заполненность
W_free = 0.075  # Наличие бюджетных мест

def compute_program_score(program: Program, filters: ProgramFilterParams) -> float:
    """
    Вычисляет рейтинг программы с учетом всех параметров из ProgramFilterParams.
    Больше очков дается программам, где pass_score ближе к user_score.
    """
    # ===== P_ex (экзамен) =====
    try:
        pass_score = int(program.forms[0]["score"])
    except (ValueError, TypeError, KeyError):
        pass_score = 0

    if filters.user_score and pass_score:
        # Вычисляем абсолютную разницу между user_score и pass_score
        score_diff = abs(filters.user_score - pass_score)
        # Максимальная допустимая разница (например, 50 баллов), чтобы рейтинг не обнулился
        max_diff = 50
        if score_diff <= max_diff:
            # Чем меньше разница, тем выше рейтинг (линейное убывание от 1 до 0)
            P_ex = 1 - (score_diff / max_diff)
        else:
            P_ex = 0  # Если разница больше max_diff, рейтинг 0
    else:
        P_ex = 0

    # ===== P_rat (рейтинг вуза) =====
    uni_rating = program.university.rating or 0
    P_rat = min(max(uni_rating / 100, 0), 1)

    # ===== P_dorm (общежитие) =====
    P_dorm = 1 if program.university.dormitory else 0

    # ===== P_gov (гос. вуз) =====
    P_gov = 1 if program.university.is_goverment else 0
    if filters.is_goverment is not None:
        P_gov *= 1.5 if (P_gov == (1 if filters.is_goverment else 0)) else 0.5

    # ===== P_price (цена) =====
    try:
        price = abs(int(program.forms[0]["price"]))
    except (ValueError, TypeError, KeyError):
        price = 0

    if price == 0 or (filters.is_free is True and program.forms[0]["score"] != "Только платное"):
        P_price = 1
    else:
        if filters.max_price is not None:
            max_price = abs(filters.max_price)
            if price <= max_price:
                P_price = 1
            else:
                diff = price - max_price
                P_price = max(0, 1 - diff / max_price) if max_price > 0 else 0
        else:
            P_price = 1 if price == 0 else 0.5

    if filters.is_free is True and price > 0:
        P_price *= 0.5
    elif filters.is_free is False and price == 0:
        P_price *= 0.5

    # ===== P_free (наличие бюджетных мест) =====
    try:
        free_places = int(program.forms[0]["free_places"])
    except (ValueError, TypeError, KeyError):
        free_places = 0

    if filters.is_free is True or filters.is_free is None:
        if free_places > 0:
            P_free = min(1.0, free_places / 50)  # Например, 50 мест = максимум 1
        else:
            P_free = 0
    else:  # filters.is_free is False (ищут платное)
        P_free = 0

    # ===== P_fill (заполненность) =====
    total_fields = 8
    filled = 0
    if program.direction and (not filters.direction or filters.direction.lower() in program.direction.lower()):
        filled += 1
    if program.forms:
        if not filters.education_form or any(
            form.get("education_form2", "").lower().find(filters.education_form.lower()) != -1
            for form in program.forms
        ):
            filled += 1
    if program.university.geolocation and (not filters.region or filters.region.lower() in program.university.geolocation.lower()):
        filled += 1
    if program.university.rating is not None:
        filled += 1
    if program.university.is_goverment is not None and (filters.is_goverment is None or program.university.is_goverment == filters.is_goverment):
        filled += 1
    if "score" in program.forms[0] and (filters.user_score is None or pass_score <= (filters.user_score + 10)):  # Учитываем условие <= user_score + 10
        filled += 1
    if "price" in program.forms[0] and (filters.max_price is None or price <= abs(filters.max_price)):
        filled += 1
    if "free_places" in program.forms[0] and free_places > 0:
        filled += 1
    P_fill = filled / total_fields

    # Итоговый рейтинг
    res = (
        W_ex * P_ex
        + W_rat * P_rat
        + W_dorm * P_dorm
        + W_gov * P_gov
        + W_price * P_price
        + W_fill * P_fill
        + W_free * P_free
    )
    return res

from sqlalchemy import exists, select

from sqlalchemy import exists, select

@router.get("/grouped-programs", response_model=List[UniversityWithProgramsOut])
async def get_grouped_programs(
    filters: ProgramFilterParams = Depends(),
    session: Session = Depends(get_db_session),
):
    with session() as session:
        no_filters_applied = all(
            getattr(filters, field) is None
            for field in filters.__fields__
            if field not in ["page", "page_size"]
        )

        if no_filters_applied:
            filters.region = "Москва"
            filters.is_free = True

        # Базовый запрос с присоединением университета и общежития
        stmt = select(Program).options(
            joinedload(Program.university).joinedload(University.dormitory)
        )

        conditions = []

        if filters.direction:
            conditions.append(Program.direction.ilike(f"%{filters.direction}%"))

        # Подзапрос для разворачивания JSONB массива forms
        forms_subquery = (
            select(
                Program.id.label("program_id"),
                func.jsonb_extract_path_text(func.jsonb_array_elements(Program.forms), "education_form2").label("education_form2"),
                func.jsonb_extract_path_text(func.jsonb_array_elements(Program.forms), "score").label("score"),
                func.jsonb_extract_path_text(func.jsonb_array_elements(Program.forms), "price").label("price")
            )
            .subquery("forms_expanded")
        )

        # Условия для JSONB поля forms
        if filters.education_form:
            conditions.append(
                exists(
                    select(1)
                    .select_from(forms_subquery)
                    .where(
                        and_(
                            forms_subquery.c.program_id == Program.id,
                            forms_subquery.c.education_form2.ilike(f"%{filters.education_form}%")
                        )
                    )
                )
            )

        if filters.is_free is True:
            conditions.append(
                exists(
                    select(1)
                    .select_from(forms_subquery)
                    .where(
                        and_(
                            forms_subquery.c.program_id == Program.id,
                            forms_subquery.c.score != "Только платное"
                        )
                    )
                )
            )
        elif filters.is_free is False:
            conditions.append(
                exists(
                    select(1)
                    .select_from(forms_subquery)
                    .where(
                        and_(
                            forms_subquery.c.program_id == Program.id,
                            or_(
                                forms_subquery.c.score == "Только платное",
                                func.coalesce(
                                    func.nullif(forms_subquery.c.price, "no data").cast(Integer),
                                    0
                                ) > 0
                            )
                        )
                    )
                )
            )

        if filters.user_score is not None:
            conditions.append(
                exists(
                    select(1)
                    .select_from(forms_subquery)
                    .where(
                        and_(
                            forms_subquery.c.program_id == Program.id,
                            forms_subquery.c.score.op('~')('^[0-9]+$'),
                            func.nullif(forms_subquery.c.score, "Только платное").cast(Integer) <= (filters.user_score + 10)
                        )
                    )
                )
            )

        if filters.max_price is not None:
            conditions.append(
                exists(
                    select(1)
                    .select_from(forms_subquery)
                    .where(
                        and_(
                            forms_subquery.c.program_id == Program.id,
                            forms_subquery.c.price != "no data",
                            func.coalesce(
                                func.nullif(forms_subquery.c.price, "no data").cast(Integer),
                                0
                            ) <= abs(filters.max_price)
                        )
                    )
                )
            )

        if filters.is_goverment is not None:
            stmt = stmt.join(Program.university)
            conditions.append(University.is_goverment == filters.is_goverment)

        if filters.region:
            stmt = stmt.join(Program.university)
            conditions.append(University.geolocation.ilike(f"%{filters.region}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = session.execute(stmt)
        programs = result.scalars().all()

        program_with_score = []
        for prog in programs:
            score = compute_program_score(prog, filters)
            program_with_score.append((prog, score))

        program_with_score.sort(key=lambda x: x[1], reverse=True)

        grouped: Dict[str, Dict] = {}
        for prog, score in program_with_score:
            uni = prog.university
            if uni.long_name not in grouped:
                grouped[uni.long_name] = {
                    "id": uni.id,
                    "long_name": uni.long_name,
                    "short_name": uni.short_name,
                    "geolocation": uni.geolocation,
                    "is_goverment": uni.is_goverment,
                    "rating": uni.rating,
                    "dormitory": uni.dormitory,
                    "programs": []
                }
            # Фильтруем forms, чтобы включать только те, что соответствуют education_form
            filtered_forms = prog.forms
            if filters.education_form:
                filtered_forms = [
                    form for form in prog.forms
                    if form.get("education_form2", "").lower().find(filters.education_form.lower()) != -1
                ]
            prog_dict = ProgramShortOut.model_validate(prog).model_dump()
            prog_dict["forms"] = filtered_forms  # Заменяем forms на отфильтрованные
            prog_dict["ranking"] = score
            grouped[uni.long_name]["programs"].append(prog_dict)

        grouped_list = list(grouped.values())
        grouped_list.sort(key=lambda x: max(p["ranking"] for p in x["programs"]) if x["programs"] else 0, reverse=True)

        offset = (filters.page - 1) * filters.page_size
        paginated_grouped_list = grouped_list[offset:offset + filters.page_size]

        return [
            UniversityWithProgramsOut(
                **{
                    **v,
                    "dormitory": DormitoryOut.model_validate(v["dormitory"]) if v["dormitory"] else None,
                    "programs": [ProgramShortOut(**p) for p in v["programs"]]
                }
            )
            for v in paginated_grouped_list
        ]