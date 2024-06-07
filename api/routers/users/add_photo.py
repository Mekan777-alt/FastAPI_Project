import shutil
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token
from starlette.responses import JSONResponse
from typing import Annotated
from fastapi import Depends, UploadFile, File, APIRouter
from sqlalchemy.future import select
from models.base import TenantProfile
from config import get_session
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


@router.post("/add_photo")
async def add_photo(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                    session: AsyncSession = Depends(get_session), photo: UploadFile = File(...)):

    try:
        photo.filename = photo.filename.lower()

        tenant_id = user["uid"]

        tenant = await session.execute(select(TenantProfile).where(TenantProfile.uuid == tenant_id))
        tenant_profile = tenant.scalar()

        file_key = await s3_client.upload_file(photo, tenant_profile.id, "client")
        tenant_profile.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"
        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"photo_path": tenant_profile.photo_path})

    except (FileNotFoundError) as e:

        return JSONResponse(

            content={"message": str(e)},

            status_code=status.HTTP_400_BAD_REQUEST,

        )

