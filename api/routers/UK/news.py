from fastapi import APIRouter, Depends, HTTPException
from firebase.config import get_firebase_user_from_token
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from config import get_session
from typing import Annotated
from .config import get_all_news, get_news_id

router = APIRouter()


@router.get('/all-news')
async def get_all_news_from_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                               session: AsyncSession = Depends(get_session)):
    try:

        data = await get_all_news(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get('/all-news/{news_id}')
async def get_news_id_from_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                              news_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_news_id(session, user, news_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
