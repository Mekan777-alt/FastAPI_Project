from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from firebase.config import get_firebase_user_from_token, get_staff_firebase
from config import get_session
from sqlalchemy import select
from models.base import TenantProfile, TenantApartments, Object, ApartmentProfile, InvoiceHistory
from starlette import status
from .config import get_finance_from_user
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('/pay')
async def get_pay(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                  session: AsyncSession = Depends(get_session)):
    try:

        data = await get_finance_from_user(session, user)

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/pay/history')
async def get_history_invoice(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                              session: AsyncSession = Depends(get_session)):
    try:
        user_profile = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user['uid']))
        tenant_info = await session.scalar(select(TenantApartments).where(TenantApartments.tenant_id == user_profile.id))
        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == tenant_info.apartment_id))

        invoice_info = await session.scalars(select(InvoiceHistory)
                                             .where((InvoiceHistory.apartment_id == apartment_info.id) &
                                                    (InvoiceHistory.status == 'paid')))
        data_list = []
        for invoice in invoice_info:

            invoice_history_data = {
                "id": invoice.id,
                "name": "Invoice",
                "amount": invoice.amount,
                "icon_path": invoice.photo_path,
                "comment": invoice.comment if invoice.comment else None,
                "total_pay": user_profile.pay_balance
            }
            data_list.append(invoice_history_data)
        return data_list
    except HTTPException as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)
