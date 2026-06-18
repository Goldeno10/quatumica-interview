from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.link_repository import LinkRepository
from app.services.link_service import LinkService


async def get_link_repository(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[LinkRepository, None]:
    yield LinkRepository(session)


async def get_link_service(
    repository: LinkRepository = Depends(get_link_repository),
) -> AsyncGenerator[LinkService, None]:
    yield LinkService(repository)
