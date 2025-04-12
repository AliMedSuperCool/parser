from typing import Optional, List

from pydantic import BaseModel, Field

from shema.dormitory import DormitoryReturn
from shema.program import ProgramShortReturn


class UniversityScheme(BaseModel):
    long_name: Optional[str] = Field(None, description="Полное название вуза")
    short_name: Optional[str] = Field(None, description="короткое название вуза")

    class Config:
        from_attributes = True


class UniversityProgramsReturn(BaseModel):
    id: int
    long_name: str
    short_name: str
    geolocation: Optional[str]
    is_goverment: Optional[bool]
    rating: Optional[int]
    dormitory: Optional[bool]
    army: Optional[bool]
    programs: List[ProgramShortReturn]
    # phone_admission: Optional[List[str]]
    # email_admission: Optional[List[str]]

    class Config:
        from_attributes = True



