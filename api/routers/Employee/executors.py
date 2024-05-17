from fastapi import APIRouter, Depends, Form, UploadFile, File
from config import get_session
from typing import Annotated
from starlette.responses import JSONResponse
from starlette import status
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.Employee.config import get_executors_list, get_executors_detail


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
async def add_executor(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       first_name: str = Form(...),
                       last_name: str = Form(...),
                       specialization: str = Form(...),
                       phone_number: str = Form(...),
                       email: str = Form(...),
                       recipient_name: str = Form(...),
                       account: str = Form(...),
                       contact_number: str = Form(...),
                       purpose_of_payment: str = Form(...),
                       bic: str = Form(...),
                       correspondent_account: str = Form(...),
                       bank_name: str = Form(...),
                       inn: str = Form(...),
                       kpp: str = Form(...),
                       session: AsyncSession = Depends(get_session)):
    try:

        pass


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