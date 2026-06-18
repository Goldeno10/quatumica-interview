from datetime import UTC, datetime

from app.core.exceptions import LinkExpiredError, LinkNotFoundError, SlugAlreadyExistsError
from app.models.link import Link
from app.repositories.link_repository import LinkRepository
from app.schemas.link import LinkCreate, LinkCreateResponse, LinkResponse


class LinkService:
    def __init__(self, repository: LinkRepository) -> None:
        self.repository = repository

    async def create_link(self, payload: LinkCreate, base_url: str) -> LinkCreateResponse:
        slug = payload.slug or await self.repository.generate_unique_slug()
        if payload.slug:
            existing = await self.repository.get_by_slug(slug)
            if existing is not None:
                raise SlugAlreadyExistsError(slug)

        link = await self.repository.create(
            slug=slug,
            target_url=str(payload.target_url),
            expires_at=payload.expires_at,
        )
        return LinkCreateResponse(
            slug=link.slug,
            target_url=link.target_url,
            short_url=f"{base_url.rstrip('/')}/{link.slug}",
            expires_at=link.expires_at,
            created_at=link.created_at,
        )

    async def list_links(self) -> list[LinkResponse]:
        links = await self.repository.list_all()
        return [LinkResponse.model_validate(link) for link in links]

    async def delete_link(self, slug: str) -> None:
        deleted = await self.repository.delete(slug)
        if not deleted:
            raise LinkNotFoundError(slug)

    async def resolve_redirect(self, slug: str, user_agent: str | None) -> str:
        link = await self.repository.get_by_slug(slug)
        if link is None:
            raise LinkNotFoundError(slug)
        if self._is_expired(link):
            raise LinkExpiredError(slug)
        await self.repository.record_click(link, user_agent)
        return link.target_url

    @staticmethod
    def _is_expired(link: Link) -> bool:
        if link.expires_at is None:
            return False
        now = datetime.now(UTC)
        expires_at = link.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return expires_at <= now
