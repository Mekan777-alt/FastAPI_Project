from fastapi import APIRouter
from .contact import router as contact_router
from .order_request import router as order_router
from .profile import router as profile_router
from .news import router as news_router

user_router = APIRouter(
    prefix="/api/v1"
)

user_router.include_router(order_router)
user_router.include_router(profile_router)
user_router.include_router(contact_router)
user_router.include_router(news_router)
