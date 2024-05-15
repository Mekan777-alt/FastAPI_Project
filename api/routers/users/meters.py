from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse
from starlette import status
from typing import Annotated
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_session
from sqlalchemy import select
from models.base import Meters, MeterService
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

        meter = await session.scalar(select(Meters).where(Meters.id == meter_id))
        meter_service = await session.scalar(select(MeterService).where(MeterService.id == meter.meter_service_id))

        data = {
            "id": meter.id,
            "name": meter_service.name,
            "icon_path": meter_service.big_icons_path if meter_service.big_icons_path else None,
            "comment": meter.comment if meter.comment else None,
            "status": meter.status,
            "meter_readings": meter.meter_readings
        }

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    