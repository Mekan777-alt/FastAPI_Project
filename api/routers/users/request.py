from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1"
)


@router.post("")
async def post_request():
    pass


@router.get("")
async def get_request():
    pass