from fastapi import APIRouter
from .contact import router as contact_router
from .order_request import router as order_router
from .profile import router as profile_router
from .news import router as news_router
from .meters import router as meter_router
from .guest_pass import router as guest_pass_router
from .pay import router as pay_router

user_router = APIRouter(
    tags=['Client']
)

user_router.include_router(order_router)
user_router.include_router(profile_router)
user_router.include_router(contact_router)
user_router.include_router(news_router)
user_router.include_router(meter_router)
user_router.include_router(guest_pass_router)
user_router.include_router(pay_router)
