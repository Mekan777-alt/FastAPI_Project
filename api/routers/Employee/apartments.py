from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from firebase_admin import firestore
from sqlalchemy import select
from firebase.config import get_firebase_user_from_token, get_staff_firebase, delete_staff_firebase
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from models.base import (ApartmentProfile, EmployeeUK, TenantApartments, TenantProfile, Order, ExecutorOrders,
                         ExecutorsProfile, Service, AdditionalService, AdditionalServiceList,
                         NotificationUK, NotificationEmployee, UK, Object)
from schemas.employee.enter_meters import EnterMeters
from schemas.employee.additionally import Additionally
from schemas.employee.invoice import Invoice
from starlette import status
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
from api.routers.S3.main import S3Client
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(
    prefix="/api/v1/employee"
)

s3_client = S3Client(
    access_key=os.getenv("ACCESS_KEY_AWS"),
    secret_key=os.getenv("SECRET_KEY_AWS"),
    bucket_name=os.getenv("BUCKET_NAME"),
    endpoint_url=os.getenv("ENDPOINT_URL")
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
                                    photo: UploadFile = File(None),
                                    session: AsyncSession = Depends(get_session)):
    try:
        photo.filename = photo.filename.lower()

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
            internet_operator=internet_operator,
            object_id=object_id.object_id
        )

        session.add(new_apartment)
        await session.commit()

        file_key = await s3_client.upload_file(photo, new_apartment.id, "apartments")
        new_apartment.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"
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


@router.put("/apartments/apartment_info/{apartment_id}/update-info")
async def update_apartment_info(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                apartment_id: int,
                                session: AsyncSession = Depends(get_session),
                                apartment_name: str = Form(None),
                                photo: UploadFile = File(None),
                                area: str = Form(None)):
    try:

        apartment = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        if not apartment:
            return "Apartment not found"

        if photo:
            photo.filename = photo.filename.lower()

            file_key = await s3_client.upload_file(photo, apartment.id, "apartments")
            apartment.photo_path = f"https://{s3_client.bucket_name}.s3.timeweb.cloud/{file_key}"

            await session.commit()

        if apartment_name:
            apartment.apartment_name = apartment_name

            await session.commit()

        if area:
            apartment.area = area

            await session.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content=apartment.to_dict())

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

                data['photo_path'] = profile.photo_path if profile.photo_path else None
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

        return JSONResponse(content=data, status_code=status.HTTP_201_CREATED)

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


@router.get("/apartments/apartment_info/{apartment_id}/service_order/completed")
async def get_service_order_completed(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                      apartment_id: int, session: AsyncSession = Depends(get_session)):
    try:

        data = await get_completed_orders(session, apartment_id)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/apartments/apartment_info/{apartment_id}/service_order/{order_id}")
async def get_service_order_in_progress(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                        apartment_id: int, order_id: int, session: AsyncSession = Depends(get_session)):
    try:
        order = await session.scalar(
            select(Order)
            .where(Order.id == order_id)
        )

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))
        executor_data = []

        object_info = await session.scalar(select(Object).where(Object.id == apartment_info.object_id))

        if order.status == 'new':
            executor_info = await session.scalars(select(ExecutorsProfile).where(ExecutorsProfile.uk_id == object_info.uk_id))

            for executor in executor_info:
                executor_data.append(executor.to_dict())

        elif order.status == 'in progress' or order.status == 'completed':
            active_executor = await session.scalar(select(ExecutorOrders).where(ExecutorOrders.order_id == order_id))

            executor_info = await session.scalars(select(ExecutorsProfile).where(ExecutorsProfile.uk_id == object_info.uk_id))

            for executor in executor_info:
                if executor.id == active_executor.executor_id:

                    executor_dict = executor.to_dict()
                    executor_dict['active'] = True
                    executor_data.append(executor_dict)
                else:
                    executor_data.append(executor.to_dict())

        service = await session.scalar(select(Service).where(Service.id == order.selected_service_id))

        service_data = []
        additional_services = await session.scalars(select(AdditionalService)
                                                    .where(AdditionalService.order_id == order.id))

        for additional_service in additional_services:
            service_name = await (session.scalar
                                  (select(AdditionalServiceList)
                                   .where(AdditionalServiceList.id == additional_service.additional_service_id)))
            service_data.append(service_name.name)
        order.is_view = True
        await session.commit()

        db = firestore.client()
        query = db.collection('notifications').where('id', '==', f'{order_id}')

        result = query.stream()

        for doc in result:

            data = doc.to_dict()

            if data['screen'] == 'order':
                user_fb = await get_staff_firebase(user['uid'])

                if user_fb['role'] == "Employee":
                    check_notification = db.collection("notifications").document(doc.id).get(
                        {"is_view": {"employee": True}}).to_dict()
                    if check_notification['is_view']['employee'] is True:
                        pass
                    else:
                        db.collection("notifications").document(doc.id).set({"is_view": {"employee": True}}, merge=True)

                        employee_info = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == user['uid']))

                        employee_notify = await session.scalar(select(NotificationEmployee)
                                                               .where(
                            NotificationEmployee.object_id == employee_info.object_id))

                        employee_notify.is_view = True
                        await session.commit()

                elif user_fb['role'] == "Company":
                    check_notification = db.collection("notifications").document(doc.id).get(
                        {"is_view": {"company": True}}).to_dict()
                    if check_notification['is_view']['company'] is True:
                        pass
                    else:
                        db.collection("notifications").document(doc.id).set({"is_view": {"company": True}}, merge=True)

                        company_info = await session.scalar(select(UK).where(UK.uuid == user['uid']))

                        company_notify = await session.scalar(
                            select(NotificationUK).where(NotificationUK.uk_id == company_info.id))

                        company_notify.is_view = True
                        await session.commit()

        order_dict = {
            "order_id": order.id,
            "icon_path": service.big_icons_path if service.mini_icons_path else service.big_icons_path,
            "apartment_name": order.apartments.apartment_name,
            "service_name": service.name,
            "created_at": f"{order.created_at.strftime('%d %h %H:%M')}",
            "completion_date": order.completion_date,
            "completed_at": order.completion_time,
            "is_view": order.is_view,
            "status": order.status,
            "additional_info": {
                "additional_service_list": service_data
            },
            "executor": executor_data
        }

        return JSONResponse(content=order_dict, status_code=status.HTTP_200_OK)

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

        data = await select_executor(user, session, order_id, executor_id, apartment_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except HTTPException as e:

        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/apartments/apartment_info/{apartment_id}/service_order/progress/{order_id}/to_work/{executor_id}")
async def get_service_order_progress_id(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                                        apartment_id: int, order_id: int, executor_id: int,
                                        session: AsyncSession = Depends(get_session)):
    try:

        data = await select_executor(user, session, order_id, executor_id, apartment_id)

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

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)

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
