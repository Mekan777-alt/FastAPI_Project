from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from firebase_admin import firestore
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Annotated
from firebase.config import get_firebase_user_from_token
from starlette.responses import JSONResponse
from models.config import get_session
from models.base import News, TenantProfile, TenantApartments, ApartmentProfile, NewsApartments, NotificationTenants

router = APIRouter()


@router.get('/all-news')
@cache(expire=60)
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

        news_apartment = await session.scalars(select(News).
                                               join(NewsApartments).
                                               where(NewsApartments.apartment_id == apartment_info.id).
                                               order_by(News.created_at.desc()))

        news_list = [news.to_dict() for news in news_apartment]

        return JSONResponse(content=news_list, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(detail={'detail': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/all-news/{news_id}')
@cache(expire=60)
async def get_news_id(user: Annotated[dict, Depends(get_firebase_user_from_token)], news_id: int,
                      session: AsyncSession = Depends(get_session)):
    try:

        tenant_uid = user['uid']

        tenant_info = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == tenant_uid))

        if not tenant_info:
            return JSONResponse(content="User not found", status_code=status.HTTP_404_NOT_FOUND)

        news = await session.scalar(select(News).where(News.id == news_id))

        db = firestore.client()
        query = db.collection('notifications').where('id', '==', f'{news_id}')

        result = query.stream()

        for doc in result:

            data = doc.to_dict()

            if data['screen'] == 'news':
                db.collection("notifications").document(doc.id).set({"is_view": {"client": True}}, merge=True)

        local_notify = await session.scalar(select(NotificationTenants)
                                            .where(NotificationTenants.content_id == news_id))
        if not local_notify:

            print(f"Notification not found")

        local_notify.is_view = True
        await session.commit()

        return JSONResponse(content=news.to_dict(), status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
