from fastapi import APIRouter
from .update import router as update_router
from .delete_profile_all import router as delete_router

router = APIRouter(
    prefix="/api/v1",
    tags=['Обновление профиля']
)


router.include_router(update_router)
router.include_router(delete_router)
