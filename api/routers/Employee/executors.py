from fastapi import APIRouter, Depends, Form, UploadFile, File
from fastapi_cache.decorator import cache

from models.config import get_session
from typing import Annotated
from starlette.responses import JSONResponse
from starlette import status
from models.base import ExecutorsProfile, EmployeeUK, BankDetailExecutors, UK
from sqlalchemy import select
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.Employee.config import get_executors_list, get_executors_detail
from schemas.employee.add_executor import AddExecutor
from api.routers.S3.main import S3Client
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(
    prefix='/api/v1'
)

s3_client = S3Client(
    access_key=os.getenv("ACCESS_KEY_AWS"),
    secret_key=os.getenv("SECRET_KEY_AWS"),
    bucket_name=os.getenv("BUCKET_NAME"),
    endpoint_url=os.getenv("ENDPOINT_URL")
)


@router.get("/employee/executors")
@cache(expire=60)
async def get_employee_executors(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                 session: AsyncSession = Depends(get_session)):
    try:

        data = await get_executors_list(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/employee/executors/add_executor")
async def add_executor(user: Annotated[dict, Depends(get_firebase_user_from_token)], request: AddExecutor,
                       session: AsyncSession = Depends(get_session)):
    try:

        uk_id = 0

        uid = user["uid"]

        employee_data = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == uid))

        uk_data = await session.scalar(select(UK).where(UK.uuid == uid))

        if employee_data:

            uk_id = employee_data.uk_id

        elif uk_data:

            uk_id = uk_data.id

        bank_detail_executors = BankDetailExecutors(
            bank_name=request.bank_name,
            inn=request.inn,
            kpp=request.kpp,
            contact_number=request.contact_number,
            correspondent_account=request.correspondent_account,
            purpose_of_payment=request.purpose_of_payment,
            bic=request.bic,
            recipient_name=request.recipient_name,
            account=request.account,
        )
        session.add(bank_detail_executors)
        await session.commit()

        new_employee_db = ExecutorsProfile(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone_number=request.phone_number,
            specialization=request.specialization,
            uk_id=uk_id,
            bank_details_id=bank_detail_executors.id
        )
        session.add(new_employee_db)
        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_employee_db.to_dict())

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/employee/executors/{executor_id}")
@cache(expire=60)
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

        executor = await session.scalar(select(ExecutorsProfile).where(ExecutorsProfile.id == executor_id))

        file_key = await s3_client.upload_file(photo, executor.id, "executors")
        executor.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"
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
