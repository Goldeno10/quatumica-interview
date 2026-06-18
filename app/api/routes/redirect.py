from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import RedirectResponse

from app.api.dependencies import get_link_service
from app.core.exceptions import LinkExpiredError, LinkNotFoundError
from app.services.link_service import LinkService

router = APIRouter(tags=["redirect"])

RESERVED_SLUGS = {"health", "docs", "redoc", "openapi.json", "api"}


@router.get("/{slug}")
async def redirect_to_target(
    slug: Annotated[str, Path(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")],
    request: Request,
    service: LinkService = Depends(get_link_service),
) -> RedirectResponse:
    if slug in RESERVED_SLUGS:
        raise HTTPException(status_code=404, detail="Link not found")

    try:
        target_url = await service.resolve_redirect(slug, request.headers.get("user-agent"))
    except LinkNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Link not found") from exc
    except LinkExpiredError as exc:
        raise HTTPException(status_code=404, detail="Link has expired") from exc

    return RedirectResponse(url=target_url, status_code=302)
