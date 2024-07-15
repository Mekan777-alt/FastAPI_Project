from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import settings

DATABASE_URL = (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:"
                f"{settings.DB_PORT}/{settings.DB_NAME}")
engine = create_async_engine(DATABASE_URL)


async def get_session() -> AsyncSession:
    async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
