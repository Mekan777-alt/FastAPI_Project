from sqlalchemy.future import select
from sqlalchemy import delete
from models.base import UK, EmployeeUK, Object
from firebase.config import get_staff_firebase, delete_staff_firebase


async def get_staff_profile(session, uk_id):
    uk = await session.scalar(select(UK).where(UK.id == uk_id))

    data = {
        "UK name": uk.name
    }
    return data


async def get_objects_from_uk(session, staff):
    try:

        staff_uid = staff['uid']

        uk_id = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == staff_uid))

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


async def create_object_to_db(session, user, data):
    try:

        staff_id = user['uid']

        uk_id = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == staff_id))
        create_obj = Object(
            object_name=data.object_name,
            address=data.object_address,
            uk_id=uk_id.id
        )

        session.add(create_obj)
        await session.commit()

        return data

    except Exception as e:

        return e


async def get_staff_uk(session, user):
    try:

        staff_id = user['uid']

        uk_id = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == staff_id))

        all_staff_uuid = await session.scalars(select(EmployeeUK).where(EmployeeUK.uk_id == uk_id.uk_id))

        staff_list = []
        for staff_uk in all_staff_uuid:

            staff = await get_staff_firebase(staff_uk.uuid)

            del staff['role']
            del staff['email']
            staff['photo_path'] = staff_uk.photo_path
            staff['id'] = staff_uk.id

            staff_list.append(staff)

        data = {
            "staff_uk": staff_list
        }

        return data

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

        uk_id = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == staff_id))

        all_staff_uuid = await session.scalars(select(EmployeeUK).where(EmployeeUK.uk_id == uk_id.uk_id))

        staff_list_delete = []
        for staff_uk in all_staff_uuid:
            staff = await get_staff_firebase(staff_uk.uuid)

            del staff['role']
            del staff['email']
            del staff['phone_number']
            staff['id'] = staff_uk.id

            staff_list_delete.append(staff)

        data = {
            "staff_uk": staff_list_delete
        }

        return data

    except Exception as e:

        return None


async def get_staff_delete(session, staff_id):
    try:

        staff_uuid = await session.scalar(select(EmployeeUK.uuid).where(EmployeeUK.id == staff_id))

        delete_from_firestore = await delete_staff_firebase(staff_uuid)

        if delete_from_firestore is True:

            await session.execute(delete(EmployeeUK.id).where(EmployeeUK.id == staff_id))
            await session.commit()

            return True

        else:

            return False

    except Exception as e:

        return e