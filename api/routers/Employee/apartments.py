from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from firebase.config import get_firebase_user_from_token, get_staff_firebase, delete_staff_firebase
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from models.base import ApartmentProfile, EmployeeUK, TenantApartments, TenantProfile
from schemas.employee.enter_meters import EnterMeters
from schemas.employee.additionally import Additionally
from schemas.employee.invoice import Invoice
from starlette import status
import shutil
from api.routers.Employee.config import (get_apartment_list, get_apartments_info, add_tenant_db,
                                         get_new_order, get_new_order_id, select_executor, get_in_progress_order,
                                         create_bathroom, create_additionally, enter_meters, new_meters,
                                         get_apartment_invoice, create_invoice, meter_readings_get, delete_bathroom,
                                         get_in_progress_order_id, get_in_progress_order_id_completed,
                                         get_completed_orders, get_payment_history_apartment,
                                         get_payment_history_to_paid, get_invoice_id, paid_invoice_id,
                                         unpaid_invoice_id)
from starlette.responses import JSONResponse
from schemas.employee.bathroom import CreateBathroom
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


@router.post("/apartments/create_apartment")
async def create_apartment_employee(user: Annotated[dict, Depends(get_firebase_user_from_token)],
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

        employee = user['uid']

        object_id = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee))

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
            object_id=object_id.object_id
        )

        session.add(new_apartment)
        await session.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_apartment.to_dict())

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


@router.get("/apartments/apartment_info/{apartment_id}/list_tenant")
async def get_tenant_from_apartment(user: Annotated[dict, Depends(get_firebase_user_from_token)], apartment_id: int,
                                    session: AsyncSession = Depends(get_session)):
    try:

        tenants = await session.scalars(select(TenantApartments).where(TenantApartments.apartment_id == apartment_id))

        tenant_list = []
        for tenant in tenants:

            tenants_profile = await session.scalars(select(TenantProfile).where(TenantProfile.id == tenant.tenant_id))

            for profile in tenants_profile:

                data = await get_staff_firebase(profile.uuid)

                data['photo_path'] = profile.photo_path
                data['balance'] = profile.balance
                data['id'] = profile.id
                del data['role']

                tenant_list.append(data)

        return JSONResponse(content=tenant_list, status_code=status.HTTP_200_OK)

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/apartments/apartment_info/{apartment_id}/list_tenant/{tenant_id}")
async def get_tenant_id(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                        apartment_id: int, tenant_id: int, session: AsyncSession = Depends(get_session)):
    try:

        tenant = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant_id))

        data = await get_staff_firebase(tenant.uuid)

        data['photo_path'] = tenant.photo_path
        data['balance'] = tenant.balance
        data['id'] = tenant.id
        del data['role']

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)
    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/apartments/apartment_info/{apartment_id}/list_tenant/{tenant_id}/delete")
async def delete_tenant_from_apartment(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                       apartment_id: int, tenant_id: int, session: AsyncSession = Depends(get_session)):

    try:

        tenant_data = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant_id))
        if not tenant_data:
            return "Tenant not found"

        delete_db = await delete_staff_firebase(tenant_data.uuid)

        if delete_db:

            tenant_apart = await session.scalars(
                select(TenantApartments).where(
                    (TenantApartments.apartment_id == apartment_id) & (TenantApartments.tenant_id == tenant_id)))

            for apartment in tenant_apart:
                await session.delete(apartment)
                await session.commit()

            await session.delete(tenant_data)
            await session.commit()

            return "Deleted successfully"
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Not Found")

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/apartments/apartment_info/{apartment_id}/payment-history/unpaid")
async def get_payment_history(user: Annotated[dict, Depends(get_firebase_user_from_token)], apartment_id: int,
                              session: AsyncSession = Depends(get_session)):
    try:

        data = await get_payment_history_apartment(session, apartment_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/payment-history/paid")
async def get_paid_history_payment(user: Annotated[dict, Depends(get_firebase_user_from_token)], apartment_id: int,
                                   session: AsyncSession = Depends(get_session)):
    try:

        data = await get_payment_history_to_paid(session, apartment_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/payment-history/{invoice_id}")
async def get_invoice_id_from_history(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                      apartment_id: int, invoice_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_invoice_id(session, apartment_id, invoice_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/payment-history/{invoice_id}/paid")
async def paid_invoice(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       apartment_id: int, invoice_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await paid_invoice_id(session, apartment_id, invoice_id)

        return JSONResponse(content=data, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/payment-history/{invoice_id}/unpaid")
async def unpaid_invoice(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                         apartment_id: int, invoice_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await unpaid_invoice_id(session, apartment_id, invoice_id)

        return JSONResponse(content=data, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/add_tenant")
async def add_tenant(user: Annotated[dict, Depends(get_firebase_user_from_token)], apartment_id: int,
                     tenant_info: AddTenant, session: AsyncSession = Depends(get_session)):
    try:

        data = await add_tenant_db(session, apartment_id, tenant_info, user)

        if data is None:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"info": "Tenant already exists"})

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/service_order/new")
async def get_service_order_new(
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


@router.get("/apartments/apartment_info/{apartment_id}/service_order/progress/{order_id}")
async def get_service_order_in_progress(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                        apartment_id: int, order_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_in_progress_order_id(session, order_id, apartment_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/service_order/progress/{order_id}/completed")
async def get_service_order_in_progress(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                        apartment_id: int, order_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_in_progress_order_id_completed(session, order_id, apartment_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/service_order/completed")
async def get_service_order_completed(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                      apartment_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_completed_orders(session, apartment_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

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


@router.delete("/apartments/apartment_info/{apartment_id}/add_bathroom/{bathroom_id}")
async def delete_bathroom_to_apartments(apartment_id: int, bathroom_id: int,
                                        user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                        session: AsyncSession = Depends(get_session)):
    try:

        await delete_bathroom(session, apartment_id, bathroom_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content=f"bathroom {bathroom_id} deleted successfully")

    except HTTPException as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/add_additionally", response_model=Additionally)
async def add_additionally_to_apartments(apartment_id: int,
                                         user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                         additionally_data: Additionally, session: AsyncSession = Depends(get_session)):
    try:

        data = await create_additionally(session, apartment_id, additionally_data)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)

    except HTTPException as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/enter_meters")
async def apartment_info_enter_meters(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                      apartment_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await enter_meters(session, apartment_id, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/enter_meters")
async def apartment_info_enter_meters_pose(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                           meter_data: EnterMeters, apartment_id: int,
                                           session: AsyncSession = Depends(get_session)):
    try:

        data = await new_meters(session, meter_data, apartment_id, user)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data.to_dict())

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/invoice")
async def apartment_info_invoice_get(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                     apartment_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_apartment_invoice(session, apartment_id, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/apartments/apartment_info/{apartment_id}/invoice")
async def apartment_info_invoice_post(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                      invoice_data: Invoice, apartment_id: int,
                                      session: AsyncSession = Depends(get_session)):
    try:

        data = await create_invoice(session, apartment_id, invoice_data, user)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data.to_dict())

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/meter_readings")
async def get_apartment_info_meter_readings(apartment_id: int,
                                            user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                            session: AsyncSession = Depends(get_session)):
    try:

        data = await meter_readings_get(session, apartment_id, user)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
