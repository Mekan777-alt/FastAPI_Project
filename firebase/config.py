from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import firestore
from firebase_admin.auth import verify_id_token
from starlette import status
from sqlalchemy.future import select
from starlette.responses import JSONResponse

from models.models import TenantProfile, Object, ApartmentProfile, TenantApartments

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


async def get_user(user, session):
    try:
        db = firestore.client()
        docs = db.collection("users").document(f"{user['uid']}").get()
        data = docs.to_dict()

        if data['role'] == 'Tenant':
            query = await session.execute(select(TenantProfile).where(TenantProfile.uuid == user['uid']))
            tenant = query.scalar()

            balance = tenant.balance

            data["balance"] = balance

            return data
        elif data['role'] == 'UK staff':

            return data

        elif data['role'] == 'Object staff':

            return data

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=str(e))


async def get_user_profile(session, user_id, new_value=None):
    apartment_id = await session.execute(select(TenantApartments, ApartmentProfile, Object).
                                         join(ApartmentProfile).join(Object).select_from(TenantApartments)
                                         .where(TenantProfile.id == user_id))
    active_request = await session.execute(select(TenantProfile.active_request).where
                                           (TenantProfile.id == user_id))

    result = apartment_id.fetchall()
    active_request_result = active_request.fetchone()
    data_to_return = []
    for tenant_profile, apartment_profile, object_profile in result:
        data = {
            "object_address": object_profile.address,
            "active_request": active_request_result[0],
            "apartment_name": []
        }
        data["apartment_name"].append(apartment_profile.apartment_name)
        data_to_return.append(data)
    return data_to_return
