from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from starlette.responses import JSONResponse
from starlette import status
from typing import Annotated
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from models.config import get_session
from sqlalchemy import select
from models.base import Meters, MeterService, TenantProfile, TenantApartments, ApartmentProfile
from api.routers.users.config import get_user_meters

router = APIRouter()


@router.get("/meters")
@cache(expire=60)
async def get_meters(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     session: AsyncSession = Depends(get_session)):
    try:

        user = await get_user_meters(session, user['uid'])

        return JSONResponse(content=user, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(content=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/meters/{meter_id}")
@cache(expire=60)
async def get_meter_id(meter_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       session: AsyncSession = Depends(get_session)):

    try:

        meter = await session.scalar(select(Meters).where(Meters.id == meter_id))
        meter_service = await session.scalar(select(MeterService).where(MeterService.id == meter.meter_service_id))

        user_info = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user['uid']))

        if not user_info:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

        apartment = await session.scalar(select(TenantApartments).where(TenantApartments.tenant_id == user_info.id))
        apartment_info = await session.scalar(
            select(ApartmentProfile).where(ApartmentProfile.id == apartment.apartment_id))

        data = {
            "id": meter.id,
            "service_name": meter_service.name,
            "apartment_name": apartment_info.apartment_name,
            "icon_path": meter_service.big_icons_path if meter_service.big_icons_path
            else meter_service.mini_icons_path,
            "comment": meter.comment if meter.comment else None,
            "status": meter.status,
            "amount": 0,
            "meter_readings": meter.meter_readings
        }

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    