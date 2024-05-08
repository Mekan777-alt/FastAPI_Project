from sqlalchemy.orm import joinedload

from models.base import EmployeeUK, TenantApartments, TenantProfile, Service
from sqlalchemy.future import select
from fastapi import HTTPException, Depends
from models.base import (Object, ApartmentProfile, ExecutorsProfile, Order, AdditionalService, AdditionalServiceList,
                         ExecutorOrders, BathroomApartment, MeterService, Meters, InvoiceHistory)
from firebase.config import get_staff_firebase
from firebase_admin import auth, firestore
from starlette import status
from datetime import date, timedelta
from sqlalchemy import delete, and_


async def get_employee_profile(session, data_from_firebase, object_id):
    try:

        object_name = await session.scalar(select(Object).where(Object.id == object_id))

        data = {
            "firstname": data_from_firebase['firstname'],
            "lastname": data_from_firebase['lastname'],
            "object_name": object_name.object_name
        }
        return data

    except Exception as e:
        return e


async def get_apartment_list(session, user):
    try:

        employee = user['uid']

        employee_id = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee))

        if not employee_id:
            return "Employee not found"

        object_id = await session.scalar(select(Object).where(Object.id == employee_id.object_id))

        apartment_list = await session.scalars(
            select(ApartmentProfile).where(ApartmentProfile.object_id == object_id.id))

        apartment_profile_list = []

        for apartment in apartment_list:
            apartment_data = {
                "id": apartment.id,
                "apartment_name": apartment.apartment_name,
                "area": apartment.area
            }
            apartment_profile_list.append(apartment_data)

        data = {
            "apartments": apartment_profile_list
        }
        return data

    except Exception as e:

        return e


async def create_apartment(session, user, apartment_data):
    try:

        employee = user['uid']

        object_id = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee))

        if not object_id:
            return "Employee not found"

        new_apartment = ApartmentProfile(
            apartment_name=apartment_data.apartment_name,
            area=apartment_data.area,
            object_id=object_id.object_id
        )

        session.add(new_apartment)
        await session.commit()

        data = {
            "id": new_apartment.id,
            "apartment_name": new_apartment.apartment_name,
            "area": new_apartment.area
        }

        return data

    except Exception as e:

        return e


async def get_apartments_info(session, apartment_id, user):
    try:

        # employee = user['uid']
        #
        # check_employee = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee))

        # if not check_employee:
        #     return "Employee not found"

        apartment = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        if not apartment:
            return "Apartment not found"

        bathrooms = await session.scalars(
            select(BathroomApartment).where(BathroomApartment.apartment_id == apartment_id))

        if not bathrooms:

            return apartment.to_dict()

        else:

            data = apartment.to_dict()
            data['bathrooms'] = []

            for bathroom in bathrooms:
                data['bathrooms'].append({"id": bathroom.id,
                                          "characteristic": bathroom.characteristic})

            return data
    except Exception as e:

        return e


async def get_employee_info(session, user):
    try:

        employee = user['uid']

        check_employee = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee))

        if not check_employee:
            return "Employee not found"

        firestore = await get_staff_firebase(employee)

        if not firestore:
            return "Employee not found from firestore"

        del firestore['role']
        firestore['photo_path'] = check_employee.photo_path

        return firestore
    except Exception as e:

        return e


async def get_executors_list(session):
    try:

        executors = await session.scalars(select(ExecutorsProfile))

        executors_list = []

        for executor in executors:
            data = await get_staff_firebase(executor.uuid)

            del data['role']
            del data['phone_number']
            del data['email']
            data['id'] = executor.id
            data['photo_path'] = executor.photo_path

            executors_list.append(data)

        data = {
            'executors': executors_list
        }

        return data

    except Exception as e:

        return e


