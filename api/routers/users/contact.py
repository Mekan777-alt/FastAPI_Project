from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config import get_session
from starlette.responses import JSONResponse
from api.routers.users.config import get_contacts_from_db

router = APIRouter()


@router.get('/contacts')
async def get_contacts(session: AsyncSession = Depends(get_session)):

    try:

        contacts_data = await get_contacts_from_db(session)

        return JSONResponse(content=contacts_data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
