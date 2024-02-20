from typing import Annotated
from fastapi import FastAPI, APIRouter, Depends, Request, HTTPException
from starlette.responses import JSONResponse
from config import get_firebase_user_from_token, pb, read
router = APIRouter(
    prefix="/api/v1"
)


@router.post("/login")
async def login_user(request: Request):
    req_json = await request.json()
    email = req_json["email"]
    password = req_json["password"]

    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        return JSONResponse(content={"token": jwt}, status_code=200)
    except:
        return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)


@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    user_role = read(user)

    return {"role": user_role["role"]}