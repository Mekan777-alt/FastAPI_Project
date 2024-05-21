from fastapi import APIRouter, HTTPException, Depends
from config import get_session
from firebase.config import get_firebase_user_from_token
from typing import Annotated
from starlette.responses import JSONResponse
from starlette import status
from models.base import NotificationUK, UK
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get('/notifications')
async def get_notifications(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                            session: AsyncSession = Depends(get_session)):
    try:

        company_uid = user['uid']

        company_info = await session.scalar(select(UK).where(UK.uuid == company_uid))

        if not company_info:

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')

        notifications = await session.scalars(select(NotificationUK).where(NotificationUK.uk_id == company_info.id))

        notification_list = []

        for notification in notifications:
            notification_list.append(notification.to_dict())

        return JSONResponse(content=notification_list, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
