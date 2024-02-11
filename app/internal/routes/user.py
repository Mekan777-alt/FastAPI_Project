from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1"
)


@router.get("/views")
async def views():

    return {
        "message": "Hello world!"
    }
