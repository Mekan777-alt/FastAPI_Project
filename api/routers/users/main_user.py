from fastapi import APIRouter


router = APIRouter(
    prefix="/api/v1"
)


@router.get("/user")
async def main_user():
    pass
