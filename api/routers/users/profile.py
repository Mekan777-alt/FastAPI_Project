from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token, register_user
from typing import Annotated
from config import get_session
from api.routers.users.add_photo import router
from api.routers.users.config import get_profile_tenant
from sqlalchemy.ext.asyncio import AsyncSession


@router.get("/profile")
async def get_profile(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                      session: AsyncSession = Depends(get_session)):

    try:
        user_info = await get_profile_tenant(user, session)

        return JSONResponse(status_code=status.HTTP_200_OK, content=user_info)

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
