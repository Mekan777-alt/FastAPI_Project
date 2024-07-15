from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi_cache.decorator import cache

from firebase.config import get_firebase_user_from_token
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from models.config import get_session
from typing import Annotated
from sqlalchemy import select
from models.base import UK, ApartmentProfile, Object, News, NewsApartments
from .config import get_all_news, get_news_id
from firebase.notification import pred_send_notification
from api.routers.S3.main import S3Client
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

s3_client = S3Client(
    access_key=os.getenv("ACCESS_KEY_AWS"),
    secret_key=os.getenv("SECRET_KEY_AWS"),
    bucket_name=os.getenv("BUCKET_NAME"),
    endpoint_url=os.getenv("ENDPOINT_URL")
)


@router.get('/add-news')
@cache(expire=60)
async def get_news_info(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                        session: AsyncSession = Depends(get_session)):
    try:

        uk_uid = user['uid']

        uk_info = await session.scalar(select(UK).where(UK.uuid == uk_uid))

        if not uk_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='UK does not exist')
        objects_info = await session.scalars(select(Object).where(Object.uk_id == uk_info.id))

        apartment_name = []
        for object in objects_info:

            apartment_info = await session.scalars(select(ApartmentProfile)
                                                   .where(ApartmentProfile.object_id == object.id))
            for apartment in apartment_info:
                data = {
                    "id": str(apartment.id),
                    "name": apartment.apartment_name
                }
                apartment_name.append(data)
        all_user = {
            "id": 'all',
            "name": "All users"
        }
        apartment_name.append(all_user)

        return JSONResponse(content=apartment_name, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/add-news')
async def add_news_from_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                           name: str = Form(...),
                           description: str = Form(...),
                           photo: UploadFile = File(None),
                           apartment: str = Form(...),
                           session: AsyncSession = Depends(get_session)):
    try:

        uk_uid = user['uid']

        company_info = await session.scalar(select(UK).where(UK.uuid == uk_uid))

        if not company_info:
            return "Company not found"

        new_news = News(
            name=name,
            description=description,
            uk_id=company_info.id
        )
        session.add(new_news)
        await session.commit()

        if photo:

            photo.filename = photo.filename.lower()
            file_key = await s3_client.upload_file(photo, new_news.id, "news")

            new_news.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"
            await session.commit()

        if apartment == 'all':

            object_info = await session.scalars(select(Object).where(Object.uk_id == company_info.id))

            for object in object_info:

                apartments = await session.scalars(select(ApartmentProfile)
                                                   .where(ApartmentProfile.object_id == object.id))
                apartments_list = []
                for apart in apartments:
                    new_news_ = NewsApartments(
                        news_id=new_news.id,
                        apartment_id=apart.id
                    )
                    session.add(new_news_)
                    await session.commit()
                    apartments_list.append(new_news_.id)
                    await pred_send_notification(user, session, value='news',
                                                 title='News', body=description,
                                                 image=new_news.photo_path,
                                                 order_id=new_news.id, apartment_id=apartments_list)
        else:
            new_apartment = NewsApartments(
                apartment_id=int(apartment),
                news_id=new_news.id
            )
            session.add(new_apartment)

            await session.commit()
            await pred_send_notification(user, session, value='news',
                                         title='News', body=description, image=new_news.photo_path,
                                         order_id=new_news.id, apartment_id=int(apartment))

        return JSONResponse(content=new_news.to_dict(), status_code=status.HTTP_201_CREATED)

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get('/all-news')
@cache(expire=60)
async def get_all_news_from_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                               session: AsyncSession = Depends(get_session)):
    try:

        data = await get_all_news(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get('/all-news/{news_id}')
@cache(expire=60)
async def get_news_id_from_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                              news_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_news_id(session, user, news_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
