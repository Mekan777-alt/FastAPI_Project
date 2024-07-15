from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy.future import select
from models.base import TenantProfile, EmployeeUK, UK
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token, register_user, send_mail, save_code_for_db, search_user
from api.routers.UK.config import get_uk_profile
from api.routers.users.config import get_user_profile
from models.config import get_session
from config import pb
from api.routers.Employee.config import get_employee_profile
from schemas.forgot_password.schemas import ForgotPassword, EnterCode
from firebase_admin import auth
import random

router = APIRouter(
    prefix="/api/v1",
    tags=['Login']
)


@router.post("/login", include_in_schema=False)
async def login_user(request: Request):
    req_json = await request.json()
    email = req_json["email"]
    password = req_json["password"]
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        access_token = user['idToken']
        refresh_token = user['refreshToken']
        return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token}, status_code=200)
    except:
        return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)


@router.get("/login", include_in_schema=False)
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     device_token: Annotated[str, Header(...)], session: AsyncSession = Depends(get_session)):
    user_role = await register_user(user, session, device_token)

    try:
        if user_role["role"] == "client":

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

        elif user_role["role"] == "staff":

            return JSONResponse(status_code=status.HTTP_200_OK, content=user_role)

    except Exception as e:
        return HTTPException(detail={'message': f'{e}'}, status_code=400)


@router.post("/forgot-password")
async def forgot_password(request: ForgotPassword, session: AsyncSession = Depends(get_session)):
    try:

        user = auth.get_user_by_email(request.email)

        reset_code = str(random.randint(100000, 999999))

        save_code = await save_code_for_db(session, user.uid, reset_code)

        if save_code is True:

            send_mail_to_user = await send_mail(user.email, reset_code)

            if send_mail_to_user is True:

                return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password reset sent"})

        return JSONResponse(content="Error user not found from db", status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:

        return HTTPException(detail={'message': f'{e}'}, status_code=200)


@router.post("/enter-code")
async def new_password_enter_code(request: EnterCode, session: AsyncSession = Depends(get_session)):
    try:

        code = request.code

        user_uid = await search_user(session, code)

        if user_uid is not None and user_uid is not False:

            auth.update_user(
                uid=user_uid,
                password=request.new_password,
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password entered successfully"})

    except Exception as e:

        return HTTPException(detail={'message': f'{e}'}, status_code=400)


@router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                 session: AsyncSession = Depends(get_session)):
    try:

        user_uuid = user['uid']

        client = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user_uuid))

        if client:

            client.device_token = None
            await session.commit()

            return "Done"

        uk = await session.scalar(select(UK).where(UK.uuid == user_uuid))

        if uk:

            uk.device_token = None
            await session.commit()

            return "Done"

        employee = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == user_uuid))

        if employee:

            employee.device_token = None
            await session.commit()

            return "Done"

        return JSONResponse(status_code=status.HTTP_404_BAD_REQUEST, content=str('User not found'))
    except Exception as e:
        return HTTPException(detail={'message': f'{e}'}, status_code=400)
