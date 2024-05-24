import firebase_admin.auth
from sqlalchemy.future import select
from sqlalchemy import delete
from models.base import (UK, EmployeeUK, Object, ServiceObjectList, ApartmentProfile, PaymentDetails, Service, News,
                         NotificationEmployee, NotificationUK)
from firebase.config import get_staff_firebase, delete_staff_firebase
from api.routers.users.config import get_contacts_from_db
from firebase_admin import auth, firestore


async def get_uk_profile(session, uk_id):
    uk = await session.scalar(select(UK).where(UK.id == uk_id))
    payment_details = await session.scalar(select(PaymentDetails).where(PaymentDetails.uk_id == uk_id))
    news = await session.scalars(select(News).where(News.uk_id == uk_id))
    if not payment_details:
        requisites = {}
    else:
        requisites = {
            "recipient": payment_details.recipient_name,
            "inn": payment_details.inn,
            "kpp": payment_details.kpp,
            "account": payment_details.account,
            "bic": payment_details.bic,
            "correspondent_account": payment_details.correspondent_account,
            "okpo": payment_details.okpo,
            "bank_name": payment_details.bank_name
        }
    data = {
        "uk_name": uk.name,
        "photo_path": uk.photo_path,
        "requisites": requisites,
        # "news": []
    }
    # for n in news:
    #     data['news'].append(n.to_dict())
    return data


async def get_objects_from_uk(session, staff):
    try:

        uk_uid = staff['uid']

        uk_id = await session.scalar(select(UK).where(UK.uuid == uk_uid))

        objects = await session.scalars(select(Object).where(Object.uk_id == int(uk_id.id)))

        objects_list = []
        for obj in objects:
            object_dict = {
                "id": obj.id,
                "object_address": obj.address,
                "object_name": obj.object_name
            }
            objects_list.append(object_dict)

        data = {
            "objects": objects_list
        }

        return data

    except Exception as e:

        return e


async def get_staff_uk(session, user):
    try:

        uk_id = user['uid']

        uk_id_fromdb = await session.scalar(select(UK).where(UK.uuid == uk_id))

        all_staff_uuid = await session.scalars(select(EmployeeUK).where((EmployeeUK.uk_id == uk_id_fromdb.id)
                                                                        & (EmployeeUK.is_archive == False)))

        staff_list = []
        for staff_uk in all_staff_uuid:
            staff = await get_staff_firebase(staff_uk.uuid)

            del staff['role']
            del staff['email']
            staff['photo_path'] = staff_uk.photo_path
            staff['id'] = staff_uk.id

            staff_list.append(staff)

        return staff_list

    except Exception as e:

        return e


async def get_staff_uk_id(session, staff_id):
    try:

        staff = await session.scalar(select(EmployeeUK).where(EmployeeUK.id == staff_id))

        obj = await session.scalar(select(Object).where(Object.id == staff.object_id))

        data = await get_staff_firebase(staff.uuid)

        del data['role']
        data['photo_path'] = staff.photo_path
        data['object_name'] = obj.object_name

        return data

    except Exception as e:

        return None


async def get_staff_delete_list(session, user):
    try:

        staff_id = user['uid']

        uk_id = await session.scalar(select(UK).where(UK.uuid == staff_id))

        all_staff_uuid = await session.scalars(select(EmployeeUK).where((EmployeeUK.uk_id == uk_id.id) &
                                                                        (EmployeeUK.is_archive == False)))

        staff_list_delete = []
        for staff_uk in all_staff_uuid:
            staff = await get_staff_firebase(staff_uk.uuid)

            del staff['role']
            del staff['email']
            del staff['phone_number']
            staff['id'] = staff_uk.id

            staff_list_delete.append(staff)

        return staff_list_delete

    except Exception as e:

        return None


async def get_staff_delete(session, staff_id):
    try:

        staff_uuid = await session.scalar(select(EmployeeUK.uuid).where(EmployeeUK.id == staff_id))

        delete_from_firestore = await delete_staff_firebase(staff_uuid)

        if delete_from_firestore is True:

            await session.execute(delete(EmployeeUK).where(EmployeeUK.id == staff_id))
            await session.commit()

            return True

        else:

            return False

    except Exception as e:

        return e


async def get_profile_uk(session, user):
    try:

        uk_id = await session.scalar(select(UK).where(UK.uuid == user['uid']))

        profile = await get_uk_profile(session, uk_id.id)

        contact = await get_contacts_from_db(session)

        profile['contacts'] = contact

        return profile

    except Exception as e:

        return e


async def get_object_id(session, object_id):
    try:

        object = await session.scalar(select(Object).where(Object.id == object_id))

        data = {
            'id': object.id,
            'object_name': object.object_name,
            'object_address': object.address,
            'main_photo_path': object.photo_path,
            'list_services': []
        }

        services = await session.scalars(select(ServiceObjectList).where(ServiceObjectList.object_id == object.id))

        for service in services:
            service_id = await session.scalar(select(Service).where(Service.id == service.service_id))

            data['list_services'].append({"id": service_id.id, "service_name": service_id.name})

        return data

    except Exception as e:

        return e


