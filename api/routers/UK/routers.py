from fastapi import APIRouter
from .get_staff import router as get_staff_router
from .objects import router as objects_list_router
from .get_profile_uk import router as get_profile_uk_router
from .create_staff import router as create_staff_router
from .news import router as news_router
from .notification import router as notification_router

admin_router = APIRouter(
    prefix='/api/v1',
    tags=['Company']
)

admin_router.include_router(get_staff_router)
admin_router.include_router(objects_list_router)
admin_router.include_router(get_profile_uk_router)
admin_router.include_router(create_staff_router)
admin_router.include_router(news_router)
admin_router.include_router(notification_router)
