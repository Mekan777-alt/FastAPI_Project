from fastapi import APIRouter
from .get_staff import router as get_staff_router
from .UK import router as uk_router
from .objects import router as objects_list_router
from .get_profile_uk import router as get_profile_uk_router

admin_router = APIRouter(
    tags=['Management Company']
)

admin_router.include_router(uk_router)
admin_router.include_router(get_staff_router)
admin_router.include_router(objects_list_router)
admin_router.include_router(get_profile_uk_router)
