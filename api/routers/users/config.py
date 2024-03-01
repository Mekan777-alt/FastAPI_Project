from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.models import TenantProfile, Order, Service


async def get_user_id(session, user_uuid):

    query = select(TenantProfile).where(TenantProfile.uuid == user_uuid)

    result = await session.execute(query)

    models = result.scalars()

    if models:
        for i in models:
            query = await session.execute(
                select(Order, Service)
                .where(Order.tenant_id == i.id)
                .join(Service, Order.selected_service_id == Service.id)
                .options(
                    selectinload(Order.selected_service)
                )
                .distinct()
            )

            order_result = query.fetchall()

            if len(order_result) > 0:
                return order_result
            else:
                pass
