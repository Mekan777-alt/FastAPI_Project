from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy.future import select
from models.base import TenantProfile, EmployeeUK, UK
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token, register_user
from api.routers.UK.config import get_uk_profile
from api.routers.users.config import get_user_profile
from config import pb, get_session
from api.routers.Employee.config import get_employee_profile

router = APIRouter(
    prefix="/api/v1",
    tags=['Login']
)


# @router.post("/login")
# async def login_user(request: Request):
#     req_json = await request.json()
#     email = req_json["email"]
#     password = req_json["password"]
#
#     try:
#         user = pb.auth().sign_in_with_email_and_password(email, password)
#         jwt = user['idToken']
#         return JSONResponse(content={"token": jwt}, status_code=200)
#     except:
#         return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)


@router.get("/login", include_in_schema=False)
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     session: AsyncSession = Depends(get_session)):
    user_role = await register_user(user, session)

    try:
        if user_role["role"] == "Tenant":

            tenant_id = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user['uid']))

            data = await get_user_profile(session, tenant_id.id)

            return JSONResponse(content=data, status_code=status.HTTP_200_OK)

        elif user_role['role'] == "Company":

            uk_id = await session.scalar(select(UK).where(UK.uuid == user['uid']))

            data = await get_uk_profile(session, uk_id.id)

            return JSONResponse(content=data)

        elif user_role["role"] == "Employee":

            staff_id = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == user['uid']))

            data = await get_employee_profile(session, user_role, staff_id.object_id)

            return JSONResponse(content=data)

    except Exception as e:
        return HTTPException(detail={'message': f'{e}'}, status_code=400)


# @router.post("/register")
# async def register_user(request: Request):
#     req_json = await request.json()
#     user = get_user(req_json)
#
#     try:
#         db = async_session_maker()
#         if user['role'] == "Tenant":
#             new_user = TenantProfile(
#                 uuid=req_json['uuid'],
#                 apartment_id=1
#             )
#             db.add(new_user)
#             await db.commit()
#             await db.close()
#     except Exception as e:
#         print(e)
#     return user


