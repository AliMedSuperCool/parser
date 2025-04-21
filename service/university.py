from dataclasses import dataclass
from typing import Dict

from pydantic import ValidationError

from exception import UniversitiesNotFound
from models import Program
from repository import UniversityRepository, UniversityCache
from shema import UniversityFilterParams, UniversityProgramsReturn, \
    ProgramShortReturn
from service.utils_calibration import compute_program_score


# logger = logging.getLogger(__name__)


@dataclass
class UniversityService:
    university_repository: UniversityRepository
    university_cache: UniversityCache

    # task_cache: UniversityCache
    # auth_service: AuthService

    # def create_university(self, username: str, password: str) -> UniversitySchema:
    #     user = self.university_repository.create_university(
    #         UniversityCreateSchema(username=username, password=password))
    #     # access_token = self.auth_service.generate_token(user_id=user.id)
    #     return UniversitySchema(university_id=user.id, access_token=access_token)

    def filtering(self, filters: UniversityFilterParams) -> list[UniversityProgramsReturn]:
        no_filters_applied = not any(
            getattr(filters, f) is not None
            for f in filters.model_fields
            if f not in {"page", "page_size"}
        )

        if no_filters_applied:
            filters.region = "Москва"
            filters.is_free = True
            filters.has_army = True

        filters_dict = filters.model_dump()

        # Пробуем получить из кэша
        cached = self.university_cache.get_university(filters_dict)
        if cached:
            return cached

        programs = self.university_repository.filtering(filters)
        if not programs:
            raise UniversitiesNotFound

        if filters.user_exams:
            self.user_exams_set = set([e.strip().upper() for e in filters.user_exams])
            programs = list(filter(self.__exams_match, programs))

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

        result = []

        for v in paginated_grouped_list:
            try:
                programs = [ProgramShortReturn.model_validate(prog) for prog in v["programs"]]
                university_data = {**v, "programs": programs}
                result.append(UniversityProgramsReturn(**university_data))
            except ValidationError as e:
                # logger.warning(f"Ошибка валидации программ университета {v.get('short_name')}: {e}")
                print(f"Ошибка валидации программ университета {v.get('short_name')}: {e}")
                continue  # Пропустить проблемный вуз

        self.university_cache.set_university(filters_dict, result, ttl=3600)
        return result

    def __exams_match(self, program: Program) -> bool:
        exams = program.exams or []
        return all(
            any(exam.strip().upper() in self.user_exams_set for exam in slot)
            for slot in exams
        )
