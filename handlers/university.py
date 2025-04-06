import math

from fastapi import HTTPException
from typing import List, Annotated, Optional, Any, Dict, Union

from fastapi import APIRouter, status, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy import select, and_, Integer, func
from sqlalchemy.orm import Session, joinedload, selectinload

from database import get_db_session
from models import Program, University
from shema import UniversityShema

router = APIRouter(prefix="/task", tags=["task"])


class ProgramResponse(BaseModel):
    id: int
    direction: str
    profile: str
    program_code: str
    faculty: str
    exams: Optional[List[List[str]]] = None
    scores: Optional[List[List[str]]] = None
    forms: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class DormitoryResponse(BaseModel):
    id: int
    dormitory: bool
    info: Optional[str] = None
    rating: Optional[float] = None

    class Config:
        from_attributes = True


class UniversityResponse(BaseModel):
    id: int
    long_name: str
    short_name: str
    geolocation: Optional[str] = None
    is_goverment: Optional[bool] = None
    rating: Optional[int] = None
    logo: Optional[str] = None
    website: Optional[str] = None
    phone_admission: Optional[list[str]] = None
    phone_general: Optional[list[str]] = None
    email_general: Optional[list[str]] = None
    email_admission: Optional[list[str]] = None
    army: Optional[bool] = None
    comment: Optional[str] = None

    dormitory: Optional[DormitoryResponse] = None
    programs: Optional[ProgramResponse] = None

    class Config:
        from_attributes = True


@router.get("/test")
def get_first_5_universities(db: Session = Depends(get_db_session)):
    with db() as db:
        stmt = select(University).limit(5)
        results = db.scalars(stmt).all()

        for vuz in results:
            print(f"Вуз: {vuz.long_name}")
            print(f"Oбщага: {vuz.dormitory.dormitory}")
            if vuz.programs is not None:
                # print(f"Вуз программы: {vuz.programs.vuz_long_name}")
                for program in vuz.programs:
                    print(f"  Программа ID: {program.id}, вуз: {program.exams}", )
                    # return [ProgramResponse.model_validate(uni) for uni in universities]



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

    class Config:
        from_attributes = True



