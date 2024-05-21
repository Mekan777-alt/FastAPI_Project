from firebase_admin import messaging
from firebase.config import get_staff_firebase
from sqlalchemy import select
from models.base import (TenantProfile, TenantApartments, UK, EmployeeUK, ApartmentProfile, Object,
                         NotificationUK, NotificationEmployee, NotificationTenants)


async def send_notification(tokens, title, body, role, image=None, content_id=None, apartment_id=None, screen=None):
    try:
        data = {}
        if screen == 'order':
            data = {"order_id": content_id, "apartment_id": apartment_id, "screen": screen, "role": role}
        elif screen == 'news':
            data = {"id": content_id,  "screen": screen, "role": role}
        message = messaging.MulticastMessage(
            tokens=tokens,
            data={key: str(value) for key, value in data.items()},
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image,
            )
        )
        send = messaging.send_multicast(message)
        print(f"Send notification - {send.success_count}")
        return True

    except Exception as e:
        print(e)
        return e


async def pred_send_notification(user, session, value=None, title=None, body=None, image=None,
                                 order_id=None, apartment_id=None):
    try:

        user_uid = user['uid']

        user_fb = await get_staff_firebase(user_uid)

        if user_fb['role'] == 'client':

            tokens = []
            user_info = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user_uid))

            user_apart = await session.scalar(select(TenantApartments)
                                              .where(TenantApartments.tenant_id == user_info.id))

            apartment = await session.scalar(select(ApartmentProfile)
                                             .where(ApartmentProfile.id == user_apart.apartment_id))

            object_apart = await session.scalar(select(Object).where(Object.id == apartment.object_id))

            uk = await session.scalar(select(UK).where(UK.id == object_apart.uk_id))
            if uk.device_token:
                tokens.append(uk.device_token)

            employee_info = await session.scalars(select(EmployeeUK).where(EmployeeUK.object_id == object_apart.id))

            objects_id = []

            for employee in employee_info:
                if employee.object_id not in objects_id:
                    objects_id.append(employee.object_id)
                if employee.device_token:
                    tokens.append(employee.device_token)

            if value == 'order':
                notification = await send_notification(tokens, title, body=f"A new order for {body}",
                                                       role=user_fb['role'], content_id=order_id,
                                                       apartment_id=apartment_id, screen=value, image=image)

                if notification:

                    new_not_uk = NotificationUK(
                        title=title,
                        description=f"A new order for {body}",
                        type=value,
                        uk_id=uk.id,
                    )
                    session.add(new_not_uk)
                    await session.commit()
                    for object_id in objects_id:
                        new_not_employee = NotificationEmployee(
                            title=title,
                            description=f"A new order for {body}",
                            type=value,
                            object_id=object_id,
                        )
                        session.add(new_not_employee)
                        await session.commit()

                    return
            elif value == 'guest_pass':
                notification = await send_notification(tokens, title, f"A new guest request for {body}")

                if notification:
                    new_not_uk = NotificationUK(
                        title=title,
                        description=f"A new guest request for {body}",
                        type=value,
                        uk_id=uk.id,
                    )
                    session.add(new_not_uk)
                    new_not_employee = NotificationEmployee(
                        title=title,
                        description=f"A new guest request for {body}",
                        type=value,
                        object_id=object_apart.id,
                    )
                    session.add(new_not_employee)
                    await session.commit()

                    return

        elif user_fb['role'] == 'Company':
            tokens = []
            uk_info = await session.scalar(select(UK).where(UK.uuid == user_uid))
            tokens.append(uk_info.device_token)

            objects_uk = await session.scalars(select(Object).where(Object.uk_id == uk_info.id))

            for object_uk in objects_uk:

                employees = await session.scalars(select(EmployeeUK).where(EmployeeUK.object_id == object_uk.id))

                for employee in employees:
                    if employee.device_token:
                        tokens.append(employee.device_token)

            if len(apartment_id) == 1:
                tenant = await session.scalar(select(TenantApartments).where(TenantApartments.apartment_id == apartment_id))

                tenant_token = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant.id))

                if tenant_token.device_token:
                    tokens.append(tenant_token.device_token)
            elif len(apartment_id) > 1:
                for apart_id in apartment_id:
                    tenants = await session.scalars(select(TenantApartments)
                                                    .where(TenantApartments.apartment_id == apart_id))

                    for tenant in tenants:
                        tenant_token = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant.id))
                        if tenant_token.device_token:
                            tokens.append(tenant_token.device_token)
            if value == "news":

                notification = await send_notification(tokens, title,
                                                       body=f"A new news created {body}", role=user_fb['role'],
                                                       image=image, content_id=order_id, screen=value)

                if notification:
                    new_not_uk = NotificationUK(
                        title=title,
                        description=f"A new guest request for {body}",
                        uk_id=uk_info.id,
                    )
                    session.add(new_not_uk)
                    new_not_employee = NotificationEmployee(
                        title=title,
                        description=f"A new guest request for {body}",
                        object_id=objects_uk.id,
                    )
                    session.add(new_not_employee)
                    await session.commit()

                    return

            elif value == '':

                pass

        elif user_fb['role'] == 'Employee':

            pass


    except Exception as e:

        return e