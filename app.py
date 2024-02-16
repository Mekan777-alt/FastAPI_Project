from config import Session, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.users import request
from api.routers.firebase import firebase
from models.models import Base


app = FastAPI(
    title="TitleAPP",
    docs_url="/api/docs",
)


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    db_session = Session(engine)
    try:
        yield db_session
    except Exception as e:
        print(f"Error {e}")
    finally:
        await db_session.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router=firebase.router)
app.include_router(router=request.router)


@app.on_event("startup")
async def startup_event():
    await init()