@router.get("/grouped-programs", response_model=List[UniversityWithProgramsOut])
async def get_grouped_programs(
    filters: ProgramFilterParams = Depends(),
    session: Session = Depends(get_db_session),
):
    with session() as session:
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

        # Бесплатное/платное (score может быть "Только платное", price >= 0 или < 0)
        if filters.is_free is True:
            conditions.append(
                Program.forms[0]["score"].astext != "Только платное"
            )
        elif filters.is_free is False:
            conditions.append(
                Program.forms[0]["score"].astext == "Только платное"
            )

        # Минимальный балл
        if filters.min_score:
            conditions.append(
                func.nullif(Program.forms[0]["score"].astext).cast(Integer) >= filters.min_score
            )

        # Цена (у вас там отрицательные значения цены, т.е. -121500)
        if filters.max_price is not None:
            conditions.append(
                Program.forms[0]["price"].astext.cast(Integer) >= -abs(filters.max_price)
            )

        # Гос/не гос
        if filters.is_goverment is not None:
            stmt = stmt.join(Program.university)
            conditions.append(University.is_goverment == filters.is_goverment)

        # Регион (в поле geolocation)
        if filters.region:
            conditions.append(University.geolocation.ilike(f"%{filters.region}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = session.execute(stmt)
        programs = result.scalars().all()

        # ----------------------------
        # 1. Считаем рейтинг программы
        # ----------------------------

        # Предположим, у нас есть некие данные от пользователя:
        user_total_score = filters.  # Например, сумма баллов ЕГЭ
        user_ege_count = filters.ege_count or 3  # Сколько предметов ЕГЭ
        user_price_min = filters.user_price_min or 0  # Мин. цена, которую пользователь готов платить
        user_price_max = filters.user_price_max or 999999  # Макс. цена

        # Веса
        W_ex = 0.4
        W_rat = 0.3
        W_dorm = 0.1
        W_gov = 0.1
        W_price = 0.05
        W_fill = 0.05

        # Для удобства выносим логику в небольшую функцию
        def compute_program_score(program: Program) -> float:
            """
            Возвращает итоговый рейтинг (res) для одной программы.
            Все формулы из условия, часть логики упрощена/примерная,
            адаптируйте под реальную структуру ваших данных.
            """

            # ===== P_ex (экзамен) =====
            # Предположим, в program.forms[0]["score"] хранится минимальный проходной балл,
            # если он не "Только платное". Если None или не парсится, ставим 0.
            try:
                pass_score = int(program.forms[0]["score"])
            except:
                # нет или "Только платное" — можем считать проходной = 0, или любой другой дефолт
                pass_score = 0

            # Если у пользователя нет среднего балла, P_ex = 0.
            # Иначе по формуле:
            # P_ex = max(0, (user_total_score - pass_score) / (user_ege_count * 100 - pass_score))
            if user_total_score and pass_score and user_ege_count:
                denominator = user_ege_count * 100 - pass_score
                if denominator <= 0:
                    P_ex = 0
                else:
                    P_ex = max(0, (user_total_score - pass_score) / denominator)
            else:
                P_ex = 0

            # ===== P_rat (рейтинг вуза) =====
            # Пусть рейтинг лежит в поле university.rating
            # Предположим, что рейтинг в диапазоне [0..100], тогда масштабируем до [0..1]
            uni_rating = program.university.rating or 0
            P_rat = min(max(uni_rating / 100, 0), 1)

            # ===== P_dorm (общежитие) =====
            # 1, если есть, 0, если нет
            P_dorm = 1 if program.university.dormitory else 0

            # ===== P_gov (гос. вуз) =====
            # 1, если гос, 0, если не гос
            P_gov = 1 if program.university.is_goverment else 0

            # ===== P_price (цена) =====
            # Если бюджетное место (или бесплатно), P_price = 1
            # Иначе применяем логику
            #   p – цена, user_price_min, user_price_max – интервал
            #   если p в [min, max] => 1
            #   если p < min => max(0, 1 - (min - p)/min)
            #   если p > max => max(0, 1 - (p - max)/max)
            try:
                price = abs(int(program.forms[0]["price"]))
            except:
                price = 0

            # Если "score" == "Только платное", значит не бюджет
            # Но если price == 0, предположим, что это значит "бюджетное".
            if price == 0:
                P_price = 1
            else:
                if user_price_min <= price <= user_price_max:
                    P_price = 1
                elif price < user_price_min:
                    if user_price_min == 0:
                        P_price = 0  # во избежание деления на 0
                    else:
                        diff = user_price_min - price
                        P_price = max(0, 1 - diff / user_price_min)
                else:  # price > user_price_max
                    diff = price - user_price_max
                    if user_price_max == 0:
                        P_price = 0
                    else:
                        P_price = max(0, 1 - diff / user_price_max)

            # ===== P_fill (заполненность) =====
            # Условно считаем, сколько есть непустых полей в программе, делим на общее число полей
            # Допустим, total_fields = 5, fields = [direction, forms, description, ...]
            # Реальный набор полей надо определить самим
            total_fields = 5
            filled = 0
            if program.direction:
                filled += 1
            if program.forms:
                filled += 1
            if program.university.geolocation:
                filled += 1
            if program.university.rating is not None:
                filled += 1
            # и т.д. — добавляйте нужные поля
            P_fill = filled / total_fields

            # Итоговый рейтинг
            res = (
                W_ex * P_ex
                + W_rat * P_rat
                + W_dorm * P_dorm
                + W_gov * P_gov
                + W_price * P_price
                + W_fill * P_fill
            )
            return res

        # Создаем структуру, где для каждого Program считаем рейтинг:
        program_with_score = []
        for prog in programs:
            score = compute_program_score(prog)
            program_with_score.append((prog, score))

        # ----------------------------
        # 2. Сортируем программы
        # ----------------------------
        # По убыванию рейтинга:
        program_with_score.sort(key=lambda x: x[1], reverse=True)

        # ----------------------------
        # 3. Группируем по вузам
        # ----------------------------
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

            # Обратите внимание: чтобы в ответе тоже был рейтинг, нужно либо
            # расширить схему ProgramShortOut полем "score", либо вернуть это
            # дополнительным полем. Для примера будем класть в словарь:
            prog_dict = ProgramShortOut.model_validate(prog).model_dump()
            prog_dict["ranking"] = score

            grouped[uni.long_name]["programs"].append(prog_dict)

        # Если хотите также отсортировать вузы по максимальному (или среднему) рейтингу программ:
        # например, берем максимум
        def get_uni_best_score(uni_data):
            programs_ = uni_data["programs"]
            if not programs_:
                return 0
            return max(p["ranking"] for p in programs_)

        # Преобразуем в список, сортируем
        grouped_list = list(grouped.values())
        grouped_list.sort(key=get_uni_best_score, reverse=True)

        # ----------------------------
        # 4. Финальный возврат
        # ----------------------------
        return [
            UniversityWithProgramsOut(
                **{
                    **v,
                    "dormitory": DormitoryOut.model_validate(v["dormitory"]) if v["dormitory"] else None,
                    # Превращаем список словарей обратно в список ProgramShortOut,
                    # если у вас у ProgramShortOut есть поле ranking, нужно дополнить модель:
                    "programs": [ProgramShortOut(**p) for p in v["programs"]]
                }
            )
            for v in grouped_list
        ]
















    #
    # with db() as db:
    #     stmt = select(University).limit(5)
    #     results = db.scalars(stmt).all()
    #
    #     for vuz in results:
    #         print(f"Вуз: {vuz.long_name}")
    #         if vuz.programs is not None:
    #             print(f"Вуз программы: {vuz.programs.vuz_long_name}")
    #             for program in vuz.programs:
    #                 print(f"  Программа ID: {program.id}, вуз: {program.vuz_long_name}")
# @router.get("/all", response_model=List[TaskShema])
# async def get_tasks(task_service: Annotated[TaskService, Depends(get_tasks_service)]):
#     return task_service.get_tasks(user_id=user_id)
#
#
#
# @router.post("/", response_model=TaskShema)
# async def create_task(
#         body: TaskCreateShema,
#         task_service: Annotated[TaskService, Depends(get_tasks_service)],
#         user_id: int = Depends(get_request_user_id)
# ) -> TaskShema:
#     task = task_service.create_task(body, user_id)
#     return task
#
#
# @router.patch("/{task_id}", response_model=TaskShema)
# async def update_task(
#         task_id: int,
#         name: str,
#         task_service: Annotated[TaskService, Depends(get_tasks_service)],
#         user_id: int = Depends(get_request_user_id)
# ):
#     # task = next((task for task in fixture_tasks if task["id"] == task_id), None)
#     try:
#         return task_service.update_task_name(task_id=task_id, name=name, user_id=user_id)
#     except TaskNotFound as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
#
#
# @router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_item(
#         task_id: int,
#         task_service: Annotated[TaskService, Depends(get_tasks_service)],
#         user_id: int = Depends(get_request_user_id)):
#     try:
#         task_service.delete_task(task_id=task_id, user_id=user_id)
#     except TaskNotFound as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
