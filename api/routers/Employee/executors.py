from fastapi import APIRouter, Depends
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


@router.get("/employee/executors/{executor_id}")
async def get_executor_id(executor_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                          session: AsyncSession = Depends(get_session)):

    try:

        data = await get_executors_detail(session, executor_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))