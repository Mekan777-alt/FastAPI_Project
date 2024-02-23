from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token, get_user, get_user_profile
from config import pb, get_session

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
    user_role = get_user(user)
    try:
        if user_role["role"] == "Tenant":
            data = await get_user_profile(session, user['uid'])
            return JSONResponse(content=data, status_code=status.HTTP_200_OK)
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


