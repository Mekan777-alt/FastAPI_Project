from fastapi import APIRouter, Depends
from typing import Annotated
from starlette.responses import JSONResponse
from config import get_session
from starlette import status
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.UK.config import get_objects_from_uk
from schemas.uk.get_objects import ObjectSchemas


router = APIRouter(
    prefix="/api/v1"
)


@router.get("/get_objects_uk", response_model=ObjectSchemas)
async def get_objects(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                      session: AsyncSession = Depends(get_session)):

    try:

        data = await get_objects_from_uk(session, user)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
