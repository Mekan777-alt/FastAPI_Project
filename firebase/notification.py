from firebase_admin import messaging
from firebase.config import get_staff_firebase
from sqlalchemy import select
from models.base import TenantProfile, TenantApartments, UK, EmployeeUK, ApartmentProfile, Object


async def send_notification(tokens, title, body, image=None):
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image
            ),
            tokens=tokens
        )
        messaging.send(message)
        return True

    except Exception as e:

        return e


async def pred_send_notification(user, session, value=None):
    try:

        user_uid = user['uid']

        user_fb = await get_staff_firebase(user_uid)

        if user_fb['role'] == 'client':

            if value == 'order':

                tokens = []
                user_info = await session.scalar(select(TenantProfile).where(TenantProfile.uuid == user_uid))

                user_apart = await session.scalar(select(TenantApartments)
                                                  .where(TenantApartments.tenant_id == user_info.id))

                apartment = await session.scalar(select(ApartmentProfile)
                                                 .where(ApartmentProfile.id == user_apart.apartment_id))

                object_apart = await session.scalar(select(Object).where(Object.id == apartment.object_id))

                uk = await session.scalar(select(UK).where(UK.id == object_apart.uk_id))
                tokens.append(uk.device_token)

                employee_info = await session.scalars(select(EmployeeUK).where(EmployeeUK.object_id == object_apart.id))

                for employee in employee_info:

                    tokens.append(employee.device_token)

                await send_notification(tokens, "Новый ордер", "Новый ордер")

            elif value == 'guest_pass':

                pass

        elif user_fb['role'] == 'Company':

            pass

        elif user_fb['role'] == 'Employee':

            pass


    except Exception as e:

        return e