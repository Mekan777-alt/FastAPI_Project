import firebase_admin
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import firestore

from firebase.router import router
from config import get_settings, cred
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
    firebase_admin.initialize_app(cred)
    async with async_session_maker() as session:
        try:
            if not UserRole:
                for role in UserRole:
                    db_role = Role(name=role.value)
                    session.add(db_role)
                await session.commit()
            else:
                pass
        finally:
            await session.close()