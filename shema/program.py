from typing import Optional, List, Dict, Literal

from fastapi import Query
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


