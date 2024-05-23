from fastapi import APIRouter
from .apartments import router as apartment_router
from .employee import router as employee_router_
from .executors import router as executors_router
from .notification import router as notification_router

employee_router = APIRouter(
    tags=['Employee']
)

employee_router.include_router(apartment_router)
employee_router.include_router(employee_router_)
employee_router.include_router(executors_router)
employee_router.include_router(notification_router)
