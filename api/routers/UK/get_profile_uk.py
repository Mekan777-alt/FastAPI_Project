from typing import Annotated
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token
from fastapi import APIRouter, Depends
from api.routers.UK.config import get_profile_uk
from starlette.responses import JSONResponse
from starlette import status
from schemas.uk.get_profile_uk import UKProfile

router = APIRouter(
    prefix="/api/v1"
)


@router.get('/get_profile_uk', response_model=UKProfile)
async def get_profile_staff(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                            session: AsyncSession = Depends(get_session)):

    try:

        data = await get_profile_uk(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))

