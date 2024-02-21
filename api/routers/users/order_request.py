from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1"
)


@router.post("/new_order")
async def create_order():
    pass
