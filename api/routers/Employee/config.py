from models.base import EmployeeUK
from sqlalchemy.future import select
from models.base import Object


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
