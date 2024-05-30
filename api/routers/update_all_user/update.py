from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token
from typing import Annotated
from config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.base import TenantProfile, UK, EmployeeUK, PaymentDetails, ExecutorsProfile
from schemas.updateProfiles.schemas import UpdateProfiles
from firebase_admin import firestore, auth

router = APIRouter()


@router.put("/update-profiles", status_code=status.HTTP_200_OK)
async def update_profiles(user: Annotated[dict, Depends(get_firebase_user_from_token)], request: UpdateProfiles,
                          session: AsyncSession = Depends(get_session)):
    try:

        user_uid = user['uid']

        client = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user_uid))
        employee = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == user_uid))

        if client or employee:

            update_data = {}
            if request.first_last_name:
                first_name, last_name = request.first_last_name.split()
                update_data['first_name'] = first_name
                update_data['last_name'] = last_name
            if request.email:
                update_data['email'] = request.email
                check_email_fb = auth.get_user_by_email(request.email)

                if not check_email_fb:
                    auth.update_user(
                        uid=user_uid,
                        email=request.email
                    )
                else:
                    return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'Email already registered'})

            if request.phone_number:
                update_data['phone_number'] = request.phone_number

            if update_data:
                db = firestore.client()

                db.collection('users').document(user_uid).set(update_data, merge=True)

            return JSONResponse(content=update_data, status_code=status.HTTP_200_OK)
        uk = await session.scalar(select(UK).where(UK.uuid == user_uid))

        if uk:

            update_data = {}

            if request.name_of_company:
                update_data['name'] = request.name_of_company

            if update_data:
                db = firestore.client()
                db.collection('users').document(uk.uuid).set({"name": request.name_of_company}, merge=True)

            update_db = request.dict(exclude_unset=True)

            bank_details = await session.scalar(select(PaymentDetails).where(PaymentDetails.uk_id == uk.id))

            if bank_details:
                for key, value in update_db.items():
                    setattr(bank_details, key, value)

                await session.commit()

            return JSONResponse(content=update_db, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
