from fastapi import APIRouter, HTTPException, Depends
from config import get_session
from typing import Annotated
from starlette import status
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token
from models.base import TenantProfile, NotificationTenants
from sqlalchemy import select

router = APIRouter()


@router.get("/notifications")
async def get_notifications_from_user(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                      session: AsyncSession = Depends(get_session)):
    try:

        user_uid = user['uid']

        tenant_info = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user_uid))

        if not tenant_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')

        notifications = await session.scalars(select(NotificationTenants)
                                              .where(NotificationTenants.tenant_id == tenant_info.id))

        notification_list = []

        for notification in notifications:
            notification_list.append(notification.to_dict())

        return JSONResponse(content=notification_list, status_code=status.HTTP_200_OK)

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))

