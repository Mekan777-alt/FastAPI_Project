from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.firebase import firebase


app = FastAPI(
    title="TitleAPP",
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router=firebase.router)
