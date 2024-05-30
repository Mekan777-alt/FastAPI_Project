from fastapi import APIRouter
from .update import router as update_router

router = APIRouter(
    prefix="/api/v1",
    tags=['Обновление профиля']
)


router.include_router(update_router)
