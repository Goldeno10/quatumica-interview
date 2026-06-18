from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.dependencies import get_link_service
from app.core.exceptions import LinkNotFoundError, SlugAlreadyExistsError
from app.core.rate_limit import get_client_ip, rate_limiter
from app.schemas.link import LinkCreate, LinkCreateResponse, LinkResponse
from app.services.link_service import LinkService

router = APIRouter(prefix="/api/links", tags=["links"])


@router.post("", response_model=LinkCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: LinkCreate,
    request: Request,
    service: LinkService = Depends(get_link_service),
) -> LinkCreateResponse:
    rate_limiter.check(get_client_ip(request))
    try:
        base_url = str(request.base_url).rstrip("/")
        return await service.create_link(payload, base_url=base_url)
    except SlugAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slug '{exc.args[0]}' is already in use",
        ) from exc


@router.get("", response_model=list[LinkResponse])
async def list_links(service: LinkService = Depends(get_link_service)) -> list[LinkResponse]:
    return await service.list_links()


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(slug: str, service: LinkService = Depends(get_link_service)) -> None:
    try:
        await service.delete_link(slug)
    except LinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found") from exc
