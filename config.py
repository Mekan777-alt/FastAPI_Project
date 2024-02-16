import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DBUSER')}:{os.getenv('DBPASSWORD')}@{os.getenv('DBHOST')}/{os.getenv('DBNAME')}"
engine = create_async_engine(DATABASE_URL, echo=False)
Session = sessionmaker(
    engine=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# cred = credentials.Certificate("test_service_account_keys.json")
# firebase = firebase_admin.initialize_app(cred)
# pb = pyrebase.initialize_app(json.load(open("firebase_config.json")))
