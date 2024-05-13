from fastapi import APIRouter, Depends, File, UploadFile
from config import get_session
from typing import Annotated
from starlette.responses import JSONResponse
from starlette import status
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.Employee.config import get_employee_info
import shutil
from sqlalchemy.future import select
from models.base import EmployeeUK

router = APIRouter(
    prefix='/api/v1'
)


@router.get("/employee_info")
async def employee_info(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                        session: AsyncSession = Depends(get_session)):

    try:

        data = await get_employee_info(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/employee_info/add_photo")
async def add_photo_employee(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                             session: AsyncSession = Depends(get_session), photo: UploadFile = File(...)):

    try:

        photo.filename = photo.filename.lower()
        path = f'static/photo/employee/{photo.filename}'

        with open(path, "wb+") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        employee_id = user["uid"]

        employee = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee_id))

        employee.photo_path = path
        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"photo_path": employee.photo_path})

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
