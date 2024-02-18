import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_NAME = os.getenv("DBNAME")
DB_USER = os.getenv("DBUSER")
DB_PASSWORD = os.getenv("DBPASSWORD")
DB_HOST = os.getenv("DBHOST")
DB_PORT = os.getenv("DBPORT")


DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DBUSER')}:{os.getenv('DBPASSWORD')}@{os.getenv('DBHOST')}/{os.getenv('DBNAME')}"
engine = create_async_engine(DATABASE_URL, echo=False)
Session = sessionmaker(
    engine=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

