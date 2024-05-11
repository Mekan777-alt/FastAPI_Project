from fastapi import APIRouter, Depends
from typing import Annotated
from starlette import status
from starlette.responses import JSONResponse
from api.routers.UK.config import get_staff_uk, get_staff_uk_id, get_staff_delete_list, get_staff_delete
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token
from config import get_session
from schemas.uk.get_staff import StaffList, StaffInfo, StaffDeleteList

router = APIRouter()


@router.get("/get_staff_uk", response_model=StaffList)
async def get_staff(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                    session: AsyncSession = Depends(get_session)):
    try:

        data = await get_staff_uk(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/get_staff_uk/staff_info/{staff_id}", response_model=StaffInfo)
async def get_staff(staff_id: int, session: AsyncSession = Depends(get_session)):

    try:

        data = await get_staff_uk_id(session, staff_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e)


@router.get("/get_staff_uk/delete", response_model=StaffDeleteList)
async def delete_staff(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       session: AsyncSession = Depends(get_session)):
    try:

        data = await get_staff_delete_list(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)
    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.delete("/get_staff_uk/delete/{staff_id}", response_model=StaffDeleteList)
async def delete_staff(staff_id: int, session: AsyncSession = Depends(get_session)):
    try:

        await get_staff_delete(session, staff_id)

        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={
            "message": f"Staff {staff_id} deleted successfully"})

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
