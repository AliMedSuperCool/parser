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

        # Цена (у тебя отрицательная логика цены, т.е. -121500)
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

        # Группировка программ по вузам
        grouped: Dict[str, Dict] = {}

        for prog in programs:
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

            grouped[uni.long_name]["programs"].append(prog)

        # return [UniversityWithProgramsOut(**v) for v in grouped.values()]
        return [
            UniversityWithProgramsOut(
                **{
                    **v,
                    "dormitory": DormitoryOut.model_validate(v["dormitory"]) if v["dormitory"] else None,
                    "programs": [ProgramShortOut.model_validate(p) for p in v["programs"]]
                }
            )
            for v in grouped.values()
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