async def get_executors_detail(session, staff_id):
    try:

        executor = await session.scalar(select(ExecutorsProfile).where(ExecutorsProfile.id == staff_id))

        data = await get_staff_firebase(executor.uuid)

        del data['role']
        data['photo_path'] = executor.photo_path

        return data

    except Exception as e:

        return e


async def add_tenant_db(session, apartment_id, tenant_info, employee):
    try:

        new_tenant = auth.create_user(
            email=tenant_info.email,
            password=tenant_info.password
        )

        collection_path = "users"

        db = firestore.client()
        user_doc = db.collection(collection_path).document(new_tenant.uid)

        first_last_name = tenant_info.first_last_name.split()

        user_data = {
            "email": tenant_info.email,
            "phone_number": tenant_info.phone_number,
            "first_name": first_last_name[0],
            "last_name": first_last_name[1],
            "role": "client"
        }
        user_doc.set(user_data)

        new_tenant_for_db = TenantProfile(
            uuid=new_tenant.uid,
            photo_path='null',
            active_request=0,
            balance=0
        )

        tenant_profile = TenantApartments(
            tenant_id=new_tenant_for_db.id,
            apartment_id=apartment_id
        )

        session.add(new_tenant_for_db, tenant_profile)
        await session.commit()

        return new_tenant_for_db.to_dict()

    except Exception as e:

        return None


async def get_new_order(session, apartment_id: int):
    try:

        orders = await session.scalars(
            select(Order)
            .where((Order.apartment_id == apartment_id) & (Order.status == 'new'))
        )

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        data_list = []
        for order in orders:

            icon_path = await session.scalar(select(Service).where(Service.id == order.selected_service_id))

            created_at = order.created_at.date()

            if created_at == date.today():
                name = 'Today'
            elif created_at == date.today() - timedelta(days=1):
                name = 'Yesterday'
            else:
                name = created_at.strftime('%d %h')
            service = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
            service_data = []
            additional_services = await session.scalars(select(AdditionalService)
                                                        .where(AdditionalService.order_id == order.id))

            for additional_service in additional_services:
                service_name = await session.scalar(select(AdditionalServiceList)
                                                    .where(AdditionalServiceList.id == additional_service.
                                                           additional_service_id))
                service_data.append(service_name.name)

            data = {
                "order_id": order.id,
                "icon_path": icon_path.mini_icons_path if icon_path else None,
                "service_name": service.name,
                "apartment_name": order.apartments.apartment_name,
                "created_at": f"{order.created_at.strftime('%H:%M')}",
                "status": order.status,
                "additional_info": {
                    "additional_service_list": service_data
                }
            }

            if not data_list or data_list[-1]['name'] != name:
                data_list.append({'name': name, 'services': []})

            data_list[-1]['services'].append(data)

        return data_list
    except Exception as e:
        raise e


async def get_new_order_id(session, apartment_id, order_id):
    try:

        query = (
            select(Order, AdditionalServiceList, AdditionalService)
            .join(AdditionalService, Order.id == AdditionalService.order_id)
            .join(AdditionalServiceList, AdditionalService.additional_service_id == AdditionalServiceList.id)
            .where(Order.id == order_id)
        )

        orders = await session.execute(query)

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        executors = await session.scalars(select(ExecutorsProfile))

        order_dict = {}
        for order, additional_service_list, additional_service in orders:
            icon_path = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
            service = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
            if order.id not in order_dict:
                order_dict[order.id] = {
                    "order_id": order.id,
                    "icon_path": icon_path.big_icons_path if icon_path else None,
                    "apartment_name": order.apartments.apartment_name,
                    "service_name": service.name,
                    "created_at": f"{order.created_at.strftime('%d %h %H:%M')}",
                    "completion_date": order.completion_date,
                    "completed_at": order.completion_time,
                    "status": order.status,
                    "additional_info": {
                        "additional_service_list": []
                    },
                    "executors": []
                }
            if additional_service_list:
                order_dict[order.id]["additional_info"]["additional_service_list"].append(additional_service_list.name)

            for executor in executors:
                check_executor = await session.scalar(
                    select(ExecutorOrders).where(ExecutorOrders.executor_id == executor.id))
                if not check_executor:
                    data = await get_staff_firebase(executor.uuid)
                    data["id"] = executor.id
                    order_dict[order.id]["executors"].append(data)

        return order_dict

    except HTTPException as e:

        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


