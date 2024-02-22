import firebase_admin
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from firebase.router import router
from config import get_settings, cred
from api.routers.users.order_request import router as order_request

app = FastAPI()

app.include_router(router)
app.include_router(order_request)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

firebase_admin.initialize_app(cred)