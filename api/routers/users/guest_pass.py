from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from api.routers.users.config import get_guest_pass, post_guest_pass
from schemas.user.guest_pass import GuestPassModel
from firebase.notification import pred_send_notification


router = APIRouter()


@router.get("/guest_pass")
async def guest_pass(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     session: AsyncSession = Depends(get_session)):

    try:

        data = await get_guest_pass(session, user['uid'])

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/guest_pass", status_code=status.HTTP_201_CREATED)
async def gust_pass_post(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                         request: GuestPassModel, session: AsyncSession = Depends(get_session)):

    try:

        data = await post_guest_pass(session, user['uid'], request)
        await pred_send_notification(user, session, value='guest_pass',
                                     title="Guest pass", body=f"{data[0]['visit_date']} - {data[0]['visit_time']} "
                                                              f"- {data[0]['full_name']}")
        return data

    except Exception as e:

        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
