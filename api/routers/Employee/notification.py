from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache

from models.config import get_session
from firebase.config import get_firebase_user_from_token
from typing import Annotated
from starlette.responses import JSONResponse
from starlette import status
from models.base import NotificationEmployee, EmployeeUK
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix='/api/v1/employee'
)


@router.get('/notifications')
@cache(expire=60)
async def get_notifications(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                            session: AsyncSession = Depends(get_session)):
    try:

        employee_uid = user['uid']

        employee_info = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee_uid))

        if not employee_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Employee not found')

        notifications = await session.scalars(select(NotificationEmployee)
                                              .where(NotificationEmployee.employee_id == employee_info.id))

        if notifications is None:
            return JSONResponse(content=[], status_code=status.HTTP_200_OK)

        notification_list = []

        for notification in notifications:
            if notification.apartment_id is None:
                notification.apartment_id = 0
                await session.commit()
            notification_list.append(notification.to_dict())

        return JSONResponse(content=notification_list, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
