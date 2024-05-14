from fastapi import APIRouter, Depends, Form, File, UploadFile
from typing import Annotated
from sqlalchemy import select
from starlette.responses import JSONResponse
from config import get_session
from starlette import status
import shutil
from models.base import Object as ObjectModels, UK, ApartmentProfile
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.UK.config import (get_objects_from_uk, get_object_id, get_apartments_from_object,
                                   create_apartment_for_object, get_staff_object, get_staff_id_object)
from schemas.uk.object import ObjectSchemas, Object
from schemas.uk.apartments import ApartmentsList, ApartmentSchemasCreate

router = APIRouter()


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
                        photo: UploadFile = File(...),
                        session: AsyncSession = Depends(get_session)):
    try:
        photo.filename = photo.filename.lower()
        path = f'static/photo/object/{photo.filename}'

        with open(path, "wb+") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        staff_id = user['uid']

        uk_id = await session.scalar(select(UK).where(UK.uuid == staff_id))
        create_obj = ObjectModels(
            object_name=object_name,
            address=object_address,
            photo_path=f"http://217.25.95.113:8000/{path}",
            uk_id=uk_id.id
        )

        session.add(create_obj)
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
                              photo: UploadFile = File(...),
                              session: AsyncSession = Depends(get_session)):
    try:
        photo.filename = photo.filename.lower()
        path = f'static/photo/apartments/{photo.filename}'

        with open(path, "wb+") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        if not object_id:
            return "Employee not found"

        new_apartment = ApartmentProfile(
            apartment_name=apartment_name,
            area=area,
            key_holder=key_holder,
            internet_speed=internet_speed,
            internet_fee=internet_fee,
            photo_path=f"http://217.25.95.113:8000/{path}",
            internet_operator=internet_operator,
            object_id=object_id
        )

        session.add(new_apartment)
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
