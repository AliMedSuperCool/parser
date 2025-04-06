import math

from fastapi import HTTPException
from typing import List, Annotated, Optional, Any, Dict, Union

from fastapi import APIRouter, status, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy import select, and_, Integer, func, or_
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
    min_score: Optional[int] = Field(None, description="Минимальный балл")
    max_price: Optional[int] = Field(None, description="Максимальная цена (отрицательная)")
    is_goverment: Optional[bool] = Field(None, description="Гос или не гос")
    region: Optional[str] = Field(None, description="Регион (по university.geolocation)")
    limit: int = Field(50, ge=1, le=500, description="Сколько программ вернуть")
    offset: int = Field(0, ge=0, description="Пропустить программ")

    class Config:
        from_attributes = True



# Веса для ранжирования
W_ex = 0.4    # Экзамены (минимальный балл)
W_rat = 0.3   # Рейтинг университета
W_dorm = 0.1  # Наличие общежития
W_gov = 0.1   # Государственный вуз
W_price = 0.05  # Цена
W_fill = 0.05  # Заполненность
W_free = 0.1  # Наличие бюджетных мест (добавляем новый вес, корректируем другие если нужно)

def compute_program_score(program: Program, filters: ProgramFilterParams) -> float:
    """
    Вычисляет рейтинг программы с учетом всех параметров из ProgramFilterParams, включая free_places.
    """
    # ===== P_ex (экзамен) =====
    try:
        pass_score = int(program.forms[0]["score"])
    except (ValueError, TypeError, KeyError):
        pass_score = 0

    if filters.min_score and pass_score:
        user_ege_count = 3  # Условно, можно сделать параметром
        denominator = user_ege_count * 100 - pass_score
        if denominator <= 0:
            P_ex = 0
        else:
            P_ex = max(0, (filters.min_score - pass_score) / denominator)
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

    # Если ищут бюджетное (is_free=True) или не указано (is_free=None), наличие мест повышает рейтинг
    if filters.is_free is True or filters.is_free is None:
        if free_places > 0:
            # Масштабируем: больше мест -> выше рейтинг, но не более 1
            P_free = min(1.0, free_places / 50)  # Например, 50 мест = максимум 1
        else:
            P_free = 0
    else:  # filters.is_free is False (ищут платное)
        P_free = 0  # Бюджетные места не влияют на рейтинг

    # ===== P_fill (заполненность) =====
    total_fields = 8  # Увеличиваем на 1 из-за free_places
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
    if "score" in program.forms[0] and (filters.min_score is None or pass_score >= filters.min_score):
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
        + W_free * P_free  # Добавляем вклад бюджетных мест
    )
    return res

@router.get("/grouped-programs", response_model=List[UniversityWithProgramsOut])
async def get_grouped_programs(
    filters: ProgramFilterParams = Depends(),
    session: Session = Depends(get_db_session),
):
    with session() as session:
        # Базовый запрос с подгрузкой связанных данных
        stmt = select(Program).options(
            joinedload(Program.university).joinedload(University.dormitory)
        )

        conditions = []

        # Фильтрация по направлению
        if filters.direction:
            conditions.append(Program.direction.ilike(f"%{filters.direction}%"))

        # Форма обучения в JSONB
        if filters.education_form:
            conditions.append(
                Program.forms[0]["education_form2"].astext.ilike(f"%{filters.education_form}%")
            )

        # Бесплатное/платное
        if filters.is_free is True:
            conditions.append(
                Program.forms[0]["score"].astext != "Только платное"
            )
        elif filters.is_free is False:
            conditions.append(
                or_(
                    Program.forms[0]["score"].astext == "Только платное",
                    Program.forms[0]["price"].astext.cast(Integer) < 0
                )
            )

        # Минимальный балл
        if filters.min_score:  # что это
            conditions.append(
                func.nullif(Program.forms[0]["score"].astext, "Только платное").cast(Integer) >= filters.min_score
            )

        # Максимальная цена
        if filters.max_price is not None:
            conditions.append(
                func.coalesce(
                    func.nullif(Program.forms[0]["price"].astext, "no data").cast(Integer),
                    0  # Значение по умолчанию для нечисловых значений
                ) >= -abs(filters.max_price)
            )

        # Гос/не гос
        if filters.is_goverment is not None:
            stmt = stmt.join(Program.university)
            conditions.append(University.is_goverment == filters.is_goverment)

        # Регион
        if filters.region:
            stmt = stmt.join(Program.university)
            conditions.append(University.geolocation.ilike(f"%{filters.region}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Выполнение запроса
        result = session.execute(stmt)
        programs = result.scalars().all()

        # Ранжирование программ
        program_with_score = []
        for prog in programs:
            score = compute_program_score(prog, filters)
            program_with_score.append((prog, score))

        # Сортировка по убыванию рейтинга
        program_with_score.sort(key=lambda x: x[1], reverse=True)

        # Группировка по университетам
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
            prog_dict = ProgramShortOut.model_validate(prog).model_dump()
            prog_dict["ranking"] = score
            grouped[uni.long_name]["programs"].append(prog_dict)

        # Сортировка университетов по максимальному рейтингу программ
        grouped_list = list(grouped.values())
        grouped_list.sort(key=lambda x: max(p["ranking"] for p in x["programs"]) if x["programs"] else 0, reverse=True)

        # Формирование ответа
        return [
            UniversityWithProgramsOut(
                **{
                    **v,
                    "dormitory": DormitoryOut.model_validate(v["dormitory"]) if v["dormitory"] else None,
                    "programs": [ProgramShortOut(**p) for p in v["programs"]]
                }
            )
            for v in grouped_list
        ]




