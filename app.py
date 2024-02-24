import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase.router import router
from config import cred
from api.routers.users.order_request import router as order_request
from api.routers.users.get_order import router as get_order

app = FastAPI()

app.include_router(router)
app.include_router(order_request)
app.include_router(get_order)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

firebase_admin.initialize_app(cred)