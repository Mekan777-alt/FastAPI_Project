from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy.future import select
from config import get_session
from starlette.responses import JSONResponse
from models.models import Contacts

router = APIRouter(
    prefix="/api/v1",
    tags=["Contacts"]
)


@router.get('/contacts')
async def get_contacts(session: AsyncSession = Depends(get_session)):

    try:

        contacts = await session.execute(select(Contacts))

        db_contacts = contacts.scalars()

        contacts_data = []
        for contact in db_contacts:
            contact_data = {
                "name": contact.name,
                "description": contact.description,
                "email": contact.email if contact.email is not None else "null",
                "phone": contact.phone if contact.phone is not None else "null"
            }
            contacts_data.append(contact_data)

        return JSONResponse(content=contacts_data, status_code=status.HTTP_200_OK)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
