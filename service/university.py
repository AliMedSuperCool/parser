import string
from dataclasses import dataclass
from random import random, choice

from pydantic import ValidationError

from repository import UserRepository

from shema import UserLoginSchema, UserCreateSchema, UniversityFilterParams, UniversityProgramsReturn, \
    ProgramShortReturn

# logger = logging.getLogger(__name__)


@dataclass
class UniversityService:
    user_repository: UserRepository
    task_cache: UniversityCache

    # auth_service: AuthService

    def create_university(self, username: str, password: str) -> UniversitySchema:
        user = self.university_repository.create_university(
            UniversityCreateSchema(username=username, password=password))
        # access_token = self.auth_service.generate_token(user_id=user.id)
        return UniversitySchema(university_id=user.id, access_token=access_token)

    def filtering(self, filters: UniversityFilterParams) -> list[UniversityProgramsReturn]:
        raw_universities = self.university_repository.filtering(filters)
        result = []

        for v in raw_universities:
            try:
                programs = [ProgramShortReturn.model_validate(prog) for prog in v["programs"]]
                university_data = {**v, "programs": programs}
                result.append(UniversityProgramsReturn(**university_data))
            except ValidationError as e:
                # logger.warning(f"Ошибка валидации программ университета {v.get('short_name')}: {e}")
                print(f"Ошибка валидации программ университета {v.get('short_name')}: {e}")
                continue  # Пропустить проблемный вуз

        return result
