from fastapi import APIRouter, Depends, Form, File, UploadFile
from typing import Annotated, List
from sqlalchemy import select
from starlette.responses import JSONResponse
from config import get_session
from starlette import status
import shutil
from models.base import Object as ObjectModels, UK, ApartmentProfile, Service, ServiceObjectList
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.UK.config import (get_objects_from_uk, get_object_id, get_apartments_from_object,
                                   create_apartment_for_object, get_staff_object, get_staff_id_object)
from schemas.uk.object import ObjectSchemas, Object
from schemas.uk.apartments import ApartmentsList
from schemas.uk.add_additional import Additionaly
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


@router.get("/get_objects_uk", response_model=ObjectSchemas)
async def get_objects(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                      session: AsyncSession = Depends(get_session)):
    try:

        data = await get_objects_from_uk(session, user)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/create_object")
async def create_object(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                        object_name: str = Form(...),
                        object_address: str = Form(...),
                        photo: UploadFile = File(None),
                        session: AsyncSession = Depends(get_session)):
    try:
        staff_id = user['uid']

        uk_id = await session.scalar(select(UK).where(UK.uuid == staff_id))
        create_obj = ObjectModels(
            object_name=object_name,
            address=object_address,
            uk_id=uk_id.id
        )

        session.add(create_obj)
        await session.commit()

        if photo:

            file_key = await s3_client.upload_file(photo, create_obj.id, "objects")
            create_obj.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"

        else:

            create_obj.photo_path = "http://217.25.95.113:8000/static/icons/big/object_main.jpg"

        await session.commit()

        return JSONResponse(content=create_obj.to_dict(), status_code=status.HTTP_201_CREATED)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/get_objects_uk/{object_id}", response_model=Object)
async def get_object_id_uk(object_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_object_id(session, object_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


# @router.put("/get_objects_uk/{object_id}/update-info")
# async def update_object_info(object_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
#                              session: AsyncSession = Depends(get_session),
#                              object_name: str = Form(None),
#                              object_address: str = Form(None),
#                              photo: UploadFile = File(None)):
#     try:
#
#         object_info = await session.scalar(select(ObjectModels).where(ObjectModels.id == object_id))
#
#         if not object_info:
#             return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Object not found")
#
#         if object_name:
#
#             object_info.object_name = object_name
#             await session.commit()
#
#         if object_address:
#             object_info.address = object_address
#             await session.commit()
#
#         if photo:
#             photo.filename = photo.filename.lower()
#
#             file_key = await s3_client.upload_file(photo, object_info.id, "objects")
#             object_info.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"
#
#             await session.commit()
#
#         return JSONResponse(content=object_info.to_dict(), status_code=status.HTTP_200_OK)
#
#     except Exception as e:
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/get_objects_uk/{object_id}/list-service")
async def get_list_service_to_object(object_id: int, session: AsyncSession = Depends(get_session)):
    try:

        object_info = await session.scalar(select(ObjectModels).where(ObjectModels.id == object_id))

        if not object_info:
            return "Object not found"

        services = await session.scalars(select(Service))

        service_list = []
        for service in services:
            data = {
                "id": service.id,
                "service_name": service.name
            }
            service_list.append(data)

        return JSONResponse(status_code=status.HTTP_200_OK, content=service_list)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/get_objects_uk/{object_id}/list-service")
async def post_list_order_to_object(object_id: int,
                                    request: Additionaly,
                                    session: AsyncSession = Depends(get_session)):
    try:

        object_info = await session.scalar(select(ObjectModels).where(ObjectModels.id == object_id))

        if not object_info:
            return "Object not found"

        check_service = await session.scalar(select(ServiceObjectList)
                                             .where((ServiceObjectList.service_id == request.id)
                                                    & (ServiceObjectList.object_id == object_id)))
        if check_service:

            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content=str("This service has already been added"))

        new_service = ServiceObjectList(
            object_id=object_id,
            service_id=request.id
        )
        session.add(new_service)

        await session.commit()

        return JSONResponse(content=request.to_dict(), status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/get_objects_uk/{object_id}/list-service/{service_id}/delete",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_list_service_to_object(object_id: int, service_id: int,
                                        user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                        session: AsyncSession = Depends(get_session)):
    try:

        service = await session.scalar(select(ServiceObjectList).where((ServiceObjectList.object_id == object_id) &
                                                                       (ServiceObjectList.service_id == service_id)))
        await session.delete(service)
        await session.commit()

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/get_objects_uk/{object_id}/apartment_list", response_model=ApartmentsList)
async def get_apartment_list(object_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_apartments_from_object(session, object_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/get_objects_uk/{object_id}/create_apartment")
async def create_apartment_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                              object_id: int,
                              apartment_name: str = Form(...),
                              area: float = Form(...),
                              key_holder: str = Form(...),
                              internet_speed: int = Form(...),
                              internet_fee: float = Form(...),
                              internet_operator: str = Form(...),
                              photo: UploadFile = File(None),
                              session: AsyncSession = Depends(get_session)):
    try:

        new_apartment = ApartmentProfile(
            apartment_name=apartment_name,
            area=area,
            key_holder=key_holder,
            internet_speed=internet_speed,
            internet_fee=internet_fee,
            internet_operator=internet_operator,
            object_id=object_id
        )

        session.add(new_apartment)
        await session.commit()

        if photo:

            file_key = await s3_client.upload_file(photo, new_apartment.id, "apartments")
            new_apartment.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"

        else:

            new_apartment.photo_path = "http://217.25.95.113:8000/static/icons/big/object_main.jpg"

        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_apartment.to_dict())
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/get_objects_uk/{object_id}/get_staff_object")
async def get_object_id_uk(object_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                           session: AsyncSession = Depends(get_session)):
    try:

        data = await get_staff_object(session, object_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/get_objects_uk/{object_id}/get_staff_object/{staff_id}")
async def get_object_id_uk(object_id: int, staff_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                           session: AsyncSession = Depends(get_session)):
    try:

        data = await get_staff_id_object(session, object_id, staff_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
