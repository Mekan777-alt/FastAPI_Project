from fastapi import APIRouter

from .UK import router as uk_router


admin_router = APIRouter(
    prefix='/api/v1'
)

admin_router.include_router(uk_router)