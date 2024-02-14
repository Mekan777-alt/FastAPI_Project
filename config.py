from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from firebase_admin import credentials
import json
import pyrebase
import firebase_admin

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/asyncalchemy" #os.environ.get('DATABASE_URL')
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine=engine, class_=AsyncSession, expire_on_commit=False
)

cred = credentials.Certificate("test_service_account_keys.json")
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open("firebase_config.json")))
