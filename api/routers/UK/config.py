from sqlalchemy.future import select
from models.models import UK


async def get_staff_profile(session, uk_id):
    uk = await session.scalar(select(UK).where(UK.id == uk_id))

    data = {
        "UK name": uk.name
    }
    return data
