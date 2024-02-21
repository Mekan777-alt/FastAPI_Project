import json
import os
from functools import lru_cache
from typing import Annotated, Optional, AsyncGenerator
import pyrebase
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import credentials
from firebase_admin.auth import verify_id_token
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from firebase_admin import firestore

load_dotenv()

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


bearer_scheme = HTTPBearer(auto_error=False)


def get_firebase_user_from_token(
    token: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> Optional[dict]:
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


DB_NAME = os.getenv("DBNAME")
DB_USER = os.getenv("DBUSER")
DB_PASSWORD = os.getenv("DBPASSWORD")
DB_HOST = os.getenv("DBHOST")
DB_PORT = os.getenv("DBPORT")


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@db:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

cred = credentials.Certificate("app-house-d0ac1-firebase-adminsdk-g0nda-1e43074d18.json")
pb = pyrebase.initialize_app(json.load(open("test_config.json")))


def get_user(user):
    db = firestore.client()
    doc = db.collection("users").document(f"{user['uid']}").get()
    return doc.to_dict()
