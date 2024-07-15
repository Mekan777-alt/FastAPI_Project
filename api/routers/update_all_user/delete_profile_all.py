from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from firebase.config import get_firebase_user_from_token, delete_staff_firebase
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from starlette import status
from models.config import get_session
from starlette.responses import JSONResponse
from models.base import TenantProfile, UK, EmployeeUK

router = APIRouter()


@router.delete("/delete-profile")
async def delete_profile(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                         session: AsyncSession = Depends(get_session)):

    try:

        current_user_uid = user['uid']

        client = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == current_user_uid))

        if client:

            delete_from_firebase_client = await delete_staff_firebase(current_user_uid)

            if delete_from_firebase_client:

                await session.delete(client)
                await session.commit()

            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Profile deleted"})

        employee = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == current_user_uid))

        if employee:

            delete_from_firebase_employee = await delete_staff_firebase(current_user_uid)

            if delete_from_firebase_employee:

                await session.delete(employee)
                await session.commit()

            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Profile deleted"})

        uk = await session.scalar(select(UK).where(UK.uuid == current_user_uid))

        if uk:

            delete_from_firebase_uk = await delete_staff_firebase(current_user_uid)

            if delete_from_firebase_uk:

                await session.delete(uk)
                await session.commit()

            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Profile deleted"})

        else:

            return JSONResponse(content="User not found", status_code=status.HTTP_404_NOT_FOUND)
    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))