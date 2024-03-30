from models.base import EmployeeUK, TenantApartments, TenantProfile
from sqlalchemy.future import select
from models.base import Object, ApartmentProfile, ExecutorsProfile
from firebase.config import get_staff_firebase
from firebase_admin import auth, firestore


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

        apartment_list = await session.scalars(select(ApartmentProfile).where(ApartmentProfile.object_id == object_id.id))

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

        employee = user['uid']

        check_employee = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == employee))

        if not check_employee:

            return "Employee not found"

        apartment = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        if not apartment:

            return "Apartment not found"

        data = {
            "apartment_name": apartment.apartment_name,
            "area": apartment.area
        }

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
        del firestore['is_admin']
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

        return e
