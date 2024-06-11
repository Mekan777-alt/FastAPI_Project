from typing import Annotated
from sqlalchemy import update
from api.routers.users.get_order import router
from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import JSONResponse
from firebase.config import get_firebase_user_from_token
from .config import get_user_profile
from config import get_session
from firebase.notification import pred_send_notification
from schemas.user.new_order import OrderCreateSchema
from models.base import Order, AdditionalService, Document, Service, TenantProfile, OrderFromTenant, ApartmentProfile

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


@router.post("/create_order")
async def create_order(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       order_data: OrderCreateSchema, session: AsyncSession = Depends(get_session)):

    try:

        tenant_uid = user['uid']

        tenant_profile = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == tenant_uid))
        if not tenant_profile:
            return "Tenant not found"

        order = Order(
            apartment_id=order_data.apartment_id,
            completion_date=order_data.completion_date,
            completion_time=order_data.completion_time,
            notes=order_data.notes,
            status='new',
            selected_service_id=await get_model_id(session, "Service", order_data.selected_services),
        )
        session.add(order)
        await session.commit()

        relationship = OrderFromTenant(
            tenant_id=tenant_profile.id,
            order_id=order.id,
        )
        session.add(relationship)
        await session.commit()

        if order_data.additional_services:
            for additional_service_data in order_data.additional_services:
                if additional_service_data.additional_service_id != 2:
                    additional_service_data.quantity = 0
                additional_service = AdditionalService(
                    order_id=order.id,
                    service_id=await get_model_id(session, "Service", order_data.selected_services),
                    quantity=additional_service_data.quantity,
                    additional_service_id=additional_service_data.additional_service_id,
                )
                session.add(additional_service)

            await session.commit()

        # file_path = "uploads/document/" + file.filename
        if order_data.documents:
            for document_data in order_data.documents:
                document = Document(
                    order_id=order.id,
                    file_name=document_data.file_name,
                    mime_type=document_data.mime_type,
                    file_path='yes'
                )
                session.add(document)

            await session.commit()

        query = (
            update(TenantProfile)
            .where(
                (TenantProfile.id == tenant_profile.id)
            )
            .values({"active_request": TenantProfile.active_request + 1})
            .returning(TenantProfile.active_request)
        )
        await session.execute(query)
        await session.commit()

        apartment_name = await session.scalar(select(ApartmentProfile)
                                              .where(ApartmentProfile.id == order_data.apartment_id))
        service_id = await get_model_id(session, "Service", order_data.selected_services)
        icon = await session.scalar(select(Service).where(Service.id == service_id))
        await pred_send_notification(user, session, "order", title=order_data.selected_services,
                                     body=apartment_name.apartment_name, order_id=order.id,
                                     apartment_id=order_data.apartment_id, image=icon.big_icons_path)
        data = await get_user_profile(session, tenant_profile.id)
        return JSONResponse(content=data, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        return JSONResponse(content=f"Error create order {e}", status_code=status.HTTP_400_BAD_REQUEST)
