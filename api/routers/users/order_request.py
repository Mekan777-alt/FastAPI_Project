from typing import Annotated
from sqlalchemy import update
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token, get_user_profile
from config import get_session, check_user
from schemas.new_order import OrderCreateSchema
from models.models import Order, AdditionalService, Document, Service, TenantProfile

router = APIRouter(
    prefix="/api/v1",
    tags=["Order"]
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
async def create_order(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       order_data: OrderCreateSchema, session: AsyncSession = Depends(get_session)):
    tenant_id = await check_user(user["uid"], session)

    try:
        order = Order(
            tenant_id=tenant_id,
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

        query = (
            update(TenantProfile)
            .where(
                (TenantProfile.uuid == tenant_id)
            )
            .values({"active_request": TenantProfile.active_request + 1})
            .returning(TenantProfile.active_request)
        )
        await session.execute(query)
        await session.commit()

        data = await get_user_profile(session, tenant_id)
        return JSONResponse(content=data, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        return JSONResponse(content=f"Error create order {e}", status_code=status.HTTP_400_BAD_REQUEST)
