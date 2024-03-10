from typing import Annotated
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse
from api.routers.users.config import get_user_id
from schemas.user.get_orders import OrderListResponse
from schemas.user.get_order_list import Apartment
from schemas.user.new_order import AdditionalServiceSchema, DocumentSchema
from config import get_session
from firebase.config import get_firebase_user_from_token
from sqlalchemy.future import select
from models.base import (AdditionalService, Service, Document, TenantProfile, ApartmentProfile,
                         AdditionalServiceList, TenantApartments)

router = APIRouter(
    prefix="/api/v1",
)


@router.get("/get_orders", response_model=OrderListResponse)
async def get_orders(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     session: AsyncSession = Depends(get_session)):

    try:
        order_result = await get_user_id(session, user['uid'])

        orders = []
        for order in order_result:
            for row in order:
                order = row[0]
                order_data = {
                    "order_id": str(order.id),
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

        return {"orders": orders}
    except Exception as e:
        return JSONResponse(content=f"{e}", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/get_order_list", response_model=Apartment)
async def get_order_list(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                         session: AsyncSession = Depends(get_session)):

    try:

        tenant_id = user['uid']

        query = await session.execute(select(TenantProfile)
                                      .where(TenantProfile.uuid == tenant_id))

        tenant_profile = query.scalar()

        apartment_id = await session.execute(select(TenantApartments)
                                             .where(TenantApartments.tenant_id == tenant_profile.id))

        apartments_model = apartment_id.scalars()

        apartment_name = []

        for i in apartments_model:

            query = await session.execute(select(ApartmentProfile).where(ApartmentProfile.id == i.apartment_id))

            apartment_profile = query.scalars()

            for j in apartment_profile:

                apartment_name.append(j.apartment_name)

        service_query = await session.execute(select(Service))

        services = service_query.scalars()

        service_list = []

        for service in services:

            service_list.append(service.name)

        additional_query = await session.execute(
            select(AdditionalServiceList).join(Service, AdditionalServiceList.service_id == Service.id))

        additional_service_list = additional_query.scalars().all()

        additional_services_dict = {}
        for additional_service in additional_service_list:
            if additional_service.service.name not in additional_services_dict:
                additional_services_dict[additional_service.service.name] = []
            additional_services_dict[additional_service.service.name].append({
                "name": additional_service.name,
                "price": additional_service.price
            })

        data = {
            "apartment_name": apartment_name,
            "types of services": service_list,
            "additional_services": additional_services_dict
        }

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content=f"{e}", status_code=status.HTTP_400_BAD_REQUEST)




