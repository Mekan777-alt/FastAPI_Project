from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.base import (TenantProfile, Order, Service, TenantApartments, ApartmentProfile, Object, UK, Contacts, Meters,
                         MeterService, GuestPass, GuestPassDocuments, InvoiceHistory)
from firebase.config import get_staff_firebase
from fastapi import HTTPException
from starlette import status


async def get_user_id(session, user_uuid):

    query = await session.scalars(select(TenantProfile).where(TenantProfile.uuid == user_uuid))

    orders_data = []

    for i in query:
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
        apartments = await session.scalars(select(TenantApartments).where(TenantApartments.tenant_id == tenant_profile.id))

        if client['role'] != 'client':

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to client")

        client['apartment_info'] = []
        for apartment in apartments:
            apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment.apartment_id))
            data = {
                'id': apartment_info.id,
                'name': apartment_info.apartment_name,
            }
            client['apartment_info'].append(data)
        client['photo_path'] = tenant_profile.photo_path
        client['balance'] = tenant_profile.balance
        return client

    except HTTPException as e:
        raise e


async def get_user_meters(session, user_id):
    try:

        user_info = await session.scalar(select(TenantApartments).where(TenantProfile.uuid == user_id))

        if not user_info:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

        apartment = await session.scalar(select(TenantApartments).where(TenantApartments.tenant_id == user_info.id))

        if not apartment:

            raise HTTPException(detail="Apartment not found", status_code=status.HTTP_404_NOT_FOUND)


        meters = await session.scalars(select(Meters).where(Meters.apartment_id == apartment.apartment_id))

        if not meters:

            return "No Meters"

        data = []
        for meter in meters:
            meter_service_info = await session.scalar(select(MeterService).where(
                MeterService.id == meter.meter_service_id))

            service_info = {
                "id": meter.id,
                "icon_path": meter_service_info.big_icons_path,
                "name": meter_service_info.name,
            }
            data.append(service_info)
        return data

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def get_guest_pass(session, user_id):
    try:

        tenant = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user_id))

        if not tenant:

            raise HTTPException(detail="Tenant not found", status_code=status.HTTP_404_NOT_FOUND)

        apartment_id = await session.scalars(select(TenantApartments).where(TenantApartments.tenant_id == tenant.id))

        if not apartment_id:

            raise HTTPException(detail="Apartment not found", status_code=status.HTTP_404_NOT_FOUND)

        data = []

        for apartment in apartment_id:

            apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == apartment.id))

            apartment_data = {
                "id": apartment_info.id,
                "name": apartment_info.apartment_name,
            }
            data.append(apartment_data)

        return data

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def post_guest_pass(session, user_id, request_form):
    try:

        data = []
        guest_pass = GuestPass(
            visit_date=request_form.visit_date,
            visit_time=request_form.visit_time,
            full_name=request_form.full_name,
            note=request_form.note if request_form.note else None,
            apartment_id=request_form.apartment_id
        )
        session.add(guest_pass)
        await session.commit()
        data.append(guest_pass.to_dict())

        if request_form.documents:
            for doc in request_form.documents:
                document = GuestPassDocuments(
                    file_name=doc.file_name,
                    mime_type=doc.mime_type,
                    file_path='yes',
                    guest_pass_id=guest_pass.id
                )
                session.add(document)
                await session.commit()
                data.append(document.to_dict())

        return data

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def get_finance_from_user(session, user):
    try:

        user_profile = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user['uid']))
        tenant_info = await session.scalar(select(TenantApartments).where(TenantApartments.tenant_id == user_profile.id))
        apartment_info = await session.scalar(select(ApartmentProfile).where(ApartmentProfile.id == tenant_info.apartment_id))
        object_info = await session.scalar(select(Object).where(Object.id == apartment_info.object_id))
        from_firebase = await get_staff_firebase(user['uid'])

        if not user:

            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

        del from_firebase['phone_number']
        del from_firebase['email']
        del from_firebase['role']

        from_firebase['balance'] = user_profile.balance
        from_firebase['object_name'] = object_info.object_name
        from_firebase['invoice_history'] = []

        invoice_info = await session.scalars(select(InvoiceHistory).where(InvoiceHistory.apartment_id == apartment_info.id))

        for invoice in invoice_info:

            invoice_history_data = {
                "id": invoice.id,
                "name": "Invoice",
                "amount": invoice.amount,
                "icon_path": invoice.photo_path,
            }
            from_firebase['invoice_history'].append(invoice_history_data)
        return from_firebase
    except Exception as e:

        return e

