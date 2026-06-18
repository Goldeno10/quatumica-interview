import secrets
import string

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import SlugAlreadyExistsError
from app.models.link import Click, Link


class LinkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        slug: str,
        target_url: str,
        expires_at,
    ) -> Link:
        link = Link(slug=slug, target_url=target_url, expires_at=expires_at, click_count=0)
        self.session.add(link)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise SlugAlreadyExistsError(slug) from exc
        await self.session.refresh(link)
        return link

    async def get_by_slug(self, slug: str) -> Link | None:
        result = await self.session.execute(select(Link).where(Link.slug == slug))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Link]:
        result = await self.session.execute(select(Link).order_by(Link.created_at.desc()))
        return list(result.scalars().all())

    async def delete(self, slug: str) -> bool:
        link = await self.get_by_slug(slug)
        if link is None:
            return False
        await self.session.delete(link)
        await self.session.commit()
        return True

    async def record_click(self, link: Link, user_agent: str | None) -> None:
        link.click_count += 1
        self.session.add(Click(link_id=link.id, user_agent=user_agent))
        await self.session.commit()

    async def generate_unique_slug(self) -> str:
        alphabet = string.ascii_letters + string.digits
        for _ in range(10):
            slug = "".join(secrets.choice(alphabet) for _ in range(settings.auto_slug_length))
            existing = await self.get_by_slug(slug)
            if existing is None:
                return slug
        raise RuntimeError("Unable to generate a unique slug")
