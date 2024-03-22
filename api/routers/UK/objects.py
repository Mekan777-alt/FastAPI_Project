from fastapi import APIRouter, Depends, Request
from typing import Annotated
from starlette.responses import JSONResponse
from config import get_session
from starlette import status
from firebase.config import get_firebase_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.UK.config import (get_objects_from_uk, create_object_to_db, get_object_id, get_apartments_from_object,
                                   create_apartment_for_object)
from schemas.uk.object import ObjectSchemas, ObjectCreateSchema, Object
from schemas.uk.apartments import ApartmentsList, ApartmentSchemasCreate


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


@router.post("/create_object", response_model=ObjectCreateSchema)
async def create_object(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                        object_data: ObjectCreateSchema, session: AsyncSession = Depends(get_session)):

    try:

        data = await create_object_to_db(session, user, object_data)

        return JSONResponse(content=data, status_code=status.HTTP_201_CREATED)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e)


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
async def create_apartment(object_id: int, apartment_data: ApartmentSchemasCreate,
                           session: AsyncSession = Depends(get_session)):
    try:

        data = await create_apartment_for_object(session, object_id, apartment_data)

        return JSONResponse(content=data, status_code=status.HTTP_201_CREATED)

    except Exception as e:

        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)