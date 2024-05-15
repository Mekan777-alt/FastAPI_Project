from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from firebase.config import get_firebase_user_from_token
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from config import get_session
from typing import Annotated
from sqlalchemy import select
from models.base import UK, ApartmentProfile, Object
from .config import get_all_news, get_news_id

router = APIRouter()


@router.get('/add-news')
async def get_news_info(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                        session: AsyncSession = Depends(get_session)):
    try:

        uk_uid = user['uid']

        uk_info = await session.scalar(select(UK).where(UK.uuid == uk_uid))

        objects_info = await session.scalars(select(Object).where(Object.uk_id == uk_info.id))

        apartment_name = []
        for object in objects_info:

            apartment_info = await session.scalars(select(ApartmentProfile)
                                                  .where(ApartmentProfile.object_id == object.id))
            for apartment in apartment_info:

                data = {
                    "id": apartment.id,
                    "name": apartment.apartment_name
                }
                apartment_name.append(data)

        return JSONResponse(content=apartment_name, status_code=status.HTTP_200_OK)


    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/add-news')
async def add_news_from_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                           session: AsyncSession = Depends(get_session)):
    try:

        pass


    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


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
