from sqlalchemy.orm import joinedload
from sqlalchemy import not_
from models.base import EmployeeUK, TenantApartments, TenantProfile, Service
from sqlalchemy.future import select
from fastapi import HTTPException, Depends
from models.base import (Object, ApartmentProfile, ExecutorsProfile, Order, AdditionalService, AdditionalServiceList,
                         ExecutorOrders, BathroomApartment, MeterService, Meters, InvoiceHistory)
from firebase.config import get_staff_firebase
from firebase_admin import auth, firestore
from starlette import status
from datetime import date, timedelta
from sqlalchemy import delete, func
from firebase.notification import pred_send_notification


async def get_employee_profile(session, data_from_firebase, object_id):
    try:

        object_name = await session.scalar(select(Object).where(Object.id == object_id))

        data = {
            "first_name": data_from_firebase['first_name'],
            "last_name": data_from_firebase['last_name'],
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


async def get_apartments_info(session, apartment_id, user):
    try:
        active_orders_count = await session.scalar(
            select(func.count())
            .where((Order.apartment_id == apartment_id) & (Order.status == 'new') & not_(Order.is_view))
        )

        if active_orders_count == 0:
            active_orders_count = None

        apartment = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        if not apartment:
            return "Apartment not found"

        bathrooms = await session.scalars(
            select(BathroomApartment).where(BathroomApartment.apartment_id == apartment_id))

        if not bathrooms:
            data = apartment.to_dict()
            data['active_order_count'] = active_orders_count
            return data

        else:

            data = apartment.to_dict()
            data['bathrooms'] = []
            data['active_order_count'] = active_orders_count

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

        object_info = await session.scalar(select(Object).where(Object.id == check_employee.object_id))
        del firestore['role']
        firestore['photo_path'] = check_employee.photo_path
        firestore['object_name'] = object_info.object_name

        return firestore
    except Exception as e:

        return e


async def get_executors_list(session):
    try:

        executors = await session.scalars(select(ExecutorsProfile))

        executors_list = []

        for executor in executors:
            executors_list.append(executor.to_dict())

        return executors_list

    except Exception as e:

        return e


async def get_executors_detail(session, staff_id):
    try:

        executor = await session.scalar(select(ExecutorsProfile).where(ExecutorsProfile.id == staff_id))

        if not executor:
            return "Executor not found"

        return executor.to_dict()

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

        rooms_collection = db.collection("rooms")
        query = rooms_collection.where("apartmentId", "==", apartment_id)

        documents = query.stream()

        for document in documents:
            document_ref = document.reference

            document_ref.update({"user_id": firestore.firestore.ArrayUnion([new_tenant.uid])})

        new_tenant_for_db = TenantProfile(
            uuid=new_tenant.uid,
            active_request=0,
            balance=0
        )
        session.add(new_tenant_for_db)
        await session.commit()

        tenant_profile = TenantApartments(
            tenant_id=new_tenant_for_db.id,
            apartment_id=apartment_id
        )

        session.add(tenant_profile)
        await session.commit()

        return new_tenant_for_db.to_dict()

    except Exception as e:

        raise e


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
                "is_view": order.is_view,
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

        orders = await session.scalars(
            select(Order)
            .where((Order.apartment_id == apartment_id) & (Order.id == order_id))
        )

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        executors = await session.scalars(select(ExecutorsProfile))

        order_dict = {}
        for order in orders:
            icon_path = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
            service = await session.scalar(select(Service).where(Service.id == order.selected_service_id))

            service_data = []
            additional_services = await session.scalars(select(AdditionalService)
                                                        .where(AdditionalService.order_id == order.id))

            for additional_service in additional_services:
                service_name = await session.scalar(select(AdditionalServiceList)
                                                    .where(AdditionalServiceList.id == additional_service.
                                                           additional_service_id))
                service_data.append(service_name.name)
            if order.id not in order_dict:
                order.is_view = True
                await session.commit()

                order_dict[order.id] = {
                    "order_id": order.id,
                    "icon_path": icon_path.big_icons_path if icon_path.big_icons_path else None,
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
                    "executors": []
                }

            for executor in executors:
                check_executor = await session.scalar(
                    select(ExecutorOrders).where(ExecutorOrders.executor_id == executor.id))
                if not check_executor:
                    data = executor.to_dict()
                    order_dict[order.id]["executors"].append(data)

        return order_dict

    except HTTPException as e:

        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


async def select_executor(user, session, order_id, executor_id, apartment_id):
    try:
        check_order = await session.scalar(select(ExecutorOrders).where(ExecutorOrders.order_id == order_id))
        order = await session.scalar(select(Order).where(Order.id == order_id))
        service = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
        if check_order:
            if check_order.executor_id != executor_id:
                check_order.executor_id = executor_id
                await session.commit()
                await pred_send_notification(user, session, order_id=order_id, apartment_id=apartment_id,
                                             executor_id=executor_id,
                                             value='replacing_executor', image=service.big_icons_path
                    if service.big_icons_path else service.mini_icons_path)
                return {"executor_id": executor_id, "order_id": order_id}
        else:
            executor = ExecutorOrders(
                executor_id=executor_id,
                order_id=order_id
            )
            session.add(executor)
            order.status = 'in progress'
            await session.commit()
            await pred_send_notification(user, session, order_id=order_id, apartment_id=apartment_id,
                                         executor_id=executor_id,
                                         value='send in progress order', image=service.big_icons_path
                if service.big_icons_path else service.mini_icons_path)
            return {"executor_id": executor.executor_id, "order_id": executor.order_id}
    except HTTPException as e:

        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


async def get_in_progress_order(session, apartment_id):
    try:

        orders = await session.scalars(
            select(Order)
            .where((Order.apartment_id == apartment_id) & (Order.status == 'in progress'))
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
            apartment_id=apartment_id,
            meter_service_id=meter_data.meter_id,
            bill_number=meter_data.bill_number,
            meters_for=meter_data.month_year,
            meter_readings=meter_data.meter_readings,
            comment=meter_data.comment,
            status='not paid'
        )
        session.add(readings)
        await session.commit()

        return readings.to_dict()
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
                apartment_id=apartment_id,
                service_id=service.id,
                photo_path="http://217.25.95.113:8000/static/icons/mini/invoice.jpg",
                bill_number=invoice_data.bill_number,
                comment=invoice_data.comment
            )

            session.add(new_invoice)
            await session.commit()

            # tenant_info = await session.scalar(
            #     select(TenantApartments).where(TenantApartments.apartment_id == apartment_id))
            #
            # if tenant_info:
            #     tenant = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant_info.tenant_id))
            #
            #     tenant.balance += invoice_data.amount
            #     await session.commit()
            #
            # await pred_send_notification(user, session, value='invoice', apartment_id=apartment_id,
            #                              image=service.big_icons_path, order_id=service.id)

            return new_invoice

        if meter_service.name == service_name:

            new_invoice = InvoiceHistory(
                amount=invoice_data.amount,
                apartment_id=apartment_id,
                meter_service_id=meter_service.id,
                photo_path="http://217.25.95.113:8000/static/icons/mini/invoice.jpg",
                bill_number=invoice_data.bill_number,
                comment=invoice_data.comment
            )
            session.add(new_invoice)
            await session.commit()

            # tenant_info = await session.scalar(
            #     select(TenantApartments).where(TenantApartments.apartment_id == apartment_id))
            #
            # if tenant_info:
            #     tenant = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant_info.tenant_id))
            #
            #     tenant.balance += invoice_data.amount
            #     await session.commit()
            #
            # await pred_send_notification(user, session, value='invoice', apartment_id=apartment_id,
            #                              image=service.big_icons_path, order_id=service.id)

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


