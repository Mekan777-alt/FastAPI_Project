from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse
from starlette import status
from typing import Annotated
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_session
from api.routers.users.config import get_user_meters

router = APIRouter()


@router.get("/meters")
async def get_meters(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     session: AsyncSession = Depends(get_session)):
    try:

        user = await get_user_meters(session, user['uid'])

        return JSONResponse(content=user, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(content=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/meters/{meter_id}")
async def get_meter_id(meter_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       session: AsyncSession = Depends(get_session)):

    try:

        pass

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    