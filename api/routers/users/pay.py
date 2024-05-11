from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token
from config import get_session
from starlette import status
from .config import get_finance_from_user
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('/pay')
async def get_pay(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                  session: AsyncSession = Depends(get_session)):
    try:

        data = await get_finance_from_user(session, user)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)
