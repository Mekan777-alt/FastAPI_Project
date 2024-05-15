from typing import Annotated
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse
from api.routers.users.config import get_user_id
from schemas.user.get_order_list import Apartment
from config import get_session
from firebase.config import get_firebase_user_from_token
from sqlalchemy.future import select
from firebase.config import get_staff_firebase
from models.base import (AdditionalService, Service, Document, TenantProfile, ApartmentProfile,
                         AdditionalServiceList, TenantApartments, Order, ExecutorOrders, ExecutorsProfile)

router = APIRouter()


@router.get("/get_orders")
async def get_orders(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                     session: AsyncSession = Depends(get_session)):
    try:
        order_result = await get_user_id(session, user['uid'])

        orders = []
        for order in order_result:
            for row in order:
                order = row[0]
                order_data = {
                    "order_id": order.id,
                    "status": order.status,
                    "name": f"Service on {order.created_at.strftime('%d.%m.%Y')} at {order.created_at.strftime('%H:%M')}",
                    "created_at": order.created_at.strftime('%d %h %Y'),
                    "selected_services": order.selected_service.name if order.selected_service.name else None,
                    "additional_services": [],
                }
                for additional_service in await session.scalars(
                        select(AdditionalService)
                                .where(AdditionalService.order_id == order.id)
                ):
                    service_name = await session.scalar(select(AdditionalServiceList).where
                                                        (AdditionalServiceList.id == additional_service.additional_service_id))
                    if service_name:
                        additional_service_data = {
                            "name": service_name.name if service_name.name else None,
                            "quantity": additional_service.quantity if additional_service.quantity else 0,

                        }
                        order_data["additional_services"].append(additional_service_data)
                orders.append(order_data)

        return {"orders": orders}
    except Exception as e:
        return JSONResponse(content=f"{e}", status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/get_orders/{order_id}')
async def get_order_id(order_id: int, user: Annotated[dict, Depends(get_firebase_user_from_token)],
                       session: AsyncSession = Depends(get_session)):
    try:

        order = await session.scalar(select(Order).where(Order.id == order_id))
        icon_path = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
        service = await session.scalar(select(Service).where(Service.id == order.selected_service_id))
        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == order.apartment_id))

        service_data = []
        additional_services = await session.scalars(select(AdditionalService)
                                                    .where(AdditionalService.order_id == order.id))

        for additional_service in additional_services:
            service_name = await session.scalar(select(AdditionalServiceList)
                                                .where(
                AdditionalServiceList.id == additional_service.additional_service_id))
            service_data.append(service_name.name)

        executor_info = await session.scalar(select(ExecutorOrders).where(ExecutorOrders.order_id == order_id))

        executor_data = []

        if executor_info:

            executor = await session.scalar(select(ExecutorsProfile)
                                            .where(ExecutorsProfile.id == executor_info.executor_id))
            from_firebase = await get_staff_firebase(executor.uuid)

            from_firebase['id'] = executor.id
            executor_data.append(from_firebase)

        data = {
            "id": order.id,
            "icon_path": icon_path.big_icons_path if icon_path.big_icons_path else None,
            "service_name": service.name,
            "created_at": f"{order.created_at.strftime('%d %h %H:%M')}",
            "completion_date": order.completion_date,
            "apartment_name": apartment_info.apartment_name,
            "completed_at": order.completion_time,
            "status": order.status,
            "additional_info": {
                "additional_service_list": service_data
            },
            "executor": executor_data[0] if len(executor_data) > 0 else None
        }

        return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/get_order_list", response_model=Apartment)
async def get_order_list(user: Annotated[dict, Depends(get_firebase_user_from_token)],
                         session: AsyncSession = Depends(get_session)):
    try:

        tenant_id = user['uid']

        query = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == tenant_id))

        apartment_id = await session.scalars(select(TenantApartments)
                                             .where(TenantApartments.tenant_id == query.id))

        apartment_name = []

        for i in apartment_id:

            query = await session.scalars(select(ApartmentProfile).where(ApartmentProfile.id == i.apartment_id))

            for j in query:
                data = {
                    "id": j.id,
                    "apartment_name": j.apartment_name
                }
                apartment_name.append(data)

        service_query = await session.execute(select(Service))

        services = service_query.scalars()

        service_list = []

        for service in services:
            data = {
                "id": service.id,
                'name': service.name
            }
            service_list.append(data)

        additional_query = await session.execute(
            select(AdditionalServiceList).join(Service, AdditionalServiceList.service_id == Service.id))

        additional_service_list = additional_query.scalars().all()

        additional_services_dict = {}
        for additional_service in additional_service_list:
            if additional_service.service.name not in additional_services_dict:
                additional_services_dict[additional_service.service.name] = []
            additional_services_dict[additional_service.service.name].append({
                "id": additional_service.id,
                "name": additional_service.name,
                "price": additional_service.price
            })

        data = {
            "apartment_name": apartment_name,
            "types_of_services": service_list,
            "additional_services": additional_services_dict
        }

        return JSONResponse(content=data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content=f"{e}", status_code=status.HTTP_400_BAD_REQUEST)
