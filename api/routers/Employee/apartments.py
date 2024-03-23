from fastapi import APIRouter, Depends
from firebase.config import get_firebase_user_from_token
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from starlette import status
from api.routers.Employee.config import get_employee_profile
from starlette.responses import JSONResponse


router = APIRouter(
    prefix="/api/v1/employee"
)


@router.get("/apartments")
async def get_apartments_employee(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                    session: AsyncSession = Depends(get_session)):

    try:

        pass

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))