from typing import Annotated
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from api.routers.UK.config import get_profile_uk
from starlette.responses import JSONResponse
from starlette import status
from sqlalchemy import select
from models.base import UK
from schemas.uk.get_profile_uk import UKProfile
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


@router.get('/get_profile_uk', response_model=UKProfile)
async def get_profile_staff(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                            session: AsyncSession = Depends(get_session)):

    try:

        data = await get_profile_uk(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post('/get_profile_uk/add_photo')
async def added_photo_to_profile_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                    session: AsyncSession = Depends(get_session), photo: UploadFile = File(...)):
    try:

        photo.filename = photo.filename.lower()

        uk_id = user["uid"]

        uk = await session.scalar(select(UK).where(UK.uuid == uk_id))

        file_key = await s3_client.upload_file(photo, uk.id, "uk")
        uk.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"
        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"photo_path": uk.photo_path})

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))