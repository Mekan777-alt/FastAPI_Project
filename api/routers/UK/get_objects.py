from fastapi import APIRouter, Depends
from typing import Annotated
from starlette.responses import JSONResponse
from config import get_session
from starlette import status
from firebase.config import get_firebase_user_from_token, get_user
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/api/v1"
)


@router.get("/get_objects_uk")
async def get_objects(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                      session: AsyncSession = Depends(get_session)):

    staff = get_user(user, session)

    try:

        pass

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=str(e))
