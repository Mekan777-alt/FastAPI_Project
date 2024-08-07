from firebase_admin import messaging
from firebase.config import get_staff_firebase
from sqlalchemy import select
from models.base import (TenantProfile, TenantApartments, UK, EmployeeUK, ApartmentProfile, Object,
                         NotificationUK, NotificationEmployee, NotificationTenants, TenantProfile, Order,
                         OrderFromTenant, ExecutorsProfile)


async def send_notification(tokens, title, body, image=None, content_id=None, apartment_id=None,
                            screen=None, user_id=None):
    try:
        data = {}
        if screen == 'order':
            data = {"order_id": content_id, "apartment_id": apartment_id, "screen": screen,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK", "imageUrl": image, "user_id": user_id}
        elif screen == 'news':
            data = {"id": content_id, "screen": screen,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK", "imageUrl": image}
        elif screen == 'invoice':
            data = {"id": content_id, "screen": screen, "image": image, "click_action": "FLUTTER_NOTIFICATION_CLICK"}
        # message = messaging.MulticastMessage(
        #     tokens=tokens,
        #     data={key: str(value) for key, value in data.items()},
        #     notification=messaging.Notification(
        #         title=title,
        #         body=body,
        #     )
        # )
        #
        # send = messaging.send_multicast(message)
        # print(f"Send notification - {send.success_count}")
        # print(f"Not send notify count - {send.failure_count}")
        # print(f"Responses {send.responses}")
        for token in tokens:
            message = messaging.Message(
                token=token,
                data={key: str(value) for key, value in data.items()},
                notification=messaging.Notification(
                    title=title,
                    body=body,
                )
            )
            response = messaging.send(message)
            print('Successfully sent message:', response)
        return True

    except Exception as e:
        print(e)
        return e


async def pred_send_notification(user, session, value=None, title=None, body=None, image=None,
                                 order_id=None, apartment_id=None, executor_id=None):
    try:

        user_uid = user['uid']

        user_fb = await get_staff_firebase(user_uid)

        if user_fb['role'] == 'client':
            if value == 'order':
                tokens_client = []
                user_info = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user_uid))

                user_apart = await session.scalar(select(TenantApartments)
                                                  .where(TenantApartments.tenant_id == user_info.id))

                apartment = await session.scalar(select(ApartmentProfile)
                                                 .where(ApartmentProfile.id == user_apart.apartment_id))

                object_apart = await session.scalar(select(Object).where(Object.id == apartment.object_id))

                uk = await session.scalar(select(UK).where(UK.id == object_apart.uk_id))
                if uk.device_token:
                    new_not_uk = NotificationUK(
                        title=title,
                        description=f"A new order for {body}",
                        type=value,
                        uk_id=uk.id,
                        content_id=order_id,
                        apartment_id=apartment_id,
                        image=image,
                    )
                    session.add(new_not_uk)
                    await session.commit()
                    tokens_client.append(uk.device_token)

                employee_info = await session.scalars(select(EmployeeUK).where(EmployeeUK.object_id == object_apart.id))

                for employee in employee_info:
                    if employee.device_token:
                        new_not_employee = NotificationEmployee(
                            title=title,
                            description=f"A new order for {body}",
                            type=value,
                            employee_id=employee.id,
                            object_id=employee.object_id,
                            content_id=order_id,
                            apartment_id=apartment_id,
                            image=image,
                        )
                        session.add(new_not_employee)
                        await session.commit()
                        tokens_client.append(employee.device_token)
                await send_notification(tokens_client, title, body=f"A new order for {body}",
                                        content_id=order_id,
                                        apartment_id=apartment_id, screen=value, image=image,
                                        user_id=user_uid)

                return
        elif user_fb['role'] == 'Company':
            if value == "news":
                tokens_company = []
                uk_info = await session.scalar(select(UK).where(UK.uuid == user_uid))

                objects_uk = await session.scalars(select(Object).where(Object.uk_id == uk_info.id))

                for object_uk in objects_uk:

                    employees = await session.scalars(select(EmployeeUK).where(EmployeeUK.object_id == object_uk.id))

                    for employee in employees:
                        if employee.device_token:
                            new_not_employee = NotificationEmployee(
                                title=title,
                                description=f"A new news created {body}",
                                employee_id=employee.id,
                                type=value,
                                object_id=employee.object_id,
                                content_id=order_id,
                                image=image,
                            )
                            session.add(new_not_employee)
                            await session.commit()
                            tokens_company.append(employee.device_token)

                if apartment_id:
                    tenants = await session.scalars(
                        select(TenantApartments).where(TenantApartments.apartment_id == apartment_id))

                    for tenant in tenants:
                        tenant_token = await session.scalar(select(TenantProfile).where(TenantProfile.id == tenant.tenant_id))

                        if tenant_token.device_token:
                            new_not_tenant = NotificationTenants(
                                title=title,
                                description=f"A new news created {body}",
                                type=value,
                                tenant_id=tenant_token.id,
                                content_id=order_id,
                                image=image,
                                apartment_id=apartment_id
                            )
                            session.add(new_not_tenant)
                            await session.commit()
                            tokens_company.append(tenant_token.device_token)
                elif len(apartment_id) > 1:
                    for apart_id in apartment_id:
                        tenants = await session.scalars(select(TenantApartments)
                                                        .where(TenantApartments.apartment_id == apart_id))

                        for tenant in tenants:
                            tenant_token = await session.scalar(
                                select(TenantProfile).where(TenantProfile.id == tenant.tenant_id))
                            if tenant_token.device_token:
                                new_not_tenant = NotificationTenants(
                                    title=title,
                                    description=f"A new news created {body}",
                                    tenant_id=tenant_token.id,
                                    type=value,
                                    content_id=order_id,
                                    image=image,
                                    apartment_id=apart_id
                                )
                                session.add(new_not_tenant)
                                await session.commit()
                                tokens_company.append(tenant_token.device_token)

                await send_notification(tokens_company, title, body=f"A new news created {body}",
                                        image=image, content_id=order_id, screen=value)

                return

            elif value == '':

                pass

        elif user_fb['role'] == 'Employee':
            if value == 'invoice':
                tokens = []
                apartment_info = await session.scalar(
                    session(ApartmentProfile).where(ApartmentProfile.id == apartment_id))

                tenant_apartment = await session.scalars(select(TenantApartments)
                                                         .where(TenantApartments.apartment_id == apartment_id))
                for tenant in tenant_apartment:
                    tenant_info = await session.scalar(select(TenantProfile)
                                                       .where(TenantProfile.id == tenant.tenant_id))
                    if tenant_info.device_token:
                        new_not_tenant = NotificationTenants(
                            title=title,
                            description=f"A new invoice for {apartment_info.apartment_name}",
                            tenant_id=tenant.id,
                            content_id=order_id,
                            image=image,
                            apartment_id=apartment_id
                        )
                        session.add(new_not_tenant)
                        await session.commit()
                        tokens.append(tenant_info.device_token)
                await send_notification(tokens=tokens, title=f"New invoice",
                                        body=f"A new invoice for {apartment_info.apartment_name}",
                                        image=image,
                                        content_id=order_id, screen=value)

            elif value == 'replacing_executor' or value == 'send in progress order':
                tokens = []
                executor_info = await session.scalar(select(ExecutorsProfile).where(ExecutorsProfile.id == executor_id))

                tenant_order = await session.scalar(select(OrderFromTenant).where(OrderFromTenant.order_id == order_id))
                tenant_info = await session.scalar(select(TenantProfile)
                                                   .where(TenantProfile.id == tenant_order.tenant_id))

                if tenant_info.device_token:
                    tokens.append(tenant_info.device_token)

                if value == 'replacing_executor':
                    new_not_tenant = NotificationTenants(
                        title="Order",
                        description=f"Replacing executor, new executor - {executor_info.first_name} "
                                    f"{executor_info.last_name}",
                        tenant_id=tenant_info.id,
                        type='order',
                        content_id=order_id,
                        image=image,
                        apartment_id=apartment_id
                    )
                    session.add(new_not_tenant)
                    await session.commit()
                    await send_notification(tokens=tokens, title=f"Order",
                                            body=f'Replacing executor, new executor - '
                                                 f'{executor_info.first_name} {executor_info.last_name}',
                                            screen='order',
                                            content_id=order_id, )
                elif value == 'send in progress order':
                    new_not_tenant = NotificationTenants(
                        title="Order",
                        description=f"I've got the order to work - {executor_info.first_name} {executor_info.last_name}"
                                    f"{executor_info.last_name}",
                        tenant_id=tenant_info.id,
                        type='order',
                        content_id=order_id,
                        image=image,
                        apartment_id=apartment_id
                    )
                    session.add(new_not_tenant)
                    await session.commit()
                    await send_notification(tokens=tokens, title=f"Order",
                                            body=f"I've got the order to work - "
                                                 f"{executor_info.first_name} {executor_info.last_name}",
                                            screen='order',
                                            content_id=order_id, apartment_id=apartment_id)

            elif value == '':
                pass

    except Exception as e:

        return e
