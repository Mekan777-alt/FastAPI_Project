from fastapi import APIRouter, HTTPException, Depends
from config import get_session
from firebase.config import get_firebase_user_from_token
from typing import Annotated
from starlette.responses import JSONResponse
from starlette import status
from models.base import NotificationEmployee, EmployeeUK
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix='/api/v1'
)


@router.get('/notifications')
async def get_notifications(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                            session: AsyncSession = Depends(get_session)):
    try:

        employee_uid = user['uid']

        employee_info = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee_uid))

        if not employee_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')

        notifications = await session.scalars(select(NotificationEmployee)
                                              .where(NotificationEmployee.object_id == employee_info.object_id))

        notification_list = []

        for notification in notifications:
            notification_list.append(notification.to_dict())

        return JSONResponse(content=notification_list, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/notifications/{notification_id}')
async def get_notification_id(notification_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                              session: AsyncSession = Depends(get_session)):
    try:
        notification = await session.scalar(select(NotificationEmployee)
                                            .where(NotificationEmployee.id == notification_id))

        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Notification not found')

        return notification.to_dict()

    except HTTPException as e:

        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
