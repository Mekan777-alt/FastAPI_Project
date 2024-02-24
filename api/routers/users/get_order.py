from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.responses import JSONResponse
from schemas.new_order import AdditionalServiceSchema, DocumentSchema
from config import get_session
from firebase.config import get_firebase_user_from_token
from sqlalchemy.future import select
from models.models import Order, AdditionalService, Service, Document

router = APIRouter(
    prefix="/api/v1"
)


@router.get("/get_order")
async def get_orders(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     session: AsyncSession = Depends(get_session)):

    try:
        query = await session.execute(
            select(Order, Service)
            .where(Order.tenant_id == user['uid'])
            .join(Service, Order.selected_service_id == Service.id)
            .options(
                selectinload(Order.selected_service)
            )
            .distinct()
        )

        order_result = query.fetchall()

        orders = []
        for row in order_result:
            order = row[0]
            order_data = {
                "order_id": order.id,
                "status": order.status,
                "address": order.address,
                "completion_date": order.completion_date,
                "completion_time": order.completion_time,
                "selected_services": order.selected_service.name,
                "additional_services": [
                    AdditionalServiceSchema(
                        service=additional_service.name,
                        price=additional_service.price,
                        countable=additional_service.quantity is not None,
                        quantity=additional_service.quantity if additional_service.quantity is not None else 0
                    )
                    for additional_service in await session.scalars(
                        select(AdditionalService)
                        .where(AdditionalService.order_id == order.id)
                    )
                ],
                "documents": [
                    DocumentSchema(
                        file_name=document.file_name,
                        mime_type=document.mime_type
                    )
                    for document in await session.scalars(
                        select(Document)
                        .where(Document.order_id == order.id)
                    )
                ],
                "notes": order.notes
            }
            orders.append(order_data)

        return orders
    except Exception as e:
        return JSONResponse(content=f"{e}", status_code=status.HTTP_400_BAD_REQUEST)

