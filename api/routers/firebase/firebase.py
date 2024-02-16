from fastapi import APIRouter
from fastapi import Request
# from config import pb
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from firebase_admin import auth

router = APIRouter(
    prefix="/api/v1"
)


@router.post("/signup", include_in_schema=False)
async def signup_user(request: Request):
    req = await request.json()
    email = req["email"]
    password = req["password"]

    if email is None or password is None:
        return HTTPException(detail={'message': 'Email or password is required'}, status_code=400)

    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return JSONResponse(content={'message': f'Successfully created user {user}'}, status_code=200)
    except Exception as e:
        return HTTPException(detail={'message': f'Error {e}'}, status_code=400)


# @router.post("/login", include_in_schema=False)
# async def login_user(request: Request):
#     req_json = await request.json()
#     email = req_json["email"]
#     password = req_json["password"]
#
#     try:
#         # user = pb.auth().sign_in_with_email_and_password(email, password)
#         # jwt = user['idToken']
#         # return JSONResponse(content={"token": jwt}, status_code=200)
#     except:
#         return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)