async def get_apartments_from_object(session, object_id):
    try:

        apartments = await session.scalars(select(ApartmentProfile).where(ApartmentProfile.object_id == object_id))

        apartments_list = []
        for apartment in apartments:
            apartment_dict = {
                "id": apartment.id,
                "apartment_name": apartment.apartment_name,
                "area": apartment.area

            }
            apartments_list.append(apartment_dict)

        data = {
            'apartments': apartments_list
        }
        return data
    except Exception as e:

        return e


async def create_apartment_for_object(session, object_id, apartment_data):
    try:

        apartment = ApartmentProfile(
            object_id=object_id,
            apartment_name=apartment_data.apartment_name,
            area=apartment_data.area
        )
        session.add(apartment)
        await session.commit()

        data = {
            "id": apartment.id,
            "apartment_name": apartment.apartment_name,
            "area": apartment.area
        }

        return data

    except Exception as e:

        return e


async def create_employee(session, employee_data, user):
    try:
        new_user = auth.create_user(
            email=employee_data.email,
            password=employee_data.password
        )
        collections_path = "users"

        db = firestore.client()
        user_doc = db.collection(collections_path).document(new_user.uid)

        first_last_name = employee_data.first_last_name.split()

        user_data = {
            "email": employee_data.email,
            "phone_number": employee_data.phone_number,
            "first_name": first_last_name[0],
            "last_name": first_last_name[1],
            "role": "Employee"
        }
        user_doc.set(user_data)

        uk_id = await session.scalar(select(UK).where(UK.uuid == user['uid']))

        new_employee = EmployeeUK(
            uuid=new_user.uid,
            uk_id=uk_id.id,
            photo_path='null',
            object_id=employee_data.object_id,
            is_admin=False
        )

        session.add(new_employee)
        await session.commit()

        return new_employee.to_dict()

    except (ValueError, TypeError, firebase_admin.auth.UserNotFoundError) as e:

        return str(e)


async def get_staff_object(session, object_id):
    try:

        staff_info = await session.scalars(select(EmployeeUK).where(EmployeeUK.object_id == object_id))

        data = []

        for employee in staff_info:
            employee_data = await get_staff_firebase(employee.uuid)
            del employee_data['role']
            del employee_data['email']

            employee_data['id'] = employee.id
            employee_data['photo_path'] = employee.photo_path
            data.append(employee_data)

        return data
    except (ValueError, TypeError, firebase_admin.auth.UserNotFoundError) as e:
        raise e


async def get_staff_id_object(session, object_id, staff_id):
    try:

        staff_info = await session.scalar(select(EmployeeUK).where(
            (EmployeeUK.id == staff_id) & (EmployeeUK.object_id == object_id)))

        if staff_info is None:
            return "Staff ID not found"

        object_info = await session.scalar(select(Object).where(Object.id == staff_info.object_id))

        staff_data = await get_staff_firebase(staff_info.uuid)
        del staff_data['role']

        staff_data['id'] = staff_info.id
        staff_data['photo_path'] = staff_info.photo_path
        staff_data['object_name'] = object_info.object_name

        return staff_data
    except (ValueError, TypeError, firebase_admin.auth.UserNotFoundError) as e:
        raise e


async def get_all_news(session, uk):
    try:

        uk_uid = uk['uid']

        uk_info = await session.scalar(select(UK).where(UK.uuid == uk_uid))

        if not uk_info:
            return "company not found"

        news = await session.scalars(select(News).where(News.uk_id == uk_info.id))

        news_list = []

        for n in news:
            news_list.append(n.to_dict())
        return news_list
    except Exception as e:
        raise e


async def get_news_id(session, uk, news_id):
    try:
        if uk['role'] == 'Company':
            uk_uid = uk['uid']
            uk_info = await session.scalar(select(UK).where(UK.uuid == uk_uid))

            if uk_info is not None:
                news = await session.scalar(select(News)
                                            .where((News.uk_id == uk_info.id) & (News.id == news_id)))

                if not news:
                    return "News not found"

                db = firestore.client()
                query = db.collection('notifications').where('id', '==', f'{news_id}')

                result = query.stream()

                for doc in result:

                    data = doc.to_dict()

                    if data['screen'] == 'news':
                        view = data['is_view']['company']
                        db.collection("notifications").document(doc.id).update({f'{view}': True})
                local_notify = await session.scalar(select(NotificationUK).where(
                    (NotificationUK.content_id == news_id) & (NotificationUK.type == 'news')))

                if not local_notify:
                    print("Notification not found")

                local_notify.is_view = True
                await session.commit()

                return news.to_dict()

        elif uk['role'] == 'Employee':
            employee_uid = uk['uid']
            employee_info = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee_uid))

            if employee_info is not None:
                news = await session.scalar(select(News).where((News.id == news_id)
                                                               & (News.uk_id == employee_info.uk_id)))

                if not news:
                    return "News not found"

                db = firestore.client()
                query = db.collection('notifications').where('id', '==', f'{news_id}')

                result = query.stream()

                for doc in result:

                    data = doc.to_dict()

                    if data['screen'] == 'news':
                        view = data['is_view']['employee']
                        db.collection("notifications").document(doc.id).update({f'{view}': True})

                local_notify = await session.scalar(select(NotificationEmployee)
                                                    .where((NotificationEmployee.content_id == news_id) &
                                                           (NotificationEmployee.type == 'news')))
                if not local_notify:
                    print("Notification not found")

                local_notify.is_view = True
                await session.commit()

                return news.to_dict()
    except Exception as e:
        raise e
