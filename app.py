import os
import pathlib
from functools import lru_cache

import firebase_admin
from pydantic_settings import BaseSettings

from auth.database import User
from auth.manager import get_user_manager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth.auth import auth_backend
from fastapi_users import FastAPIUsers
from auth.schemas import UserRead, UserCreate
from firebase.router import router
from config import get_settings


app = FastAPI()

app.include_router(router)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
#
# fastapi_users = FastAPIUsers[User, int](
#     get_user_manager,
#     [auth_backend]
# )
#
# app.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix="/api/v1",
#     tags=["auth"])
#
# app.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
#     prefix="/api/v1",
#     tags=["register"]
# )
#
# app.include_router(
#     fastapi_users.get_verify_router(UserRead),
#     prefix="/api/v1",
#     tags=["verify"]
# )
#
# app.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )


class Settings(BaseSettings):
    """Main settings"""
    app_name: str = "firebase"
    env: str = os.getenv("ENV", "development")
    # Needed for CORS
    frontend_url: str = os.getenv("FRONTEND_URL", "NA")


@lru_cache
def get_settings() -> Settings:
    """Retrieves the fastapi settings"""
    return Settings()

firebase_admin.initialize_app()

print("Current App Name:", firebase_admin.get_app().project_id)