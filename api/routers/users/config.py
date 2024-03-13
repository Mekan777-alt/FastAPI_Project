from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.base import TenantProfile, Order, Service, TenantApartments, ApartmentProfile, Object, UK, Contacts


async def get_user_id(session, user_uuid):

    query = select(TenantProfile).where(TenantProfile.uuid == user_uuid)

    result = await session.execute(query)

    models = result.scalars()

    orders_data = []

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

        orders_data.append(order_result)

    return orders_data


async def get_user_profile(session, user_id, new_value=None):
    apartment_id = await session.execute(select(TenantApartments, ApartmentProfile, Object).
                                         join(ApartmentProfile).join(Object).select_from(TenantApartments)
                                         .where(TenantProfile.id == user_id))
    tenant_profiles = await session.scalar(select(TenantProfile).where
                                           (TenantProfile.id == user_id))

    result = apartment_id.fetchall()
    data_to_return = []
    for tenant_profile, apartment_profile, object_profile in result:
        data = {
            "object_address": object_profile.address,
            "apartment_name": [],
            "active_request": tenant_profiles.active_request,
            "balance": tenant_profiles.balance
        }
        data["apartment_name"].append(apartment_profile.apartment_name)
        data_to_return.append(data)
    return data_to_return


async def get_contacts_from_db(session):

    try:
        contacts = await session.scalars(select(Contacts))

        contacts_data = []
        for contact in contacts:
            contact_data = {
                "name": contact.name,
                "description": contact.description,
                "email": contact.email if contact.email is not None else "null",
                "phone": contact.phone if contact.phone is not None else "null"
            }
            contacts_data.append(contact_data)

        return contacts_data

    except Exception as e:

        return None
