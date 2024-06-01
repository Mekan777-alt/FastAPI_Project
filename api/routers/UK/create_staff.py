from fastapi import APIRouter, Depends
from typing import Annotated
from config import get_session
from firebase_admin import auth
from sqlalchemy import select
from firebase_admin import firestore
from models.base import UK, EmployeeUK
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.uk.create_employee import CreateEmployee
from firebase.config import get_firebase_user_from_token
from starlette.responses import JSONResponse
from starlette import status

router = APIRouter()


@router.post('/add_employee_uk/{obj_id}', response_model=CreateEmployee)
async def create_employee_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                             employee_data: CreateEmployee, session: AsyncSession = Depends(get_session)):
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

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_200_OK, content=str(e))
