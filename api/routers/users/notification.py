from fastapi import APIRouter, HTTPException, Depends
from config import get_session
from typing import Annotated
from starlette import status
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token


router = APIRouter()


@router.get("/notifications")
async def get_notifications_from_user(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                      session: AsyncSession = Depends(get_session)):
    try:

        pass


    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))