from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from dependecy import get_university_service
from exception import UniversitiesNotFound
from service import UniversityService
from shema import UniversityFilterParams, UniversityProgramsReturn, get_filter_params

router = APIRouter(prefix="/university", tags=["university"])


@router.post("/university-filtering", response_model=List[UniversityProgramsReturn])
async def get_tasks(
        university_service: Annotated[UniversityService, Depends(get_university_service)],
        filters: UniversityFilterParams = Depends(get_filter_params),
):
    try:
        return university_service.filtering(filters)
    except UniversitiesNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
