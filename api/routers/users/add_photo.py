import os
import shutil
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_user, get_firebase_user_from_token
from starlette.responses import JSONResponse
from typing import Annotated
from fastapi import Depends, UploadFile, File, APIRouter
from sqlalchemy.future import select
from models.models import TenantProfile
from config import get_session

router = APIRouter(
    prefix="/api/v1",
    tags=['Profile']
)


@router.post("/add_photo")
async def add_photo(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                    session: AsyncSession = Depends(get_session), photo: UploadFile = File(...)):

    try:
        photo.filename = photo.filename.lower()
        path = f'media/{photo.filename}'

        with open(path, "wb+") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        tenant_id = user["uid"]

        tenant = await session.execute(select(TenantProfile).where(TenantProfile.uuid == tenant_id))
        tenant_profile = tenant.scalar()

        tenant_profile.photo_path = path
        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content="OK")


    except (FileNotFoundError) as e:

        return JSONResponse(

            content={"message": str(e)},

            status_code=status.HTTP_400_BAD_REQUEST,

        )

