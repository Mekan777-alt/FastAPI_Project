from fastapi import APIRouter
from .get_staff import router as get_staff
from .UK import router as uk_router


admin_router = APIRouter(
    prefix='/api/v1'
)

admin_router.include_router(uk_router)
admin_router.include_router(get_staff)
