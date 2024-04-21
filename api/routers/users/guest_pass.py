from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from api.routers.users.config import get_guest_pass


router = APIRouter(
    prefix="/api/v1/client",
)


@router.get("/guest_pass")
async def guest_pass(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     session: AsyncSession = Depends(get_session)):

    try:

        data = await get_guest_pass(session, user['uid'])

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)