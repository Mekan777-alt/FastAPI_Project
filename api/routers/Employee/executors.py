from fastapi import APIRouter, Depends, Form, UploadFile, File
from config import get_session
from typing import Annotated
from starlette.responses import JSONResponse
from starlette import status
from models.base import ExecutorsProfile, EmployeeUK, BankDetailExecutors
from sqlalchemy import select
from firebase.config import get_firebase_user_from_token, delete_staff_firebase
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.Employee.config import get_executors_list, get_executors_detail
from firebase_admin import auth, firestore
from schemas.employee.add_executor import AddExecutor
import shutil

router = APIRouter(
    prefix='/api/v1'
)


@router.get("/employee/executors")
async def get_employee_executors(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                 session: AsyncSession = Depends(get_session)):
    try:

        data = await get_executors_list(session)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/employee/executors/add_executor")
async def add_executor(user: Annotated[dict, Depends(get_firebase_user_from_token)], request: AddExecutor,
                       session: AsyncSession = Depends(get_session)):
    try:

        employee_uid = user["uid"]

        employee_data = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee_uid))

        if not employee_data:
            return "Employee not found"

        bank_detail_executors = BankDetailExecutors(
            bank_name=request.bank_name,
            inn=request.inn,
            kpp=request.kpp,
            contact_number=request.contact_number,
            correspondent_account=request.correspondent_account,
            purpose_of_payment=request.purpose_of_payment,
            bic=request.bic,
            recipient_name=request.recipient_name,
            account=request.account
        )
        session.add(bank_detail_executors)
        await session.commit()

        new_employee_db = ExecutorsProfile(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone_number=request.phone_number,
            specialization=request.specialization,
            uk_id=employee_data.uk_id,
            bank_details_id=bank_detail_executors.id
        )
        session.add(new_employee_db)
        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_employee_db.to_dict())

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/employee/executors/{executor_id}")
async def get_executor_id(executor_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                          session: AsyncSession = Depends(get_session)):
    try:

        data = await get_executors_detail(session, executor_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/employee/executors/{executor_id}/add_photo")
async def add_photo_for_executor(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                 executor_id: int,
                                 photo: UploadFile = File(...),
                                 session: AsyncSession = Depends(get_session)):
    try:
        photo.filename = photo.filename.lower()
        path = f'/FastAPI_Project/static/photo/{photo.filename}'

        with open(path, "wb+") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        executor = await session.scalar(select(ExecutorsProfile).where(ExecutorsProfile.id == executor_id))

        executor.photo_path = f"http://217.25.95.113:8000/static/photo/{photo.filename}"
        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"photo_path": executor.photo_path})

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.delete("/employee/executors/{executor_id}/delete")
async def delete_executor(user: Annotated[dict, Depends(get_firebase_user_from_token)], executor_id: int,
                          session: AsyncSession = Depends(get_session)):
    try:

        executor_data = await session.scalar(select(ExecutorsProfile).where(ExecutorsProfile.id == executor_id))
        if not executor_data:
            return "Executor not found"

        await session.delete(executor_data)
        await session.commit()

        return {"message": "Deleted successfully"}

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
