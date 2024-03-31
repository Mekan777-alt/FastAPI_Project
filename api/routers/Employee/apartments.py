from fastapi import APIRouter, Depends, HTTPException
from firebase.config import get_firebase_user_from_token
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from schemas.employee.additionally import Additionally
from starlette import status
from api.routers.Employee.config import (get_apartment_list, create_apartment, get_apartments_info, add_tenant_db,
                                         get_new_order, get_new_order_id, select_executor, get_in_progress_order,
                                         create_bathroom, create_additionally)
from starlette.responses import JSONResponse

from schemas.employee.bathroom import CreateBathroom
from schemas.uk.apartments import ApartmentSchemasCreate
from schemas.uk.add_tenant import AddTenant

router = APIRouter(
    prefix="/api/v1/employee"
)


@router.get("/apartments")
async def get_apartments_employee(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                  session: AsyncSession = Depends(get_session)):
    try:

        data = await get_apartment_list(session, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/create_apartment", response_model=ApartmentSchemasCreate)
async def create_apartment_employee(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                    apartment_data: ApartmentSchemasCreate,
                                    session: AsyncSession = Depends(get_session)):
    try:

        data = await create_apartment(session, user, apartment_data)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}")
async def apartment_info(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                         apartment_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_apartments_info(session, apartment_id, user)

        if data in ["Employee not found", "Apartment not found"]:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=data)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/add_tenant")
async def add_tenant(user: Annotated[dict, Depends(get_firebase_user_from_token)], apartment_id: int,
                     tenant_info: AddTenant, session: AsyncSession = Depends(get_session)):
    try:

        data = await add_tenant_db(session, apartment_id, tenant_info, user)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/service_order/new")
async def get_service_order_new(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                apartment_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_new_order(session, apartment_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)
    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/service_order/progress")
async def get_service_order_in_progress(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                        apartment_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_in_progress_order(session, apartment_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/service_order/completed")
async def get_service_order_completed(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                      apartment_id: int, session: AsyncSession = Depends(get_session)):
    try:

        pass

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/service_order/new/{order_id}")
async def get_service_order_new_id(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                   apartment_id: int, order_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_new_order_id(session, apartment_id, order_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/apartments/apartment_info/{apartment_id}/service_order/new/{order_id}/to_work/{executor_id}")
async def get_service_order_new_id(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                   apartment_id: int, order_id: int, executor_id: int,
                                   session: AsyncSession = Depends(get_session)):
    try:

        data = await select_executor(session, order_id, executor_id)

        if data == "Данный исполнитель занят другим ордером":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except HTTPException as e:

        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/apartments/apartment_info/{apartment_id}/add_bathroom")
async def add_bathroom_to_apartments(apartment_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                     bathroom_data: CreateBathroom, session: AsyncSession = Depends(get_session)):

    try:

        data = await create_bathroom(session, bathroom_data, apartment_id)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)

    except HTTPException as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/add_additionally", response_model=Additionally)
async def add_additionally_to_apartments(apartment_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                         additionally_data: Additionally, session: AsyncSession = Depends(get_session)):
    try:

        data = await create_additionally(session, apartment_id, additionally_data)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)

    except HTTPException as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

