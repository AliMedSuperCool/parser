from typing import Optional, List, Dict, Literal

from pydantic import BaseModel, Field


class FormReturn(BaseModel):
    education_form2: str
    score: Optional[int]
    price: Optional[int]
    olympic: Optional[str]
    free_places: Optional[int]
    average_score: Optional[int]


    class Config:
        from_attributes = True


class ProgramShortReturn(BaseModel):
    id: int
    direction: str
    profile: str
    program_code: str
    faculty: str
    exams: Optional[List[List[str]]] = None
    forms: List[FormReturn]  # Включает баллы, цену, форму обучения

    class Config:
        from_attributes = True


class ProgramFilterParams(BaseModel):
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
