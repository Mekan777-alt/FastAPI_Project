from typing import Annotated
from fastapi import FastAPI, APIRouter, Depends
from config import get_firebase_user_from_token

router = APIRouter(
    prefix="/api/v1"
)


@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """gets the firebase connected user"""
    return {"id": user["uid"]}