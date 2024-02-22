from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config import get_session
from schemas.new_order import OrderCreateSchema, AdditionalServiceSchema, DocumentSchema
from models.models import Order, AdditionalService, Document, Service

router = APIRouter(
    prefix="/api/v1",
    tags=["Create request"]
)

models_map = {
    "Order": Order,
    "Service": Service,
    "AdditionalService": AdditionalService,
    "Document": Document,
}

# schemas_map = {
#     "Address": Address,
#     "AdditionalService": AdditionalService,
#     "Document": DocumentSchema,
# }


async def get_model_id(session: AsyncSession, model_name: str, model_data: str) -> int:
    model = models_map[model_name]

    result = await session.execute(select(model).where(model.name == model_data))
    db_model = result.scalar()

    if db_model:
        return db_model.id
    else:
        db_model = model(name=model_data)
        session.add(db_model)
        await session.commit()
        await session.refresh(db_model)
        return db_model.id


@router.post("/new_order")
async def create_order(order_data: OrderCreateSchema, session: AsyncSession = Depends(get_session)):
    try:
        order = Order(
            tenant_id=order_data.customer_id,
            address=order_data.address,
            completion_date=order_data.completion_date,
            completion_time=order_data.completion_time,
            notes=order_data.notes,
            status=order_data.status,
            selected_service_id=await get_model_id(session, "Service", order_data.selected_services),
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)

        for additional_service_data in order_data.additional_services:
            additional_service = AdditionalService(
                order_id=order.id,
                service_id=await get_model_id(session, "Service", order_data.selected_services),
                quantity=additional_service_data.quantity,
                name=additional_service_data.service,
                price=additional_service_data.price
            )
            session.add(additional_service)

        await session.commit()

        for document_data in order_data.documents:
            document = Document(
                order_id=order.id,
                file_name=document_data.file_name,
                mime_type=document_data.mime_type,
            )
            session.add(document)

        await session.commit()

        return order

    except Exception as e:
        print(e)
