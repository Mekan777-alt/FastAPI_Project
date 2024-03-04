from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from config import get_session
from firebase.config import get_firebase_user_from_token

router = APIRouter(
    prefix='/api/v1'
)


@router.post("/create_object")
async def create_object(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                        session: AsyncSession = Depends(get_session)):
    try:

        pass

    except Exception as e:
        pass
