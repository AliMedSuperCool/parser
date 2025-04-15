from typing import Optional, List, Literal

from fastapi import Query
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




class UniversityFilterParams(BaseModel):
    # university: Optional[UniversityScheme] = Field(None, description="Вуз")
    long_name: Optional[str] = Field(None, description="Вуз полное название",
                                     examples=['Курская академия государственной и муниципальной службы'])
    short_name: Optional[str] = Field(None, description="Вуз короткое название", examples=['КАГМС'])

    direction: Optional[str] = Field(None, description="Направление", examples=['Экономика'])
    education_form: Optional[Literal["Очная", "Заочная", "Очно-заочная"]] = Field(None,
                                                                                  description="Форма обучения",
                                                                                  examples=['очная', 'заочная',
                                                                                            'очно-заочная'])
    is_free: Optional[bool] = Field(None, description="Только бесплатные места")
    user_score: Optional[int] = Field(None, description="Балл пользователя")
    max_price: Optional[int] = Field(None, description="Максимальная цена (отрицательная):")
    is_goverment: Optional[bool] = Field(None, description="Гос или не гос")
    region: Optional[str] = Field(None, description="Регион (по university.geolocation)")
    user_exams: Optional[List[str]] = Field(None, description="Список экзаменов пользователя",
                                            examples=["РЯ", "Х", "Б"])
    has_dormitory: Optional[bool] = Field(None, description="Наличие общежития")
    has_army: Optional[bool] = Field(None, description="Наличие военной кафедры")

    page_size: int = Field(5, ge=1, le=50, description="Сколько программ вернуть")
    page: int = Field(1, ge=1, description="Пропустить программ")

    class Config:
        from_attributes = True



def get_filter_params(
    long_name: Optional[str] = Query(None),
    short_name: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    education_form: Optional[Literal["Очная", "Заочная", "Очно-заочная"]] = Query(None),
    is_free: Optional[bool] = Query(None),
    user_score: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    is_goverment: Optional[bool] = Query(None),
    region: Optional[str] = Query(None),
    user_exams: Optional[List[str]] = Query(None),
    has_dormitory: Optional[bool] = Query(None),
    has_army: Optional[bool] = Query(None),
    page_size: int = Query(5, ge=1, le=50),
    page: int = Query(1, ge=1),
) -> UniversityFilterParams:
    return UniversityFilterParams(
        long_name=long_name,
        short_name=short_name,
        direction=direction,
        education_form=education_form,
        is_free=is_free,
        user_score=user_score,
        max_price=max_price,
        is_goverment=is_goverment,
        region=region,
        user_exams=user_exams,
        has_dormitory=has_dormitory,
        has_army=has_army,
        page_size=page_size,
        page=page,
    )