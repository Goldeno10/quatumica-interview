from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from app.models.link import Link


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"


@pytest.mark.asyncio
async def test_create_link_with_custom_slug(client: AsyncClient):
    response = await client.post(
        "/api/links",
        json={"target_url": "https://example.com", "slug": "my-link"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "my-link"
    assert data["target_url"] == "https://example.com/"
    assert data["short_url"] == "http://test/my-link"


@pytest.mark.asyncio
async def test_create_link_auto_slug(client: AsyncClient):
    response = await client.post(
        "/api/links",
        json={"target_url": "https://example.org"},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["slug"]) == 8
    assert data["target_url"] == "https://example.org/"


@pytest.mark.asyncio
async def test_create_link_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/links",
        json={"target_url": "not-a-url", "slug": "bad slug!"},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Validation failed"
    assert len(body["errors"]) >= 1


@pytest.mark.asyncio
async def test_create_duplicate_slug(client: AsyncClient):
    payload = {"target_url": "https://example.com", "slug": "dup"}
    assert (await client.post("/api/links", json=payload)).status_code == 201
    response = await client.post("/api/links", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_links(client: AsyncClient):
    await client.post("/api/links", json={"target_url": "https://a.com", "slug": "link-a"})
    await client.post("/api/links", json={"target_url": "https://b.com", "slug": "link-b"})

    response = await client.get("/api/links")
    assert response.status_code == 200
    links = response.json()
    assert len(links) == 2
    assert all("click_count" in link and "created_at" in link for link in links)


@pytest.mark.asyncio
async def test_redirect_and_click_count(client: AsyncClient):
    await client.post(
        "/api/links",
        json={"target_url": "https://redirect-target.com", "slug": "go-now"},
    )

    response = await client.get("/go-now", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://redirect-target.com/"

    links = (await client.get("/api/links")).json()
    assert links[0]["click_count"] == 1


@pytest.mark.asyncio
async def test_redirect_records_user_agent(client: AsyncClient, session):
    await client.post(
        "/api/links",
        json={"target_url": "https://example.com", "slug": "ua-test"},
    )
    await client.get("/ua-test", headers={"User-Agent": "pytest-agent"})

    from sqlalchemy import select

    from app.models.link import Click

    result = await session.execute(select(Click))
    click = result.scalar_one()
    assert click.user_agent == "pytest-agent"


@pytest.mark.asyncio
async def test_redirect_not_found(client: AsyncClient):
    response = await client.get("/missing")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_redirect_expired(client: AsyncClient, session, past_expiry: datetime):
    session.add(
        Link(
            slug="old",
            target_url="https://expired.com",
            expires_at=past_expiry,
            click_count=0,
        )
    )
    await session.commit()

    response = await client.get("/old")
    assert response.status_code == 404
    assert response.json()["detail"] == "Link has expired"


@pytest.mark.asyncio
async def test_delete_link(client: AsyncClient):
    await client.post("/api/links", json={"target_url": "https://x.com", "slug": "del-me"})
    response = await client.delete("/api/links/del-me")
    assert response.status_code == 204

    assert (await client.get("/del-me")).status_code == 404
    assert (await client.delete("/api/links/del-me")).status_code == 404


@pytest.mark.asyncio
async def test_expires_at_must_be_future(client: AsyncClient):
    past = (datetime.now(UTC) - timedelta(minutes=5)).isoformat()
    response = await client.post(
        "/api/links",
        json={"target_url": "https://example.com", "slug": "future", "expires_at": past},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_rate_limit(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    from app.core import rate_limit as rate_limit_module

    monkeypatch.setattr(
        rate_limit_module.rate_limiter,
        "max_requests",
        2,
    )
    monkeypatch.setattr(
        rate_limit_module.rate_limiter,
        "window_seconds",
        60,
    )
    rate_limit_module.rate_limiter._requests.clear()

    payload = {"target_url": "https://rate.com"}
    assert (await client.post("/api/links", json=payload)).status_code == 201
    assert (await client.post("/api/links", json={**payload, "slug": "rate-two"})).status_code == 201
    response = await client.post("/api/links", json={**payload, "slug": "rate-three"})
    assert response.status_code == 429
