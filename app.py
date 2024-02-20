import firebase_admin
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from firebase.router import router
from config import get_settings
from config import async_session_maker
from models.models import UserRole, Role


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


@app.on_event("startup")
async def startup() -> None:
    firebase_admin.initialize_app()
    async with async_session_maker() as session:
        try:
            for role in UserRole:
                db_role = Role(name=role.value)
                session.add(db_role)
            await session.commit()
        finally:
            await session.close()