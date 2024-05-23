import json
import os
import pyrebase
from dotenv import load_dotenv
from fastapi import HTTPException
from firebase_admin import credentials
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from models.base import ApartmentProfile, TenantApartments


load_dotenv()


DB_NAME = os.getenv("DBNAME")
DB_USER = os.getenv("DBUSER")
DB_PASSWORD = os.getenv("DBPASSWORD")
DB_HOST = os.getenv("DBHOST")
DB_PORT = os.getenv("DBPORT")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)

cred = credentials.Certificate("app-house-d0ac1-firebase-adminsdk-g0nda-1e43074d18.json")
pb = pyrebase.initialize_app(json.load(open("test_config.json")))


async def get_session() -> AsyncSession:
    async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session


async def check_user(tenant_id: str, session, apartment_id: int):
    try:
        apartment_model = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

        if not apartment_model:
            raise HTTPException(status_code=404, detail="Apartment not found")

        tenant_model = await session.scalar(select(TenantApartments).where(
            (TenantApartments.apartment_id == apartment_model.id)))

        if tenant_model:
            return tenant_model.tenant_id

        return False

    except SQLAlchemyError as e:
        raise e
    except HTTPException as e:
        raise e

