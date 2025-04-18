import hashlib
import json

from redis import Redis

from shema import ProgramShortReturn
from shema.university import UniversityProgramsReturn


# class UniversityCache:
#     def __init__(self, redis: Redis):
#         self.redis = redis
#
#     def get_university(self) -> list[UniversityProgramsReturn]:
#         with self.redis as redis:
#             universities_json = redis.lrange('university', 0, -1)
#             result = []
#             for university in universities_json:
#                 programs = [ProgramShortReturn.model_validate(prog) for prog in university["programs"]]
#                 university_data = {**university, "programs": programs}
#                 result.append(UniversityProgramsReturn(**university_data))
#             return result
#
#     def set_university(self, universities: list[UniversityProgramsReturn]):
#         universities_json = [university.json() for university in universities]
#         with self.redis as redis:
#             redis.lpush("university", *universities_json)
#             redis.expire("university", 3600)


class UniversityCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _make_key(self, filters: dict) -> str:
        filters_json = json.dumps(filters, sort_keys=True)
        return f"university:{hashlib.md5(filters_json.encode()).hexdigest()}"

    def get_university(self, filters: dict) -> list[UniversityProgramsReturn] | None:
        key = self._make_key(filters)
        with self.redis as redis:
            universities_json = redis.lrange(key, 0, -1)
            if not universities_json:
                return None
            return [UniversityProgramsReturn.model_validate(json.loads(u)) for u in universities_json]


    def set_university(self, filters: dict, universities: list[UniversityProgramsReturn], ttl: int = 60):
        key = self._make_key(filters)
        universities_json = [u.model_dump_json() for u in universities]  # ✅ model_dump_json
        with self.redis as redis:
            redis.lpush(key, *universities_json)
            redis.expire(key, ttl)
