from fastapi import APIRouter, Depends
from typing import Annotated
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token

router = APIRouter(
    prefix='/api/v1'
)


@router.get("/add_employee_uk")
async def create_staff(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       session: AsyncSession = Depends(get_session)):
    pass


@router.post('/add_employee_uk/{obj_id}')
async def create_employee_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                             session: AsyncSession = Depends(get_session)):
    try:

        pass

    except Exception as e:

        pass
