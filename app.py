import firebase_admin
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from firebase.router import router as firebase_router
from config import cred, get_session
from api.routers.users.contact import router as contact_router
from api.routers.users.order_request import router as order_router
from api.routers.users.profile import router as profile_router
from models.models import Service, ServiceEnum

app = FastAPI()

app.include_router(firebase_router)
app.include_router(order_router)
app.include_router(profile_router)
app.include_router(contact_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

firebase_admin.initialize_app(cred)

