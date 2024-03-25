from fastapi import APIRouter, Depends
from typing import Annotated
from config import get_session
from api.routers.UK.config import create_employee
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.uk.create_employee import CreateEmployee
from firebase.config import get_firebase_user_from_token
from starlette.responses import JSONResponse
from starlette import status

router = APIRouter(
    prefix='/api/v1'
)


@router.post('/add_employee_uk/{obj_id}', response_model=CreateEmployee)
async def create_employee_uk(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                             employee_data: CreateEmployee, session: AsyncSession = Depends(get_session)):
    try:

        data = await create_employee(session, employee_data, user)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)

    except Exception as e:

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
