import math

from typing import Optional, Union

from pydantic import BaseModel, validator, Field


class DormitoryReturn(BaseModel):
    dormitory: bool = Field(description="Наличие общежития")
    # info: Optional[str] = Field(None, description="Информация об общежитии")
    # rating: Optional[Union[float, str]] = Field(None, description="Рейтинг общежития")
    #
    # @validator("rating", pre=True)
    # def replace_nan_with_none(cls, v):
    #     if isinstance(v, float) and math.isnan(v):
    #         return None
    #     return v

    class Config:
        from_attributes = True
        allow_inf_nan = True