async def select_executor(session, order_id, executor_id):
    try:
        check_order = await session.scalar(select(ExecutorOrders).where(ExecutorOrders.order_id == order_id))
        if check_order:
            return "Данный исполнитель занят или данный ордер уже исполняется"
        else:
            executor = ExecutorOrders(
                executor_id=executor_id,
                order_id=order_id
            )
            session.add(executor)
            order = await session.scalar(select(Order).where(Order.id == order_id))
            order.status = 'in progress'
            await session.commit()

            return {"executor_id": executor.executor_id, "order_id": executor.order_id}
    except HTTPException as e:

        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


async def get_in_progress_order(session, apartment_id):
    try:

        query = (
            select(Order, AdditionalServiceList, AdditionalService)
            .join(AdditionalService, Order.id == AdditionalService.order_id)
            .join(AdditionalServiceList, AdditionalService.additional_service_id == AdditionalServiceList.id)
            .where(Order.apartment_id == apartment_id, Order.status == 'in progress')
        )

        orders = await session.execute(query)

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        data_list = []
        for order, additional_service_list, additional_service in orders:

            if data_list and order.id in [service['order_id'] for service in data_list[-1]['services']]:
                data_list[-1]['services'][-1]["additional_info"]["additional_service_list"].append(
                    additional_service_list.name)
                continue

            icon_path = await session.scalar(select(Service).where(Service.id == order.selected_service_id))

            created_at = order.created_at.date()

            if created_at == date.today():
                name = 'Today'
            elif created_at == date.today() - timedelta(days=1):
                name = 'Yesterday'
            else:
                name = created_at.strftime('%d %h')
            service = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
            data = {
                "order_id": order.id,
                "icon_path": icon_path.mini_icons_path if icon_path else None,
                "service_name": service.name,
                "apartment_name": order.apartments.apartment_name,
                "created_at": f"{order.created_at.strftime('%H:%M')}",
                "status": order.status,
                "additional_info": {
                    "additional_service_list": []
                }
            }

            if additional_service_list:
                data["additional_info"]["additional_service_list"].append(additional_service_list.name)

            if not data_list or data_list[-1]['name'] != name:
                data_list.append({'name': name, 'services': []})

            data_list[-1]['services'].append(data)

        return data_list
    except Exception as e:

        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


async def create_bathroom(session, bathroom_data, apartment_id):
    try:

        new_bathroom = BathroomApartment(
            characteristic=bathroom_data.characteristic,
            apartment_id=apartment_id
        )

        session.add(new_bathroom)
        await session.commit()

        return new_bathroom.to_dict()
    except Exception as e:

        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


async def create_additionally(session, apartment_id, additionally_data):
    try:

        apartment = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        if additionally_data.garden is True or additionally_data.garden is False:
            apartment.garden = additionally_data.garden
        if additionally_data.pool is True or additionally_data.pool is False:
            apartment.pool = additionally_data.pool

        session.add(apartment)
        await session.commit()

        return apartment.to_dict()

    except (HTTPException, Exception) as e:
        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


async def enter_meters(session, apartment_id, user):
    try:

        data_list = []
        apartment = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))
        if apartment:

            apartment_data = {
                "id": apartment.id,
                "name": apartment.apartment_name
            }
            data_list.append(apartment_data)

            meter_service = await session.scalars(select(MeterService))
            meter_service_list = []

            for service in meter_service:
                data = {
                    "id": service.id,
                    "name": service.name
                }
                meter_service_list.append(data)
            data_list.append(meter_service_list)
        return data_list
    except HTTPException as e:
        return e


