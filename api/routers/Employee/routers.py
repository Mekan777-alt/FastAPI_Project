from fastapi import APIRouter
from .apartments import router as apartment_router

router = APIRouter(
    tags=['Employee']
)

router.include_router(apartment_router)
