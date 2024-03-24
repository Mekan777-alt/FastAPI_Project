from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import firestore
from firebase_admin.auth import verify_id_token
from starlette import status
from sqlalchemy.future import select
from starlette.responses import JSONResponse
from models.base import TenantProfile, EmployeeUK, UK, ExecutorsProfile

bearer_scheme = HTTPBearer(auto_error=False)


def get_firebase_user_from_token(
        token: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> dict:
    try:
        if not token:
            raise ValueError("No token")
        user = verify_id_token(token.credentials)
        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in or Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def register_user(user, session):
    try:
        db = firestore.client()
        docs = db.collection("users").document(f"{user['uid']}").get()
        data = docs.to_dict()

        if data['role'] == 'Tenant':
            query = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user['uid']))

            if not query:
                user = TenantProfile(
                    uuid=user['uid'],
                    photo_path='null',
                    active_request=0,
                    balance=0
                )

                session.add(user)
                await session.commit()

                return data

            return data

        elif data['role'] == 'Employee':

            query = await session.scalar(select(EmployeeUK).where(EmployeeUK.uuid == user['uid']))

            if not query:
                employee = EmployeeUK(
                    uuid=user['uid'],
                    uk_id=1,
                    photo_path='null',
                    object_id=1
                )

                session.add(employee)
                await session.commit()

                return data

            return data

        elif data['role'] == 'Company':

            query = await session.scalar(select(UK).where(UK.uuid == user['uid']))

            if not query:
                uk = UK(
                    uuid=user['uid'],
                    photo_path='null',
                    name=data['name']
                )
                session.add(uk)
                await session.commit()

                return data

            return data

        elif data['role'] == 'staff':

            query = await session.scalar(select(ExecutorsProfile).where(ExecutorsProfile.uuid == user['uid']))

            if not query:
                staff = ExecutorsProfile(
                    uuid=user['uid'],
                    photo_path='null',
                    specialization=data['specialization']
                )
                session.add(staff)
                await session.commit()

                return data

            return data

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


async def get_staff_firebase(staff_id):
    try:
        db = firestore.client()
        docs = db.collection("users").document(f"{staff_id}").get()
        data = docs.to_dict()

        return data

    except Exception as e:

        return e


async def delete_staff_firebase(staff_uid):
    try:
        db = firestore.client()
        db.collection("users").document(f"{staff_uid}").delete()

        return True

    except Exception as e:

        return e