async def new_meters(session, meter_data, apartment_id, user):
    try:

        readings = Meters(
            apartment_id=meter_data.apartment_id,
            meter_service_id=meter_data.meter_id,
            bill_number=meter_data.bill_number,
            meters_for=meter_data.month_year,
            meter_readings=meter_data.meter_readings,
            comment=meter_data.comment,
            status='not paid'
        )
        session.add(readings)
        await session.commit()

        return readings
    except HTTPException as e:
        return e


async def get_apartment_invoice(session, apartment_id, user):
    try:

        apartment = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        meter_service = await session.scalars(select(MeterService))
        services = await session.scalars(select(Service))

        data_list = []

        apartment_data = {
            "id": apartment.id,
            "name": apartment.apartment_name
        }
        data_list.append(apartment_data)
        service_list = []
        meter_service_list = {
            "meter_service_list": []
        }
        for service in meter_service:
            meter_service_data = {
                "id": service.id,
                "name": service.name
            }
            meter_service_list["meter_service_list"].append(meter_service_data)
        service_list.append(meter_service_list)

        service_list_services = {
            "service_list": []
        }
        for service in services:
            service_data = {
                "id": service.id,
                "name": service.name
            }
            service_list_services["service_list"].append(service_data)
        service_list.append(service_list_services)

        response_service = {
            "services_list": service_list
        }
        data_list.append(response_service)

        return data_list

    except HTTPException as e:

        return e


async def create_invoice(session, apartment_id, invoice_data, user):
    try:

        service_id, service_name = invoice_data.service_id, invoice_data.service_name

        service = await session.scalar(select(Service).where(Service.id == service_id))

        meter_service = await session.scalar(select(MeterService).where(MeterService.id == service_id))
        if service.name == service_name:
            new_invoice = InvoiceHistory(
                amount=invoice_data.amount,
                apartment_id=invoice_data.apartment_id,
                service_id=service.id,
                bill_number=invoice_data.bill_number,
                comment=invoice_data.comment
            )

            session.add(new_invoice)
            await session.commit()

            return new_invoice

        if meter_service.name == service_name:

            new_invoice = InvoiceHistory(
                amount=invoice_data.amount,
                apartment_id=invoice_data.apartment_id,
                meter_service_id=meter_service.id,
                bill_number=invoice_data.bill_number,
                comment=invoice_data.comment
            )
            session.add(new_invoice)
            await session.commit()

            return new_invoice

        else:

            return None

    except HTTPException as e:

        return e


async def meter_readings_get(session, apartment_id, user):
    try:
        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))
        meters_info = await session.scalars(select(Meters).where(Meters.apartment_id == apartment_id))

        data_list = []
        for meter in meters_info:
            icon_path = await session.scalar(select(MeterService).where(MeterService.id == meter.id))
            created_at = meter.created_at.date()

            if created_at == date.today():
                name = 'Today'
            elif created_at == date.today() - timedelta(days=1):
                name = 'Yesterday'
            else:
                name = created_at.strftime('%d %h')

            data = {
                'id': meter.id,
                'icon_path': icon_path.mini_icons_path if icon_path else None,
                'apartment_name': apartment_info.apartment_name,
                'created_at_date': meter.created_at.strftime('%d %h'),
                'created_at_time': meter.created_at.strftime('%H:%M')
            }

            if not data_list or data_list[-1]['name'] != name:
                data_list.append({'name': name, 'services': []})

            data_list[-1]['services'].append(data)

        return data_list

    except HTTPException as e:
        raise e


async def delete_bathroom(session, apartment_id, bathroom_id):
    try:

        bathroom = await session.scalar(select(BathroomApartment).where(BathroomApartment.id == bathroom_id))

        if bathroom:

            await session.execute(delete(BathroomApartment).where(BathroomApartment.id == bathroom_id))
            await session.commit()

        else:

            return "Bathroom not found"

    except HTTPException as e:
        raise e