async def get_in_progress_order_id(session, order_id, apartment_id):
    try:

        order = await session.scalar(
            select(Order)
            .where(Order.id == order_id)
        )

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))
        executor_data = []

        if order.status == 'new':
            executor_info = await session.scalars(select(ExecutorsProfile))

            for executor in executor_info:
                executor_data.append(executor.to_dict())

        elif order.status == 'in progress' or order.status == 'completed':
            active_executor = await session.scalar(select(ExecutorOrders).where(ExecutorOrders.order_id == order_id))

            executor_info = await session.scalars(select(ExecutorsProfile))

            for executor in executor_info:
                if executor.id == active_executor.executor_id:
                    executor_dict = executor.to_dict()
                    executor_dict['active'] = True
                    executor_data.append(executor_dict)
                else:
                    executor_data.append(executor.to_dict())

        icon_path = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
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
        order_dict = {
            "order_id": order.id,
            "icon_path": icon_path.big_icons_path if icon_path else None,
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

        return order_dict
    except Exception as e:
        raise e


async def get_in_progress_order_id_completed(session, order_id, apartment_id):
    try:

        order = await session.scalar(
            select(Order)
            .where((Order.apartment_id == apartment_id) & (Order.id == order_id))
        )

        order.status = 'completed'
        await session.commit()
        executor_info = await session.scalar(select(ExecutorOrders).where((ExecutorOrders.order_id == order_id)))

        executor = await session.scalar(
            select(ExecutorsProfile).where(ExecutorsProfile.id == executor_info.executor_id))

        order_dict = order.to_dict()

        order_dict['executor'] = [executor.to_dict()]

        return order.to_dict()

    except Exception as e:
        raise e


async def get_completed_orders(session, apartment_id):
    try:

        orders = await session.scalars(
            select(Order)
            .where((Order.apartment_id == apartment_id) & (Order.status == 'completed'))
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


async def get_payment_history_apartment(session, apartment_id):
    try:

        payment_history = await session.scalars(
            select(InvoiceHistory)
            .where((InvoiceHistory.apartment_id == apartment_id) & (InvoiceHistory.status == 'unpaid'))
        )

        data_list = []
        for history in payment_history:

            icon_path = ""
            if history.service_id:

                service_info = await session.scalar(select(Service).where(Service.id == history.service_id))

                icon_path += service_info.mini_icons_path

            elif history.meter_service_id:

                service_info = await session.scalar(select(MeterService).where(MeterService.id ==
                                                                               history.meter_service_id))

                icon_path += service_info.mini_icons_path

            created_at = history.issue_date.date()

            if created_at == date.today():
                name = 'Today'
            elif created_at == date.today() - timedelta(days=1):
                name = 'Yesterday'
            else:
                name = created_at.strftime('%d %h')

            apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

            data = {
                "id": history.id,
                "apartment_name": apartment_info.apartment_name,
                "created_at": f"{history.issue_date.strftime('%H:%M')}",
                "icon_path": icon_path,
                "status": history.status,
                "amount": history.amount,
            }

            if not data_list or data_list[-1]['name'] != name:
                data_list.append({'name': name, 'services': []})

            data_list[-1]['services'].append(data)
        return data_list
    except Exception as e:
        raise e


async def get_payment_history_to_paid(session, apartment_id):
    try:

        payment_history = await session.scalars(
            select(InvoiceHistory)
            .where((InvoiceHistory.apartment_id == apartment_id) & (InvoiceHistory.status == 'paid'))
        )

        data_list = []
        for history in payment_history:

            icon_path = ""
            if history.service_id:

                service_info = await session.scalar(select(Service).where(Service.id == history.service_id))

                icon_path += service_info.mini_icons_path

            elif history.meter_service_id:

                service_info = await session.scalar(
                    select(MeterService).where(MeterService.id == history.meter_service_id))

                icon_path += service_info.mini_icons_path

            created_at = history.issue_date.date()

            if created_at == date.today():
                name = 'Today'
            elif created_at == date.today() - timedelta(days=1):
                name = 'Yesterday'
            else:
                name = created_at.strftime('%d %h')

            apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

            data = {
                "id": history.id,
                "apartment_name": apartment_info.apartment_name,
                "created_at": f"{history.issue_date.strftime('%H:%M')}",
                "icon_path": icon_path,
                "status": history.status,
                "amount": history.amount,
            }

            if not data_list or data_list[-1]['name'] != name:
                data_list.append({'name': name, 'services': []})

            data_list[-1]['services'].append(data)
        return data_list
    except Exception as e:
        raise e


async def get_invoice_id(session, apartment_id, invoice_id):
    try:

        payment_history = await session.scalar(
            select(InvoiceHistory)
            .where((InvoiceHistory.apartment_id == apartment_id) & (InvoiceHistory.id == invoice_id))
        )

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        icon_path = ""
        service_name = ""
        if payment_history.service_id:

            service_info = await session.scalar(select(Service).where(Service.id == payment_history.service_id))

            icon_path += service_info.mini_icons_path
            service_name += service_info.name

        elif payment_history.meter_service_id:

            service_info = await session.scalar(select(MeterService).where(MeterService.id ==
                                                                           payment_history.meter_service_id))

            icon_path += service_info.mini_icons_path
            service_name += service_info.name

        data = {
            "id": payment_history.id,
            "apartment_name": apartment_info.apartment_name,
            "icon_path": icon_path,
            "service_name": service_name,
            "amount": payment_history.amount,
            "purpose_of_payment": payment_history.issue_date.strftime('%B %Y')
        }

        return data

    except Exception as e:
        raise e


async def paid_invoice_id(session, apartment_id, invoice_id):
    try:

        invoice = await session.scalar(
            select(InvoiceHistory)
            .where((InvoiceHistory.apartment_id == apartment_id) & (InvoiceHistory.id == invoice_id))
        )

        invoice.status = 'paid'
        invoice.photo_path = "http://217.25.95.113:8000/static/icons/mini/done_invoice.jpg"

        apartment_info_tenant = await session.scalars(select(TenantApartments)
                                                      .where(TenantApartments.apartment_id == apartment_id))

        for tenant in apartment_info_tenant:
            tenant_info = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant.tenant_id))

            tenant_info.balance += invoice.amount

            await session.commit()

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        icon_path = ""
        service_name = ""
        if invoice.service_id:

            service_info = await session.scalar(select(Service).where(Service.id == invoice.service_id))

            icon_path += service_info.mini_icons_path
            service_name += service_info.name

        elif invoice.meter_service_id:

            service_info = await session.scalar(select(MeterService).where(MeterService.id ==
                                                                           invoice.meter_service_id))

            icon_path += service_info.mini_icons_path
            service_name += service_info.name

        data = {
            "id": invoice.id,
            "apartment_name": apartment_info.apartment_name,
            "icon_path": icon_path,
            "service_name": service_name,
            "amount": invoice.amount,
            "purpose_of_payment": invoice.issue_date.strftime('%B %Y'),
        }

        return data

    except HTTPException as e:
        raise e


