import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from api.routers.users.routers import user_router
from firebase.router import router as firebase_router
from config import cred
from api.routers.UK.routers import admin_router
from api.routers.Employee.routers import employee_router
from api.routers.chat.routers import chat_router

app = FastAPI()

app.include_router(user_router)
app.include_router(firebase_router)
app.include_router(admin_router)
app.include_router(employee_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

firebase_admin.initialize_app(cred)

app.mount('/static', StaticFiles(directory='static'), name='static')
