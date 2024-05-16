from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Annotated
from firebase.config import get_firebase_user_from_token
from starlette.responses import JSONResponse
from config import get_session
from models.base import News, TenantProfile, TenantApartments, Object, UK, ApartmentProfile, NewsApartments

router = APIRouter()


@router.get('/all-news')
async def get_news(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                   session: AsyncSession = Depends(get_session)):
    try:

        user_uid = user['uid']

        user_info = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user_uid))

        if not user_info:
            return JSONResponse(content="User not found", status_code=status.HTTP_404_NOT_FOUND)

        apartment_tenant = await session.scalar(select(TenantApartments).
                                                where(TenantApartments.tenant_id == user_info.id))

        apartment_info = await session.scalar(select(ApartmentProfile)
                                              .where(ApartmentProfile.id == apartment_tenant.apartment_id))

        news_apartment = await session.scalars(select(NewsApartments)
                                               .where(NewsApartments.apartment_id == apartment_info.id))

        news_list = []
        for n in news_apartment:
            news = await session.scalar(select(News).where(News.id == n.news_id))

            news_list.append(news.to_dict())

        return JSONResponse(content=news_list, status_code=status.HTTP_200_OK)

    except Exception as e:

        raise HTTPException(detail={'detail': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/all-news/{news_id}')
async def get_news_id(user: Annotated[dict, Depends(get_firebase_user_from_token)], news_id: int,
                      session: AsyncSession = Depends(get_session)):
    try:

        news = await session.scalar(select(News).where(News.id == news_id))

        return JSONResponse(content=news.to_dict(), status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
