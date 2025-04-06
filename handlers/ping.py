from fastapi import APIRouter

router = APIRouter(prefix="/ping", tags=["ping-app, ping-db"])


@router.get("/db")
async def ping_db():
    return {"message": "ok"}


@router.get("/app")
async def ping_app():
    return {"message": "app is working"}


