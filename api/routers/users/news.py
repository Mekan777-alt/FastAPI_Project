from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import JSONResponse
from config import get_session
from schemas.news import News as NewsSchemas
from models.models import News

router = APIRouter(
    prefix='/api/v1',
    tags=['News']
)


@router.get('/news', response_model=NewsSchemas)
async def get_news(session: AsyncSession = Depends(get_session)):
    try:

        query = await session.execute(select(News))

        news = query.scalars()

        news_list = []

        for n in news:
            schemas = NewsSchemas(
                id=n.id,
                name=n.name,
                description=n.description,
                created_at=str(n.created_at)
            )

            news_list.append(schemas.dict())

        return JSONResponse(content=news_list, status_code=status.HTTP_200_OK)

    except Exception as e:

        raise HTTPException(detail={'detail': str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
