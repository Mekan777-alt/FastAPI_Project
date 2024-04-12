from fastapi import APIRouter
from .manager import router as ws_chat_router


chat_router = APIRouter(
    tags=["Chat"],
    prefix="/api/v1"
)


chat_router.include_router(ws_chat_router)
