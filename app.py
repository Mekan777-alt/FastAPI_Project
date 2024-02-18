from auth.database import User
from auth.manager import get_user_manager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.auth import auth_backend
from fastapi_users import FastAPIUsers
from auth.schemas import UserRead, UserCreate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/v1",
    tags=["auth"])

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1",
    tags=["register"]
)