async def unpaid_invoice_id(session, apartment_id, invoice_id):
    try:

        invoice = await session.scalar(
            select(InvoiceHistory)
            .where((InvoiceHistory.apartment_id == apartment_id) & (InvoiceHistory.id == invoice_id))
        )

        invoice.status = 'unpaid'
        invoice.photo_path = "http://217.25.95.113:8000/static/icons/mini/invoice.jpg"

        apartment_info_tenant = await session.scalars(select(TenantApartments)
                                                      .where(TenantApartments.apartment_id == apartment_id))

        for tenant in apartment_info_tenant:
            tenant_info = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant.tenant_id))

            tenant_info.balance -= invoice.amount

            await session.commit()

        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        icon_path = ""
        service_name = ""
        if invoice.service_id:

            service_info = await session.scalar(select(Service).where(Service.id == invoice.service_id))

            icon_path += service_info.mini_icons_path
            service_name += service_info.name

        elif invoice.meter_service_id:

            service_info = await session.scalar(select(MeterService).where(MeterService.id ==
                                                                           invoice.meter_service_id))

            icon_path += service_info.mini_icons_path
            service_name += service_info.name

        data = {
            "id": invoice.id,
            "apartment_name": apartment_info.apartment_name,
            "icon_path": icon_path,
            "service_name": service_name,
            "amount": invoice.amount,
            "purpose_of_payment": invoice.issue_date.strftime('%B %Y')
        }

        return data
    except HTTPException as e:
        raise e
