from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import ValidationError
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from database import get_db_session
from handlers.utils import apply_program_filters
from models import Program, University
from shema import (UniversityFilterParams, ProgramShortReturn,
                   UniversityProgramsReturn, get_filter_params)
from utils.calibration import compute_program_score

router = APIRouter(prefix="/university", tags=["university"])


# @router.get("/university-filtering", response_model=List[UniversityProgramsReturn])
# async def get_tasks(filters: UniversityFilterParams = Depends(get_filter_params),
#                     university_service: Annotated[UniversityService, Depends(get_university_service)]):
#     return university_service.filtering(filters)


@router.post("/university-filtering", response_model=List[UniversityProgramsReturn])
async def university_filtering(
        filters: UniversityFilterParams = Depends(get_filter_params),
        session: Session = Depends(get_db_session),
):
    no_filters_applied = not any(
        getattr(filters, f) is not None
        for f in filters.model_fields
        if f not in {"page", "page_size"}
    )

    if no_filters_applied:
        filters.region = "Москва"
        filters.is_free = True
        filters.has_army = True

    with session() as session:

        stmt = select(Program).options(
            selectinload(Program.university), selectinload(Program.forms)
        )

        if any(
                [
                    filters.long_name,
                    filters.short_name,
                    filters.is_goverment,
                    filters.has_dormitory,
                    filters.has_army,
                    filters.region,
                ]
        ):
            stmt = stmt.join(Program.university)
            # stmt = stmt.join(Program, Program.university_id == University.id)

        conditions = []
        if filters.direction:
            conditions.append(Program.direction.ilike(f"%{filters.direction}%"))

        # forms_subquery = build_forms_subquery()
        stmt = apply_program_filters(stmt, filters)

        if filters.long_name:
            # stmt = stmt.join(Program.university)
            conditions.append(University.long_name.ilike(f"%{filters.long_name}%"))

        if filters.short_name:
            # stmt = stmt.join(Program.university)
            conditions.append(University.short_name.ilike(f"%{filters.short_name}%"))

        if filters.is_goverment:
            # stmt = stmt.join(Program.university)
            conditions.append(University.is_goverment == filters.is_goverment)
        #
        if filters.has_dormitory:
            # Подтягиваем таблицу University, если еще не джойнили
            # stmt = stmt.join(University.dormitory)
            conditions.append(University.has_dormitory == filters.has_dormitory)
        #

        if filters.has_army:
            # stmt = stmt.join(Program.university)
            conditions.append(University.army == filters.has_army)
        #
        if filters.region:
            # stmt = stmt.join(Program.university)
            conditions.append(University.geolocation.ilike(f"%{filters.region}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # 2) Забираем программы из БД
        result = session.execute(stmt)
        programs = result.scalars().all()

        # Фильтрация по экзаменам в Python
        if filters.user_exams:
            user_exams_set = set(e.strip().upper() for e in filters.user_exams)

            def check_exams(program_exams: List[List[str]]) -> bool:
                for slot in program_exams:
                    if not any(ex.upper() in user_exams_set for ex in slot):
                        return False
                return True

            programs = [prog for prog in programs if check_exams(prog.exams or [])]

        # Расчёт рейтинга
        # program_with_score = programs
        program_with_score = [
            (prog, compute_program_score(prog, filters)) for prog in programs
        ]
        program_with_score.sort(key=lambda x: x[1], reverse=True)

        # 5) Группируем по университетам
        grouped: Dict[str, Dict] = {}
        for prog, score in program_with_score:
            # for prog in program_with_score:
            uni = prog.university
            if uni.long_name not in grouped:
                grouped[uni.long_name] = {
                    "id": uni.id,
                    "long_name": uni.long_name,
                    "short_name": uni.short_name,
                    "geolocation": uni.geolocation,
                    "is_goverment": uni.is_goverment,
                    "rating": uni.rating,
                    "dormitory": uni.has_dormitory,
                    "army": uni.army,
                    "programs": [],
                }

            prog_dict = ProgramShortReturn.model_validate(prog).model_dump()

            prog_dict["ranking"] = score
            grouped[uni.long_name]["programs"].append(prog_dict)

        # 6) Сортируем университеты по максимальному рангу внутри
        grouped_list = list(grouped.values())
        grouped_list.sort(
            key=lambda x: (
                max(p["ranking"] for p in x["programs"]) if x["programs"] else 0
            ),
            reverse=True,
        )

        # 7) Пагинация
        offset = (filters.page - 1) * filters.page_size
        paginated_grouped_list = grouped_list[offset: offset + filters.page_size]

        return [
            UniversityProgramsReturn(
                **{
                    **v,
                    "programs": [
                        ProgramShortReturn.model_validate(prog)
                        for prog in v["programs"]
                    ],
                }
            )
            for v in paginated_grouped_list
        ]

        # for v in paginated_grouped_list:
        #     try:
        #         programs = [ProgramShortReturn.model_validate(prog) for prog in v["programs"]]
        #         university_data = {**v, "programs": programs}
        #         result.append(UniversityProgramsReturn(**university_data))
        #     except ValidationError as e:
        #         print(f"Ошибка валидации программ университета {v.get('long_name')}: {e}")
        #         continue  # Пропустить проблемный вуз
        # return result
