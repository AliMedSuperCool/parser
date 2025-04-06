from typing import Optional

from pydantic import BaseModel, Field, model_validator


class UniversityShema(BaseModel):
    scores: Optional[float] = None
    direction: Optional[str] = None
    education_form: Optional[str] = None
    is_paid: Optional[bool] = None  # Платное или бесплатное обучение (True - платное, False - бесплатное)
    is_government: Optional[bool] = None  # Гос/не гос вуз (True - государственный, False - негосударственный)
    region: Optional[str] = None  # Регион (например, "Московская область", "Нижегородская область" и т.д.)
    price: Optional[float] = None  # Регион (например, "Московская область", "Нижегородская область" и т.д.)

    class Config:
        from_attributes = True


# class TaskShema(BaseModel):
#     id: int = Field(include=False, default=None)
#     name: str | None = None
#     pomodoro_count: int | None = None
#     category_id: int
#     user_id: int
#
#     class Config:
#         from_attributes = True
#
#     @model_validator(mode="after")
#     def check_name_or_count(self):
#         if self.name is None and self.pomodoro_count is None:
#             raise ValueError("Task name or pomodoro count must be set")
#         return self
#
#
# class TaskCreateShema(BaseModel):
#     name: str | None = None
#     pomodoro_count: int | None = None
#     category_id: int = Field(alias='category_id')
