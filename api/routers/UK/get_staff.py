from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token, get_user
from config import get_session

router = APIRouter(
    prefix="/api/v1"
)


@router.get("/get_staff")
async def get_staff(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                    session: AsyncSession = Depends(get_session)):
    staff = await get_user(user, session)
    try:

        pass

    except Exception as e:

        pass