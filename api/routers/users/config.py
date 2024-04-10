from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.base import TenantProfile, Order, Service, TenantApartments, ApartmentProfile, Object, UK, Contacts
from firebase.config import get_staff_firebase
from fastapi import HTTPException
from starlette import status


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
    data_to_return = {
        "object_address": "",
        "apartment_name": [],
        "active_request": 0,
        "balance": 0
    }
    for tenant_profile, apartment_profile, object_profile in result:
        data = {
            "object_address": object_profile.address,
            "apartment_name": [],
            "active_request": tenant_profiles.active_request,
            "balance": tenant_profiles.balance
        }
        apartment_data = {
            'id': apartment_profile.id,
            'name': apartment_profile.apartment_name
        }
        data_to_return["apartment_name"].append(apartment_data)
        data_to_return["object_address"] = object_profile.address
        data_to_return["active_request"] = tenant_profiles.active_request
        data_to_return["balance"] = tenant_profiles.balance
    return [data_to_return]


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


async def get_profile_tenant(user, session):

    try:

        client = await get_staff_firebase(user['uid'])
        tenant_profile = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user['uid']))
        apartment = await session.scalar(select(TenantApartments).where(TenantApartments.tenant_id == tenant_profile.id))

        if client['role'] != 'client':

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to client")

        client['photo_path'] = tenant_profile.photo_path
        client['apartment_id'] = apartment.apartment_id

        return client

    except HTTPException as e:
        raise e
