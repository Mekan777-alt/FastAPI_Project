from firebase_admin import messaging


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
