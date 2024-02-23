from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import firestore
from firebase_admin.auth import verify_id_token
from starlette import status
from sqlalchemy.future import select
from models.models import TenantProfile, Object, ApartmentProfile

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


def get_user(user):
    db = firestore.client()
    doc = db.collection("users").document(f"{user['uid']}").get()
    return doc.to_dict()


async def get_user_profile(session, user_uid, new_value=None):
    apartment_id = await session.execute(select(TenantProfile, ApartmentProfile, Object).
                                         join(ApartmentProfile).join(Object).select_from(TenantProfile)
                                         .where(TenantProfile.uuid == user_uid))
    active_request = await session.execute(select(TenantProfile.active_request).where
                                           (TenantProfile.uuid == user_uid))

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
