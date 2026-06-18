from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class LinkCreate(BaseModel):
    target_url: HttpUrl
    slug: Annotated[
        str | None,
        Field(
            default=None,
            min_length=3,
            max_length=64,
            pattern=r"^[a-zA-Z0-9_-]+$",
            description="Custom slug; auto-generated if omitted.",
        ),
    ] = None
    expires_at: datetime | None = None

    @field_validator("expires_at")
    @classmethod
    def expires_at_must_be_future(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("expires_at must include timezone information (UTC recommended)")
        if value is not None and value <= datetime.now(value.tzinfo):
            raise ValueError("expires_at must be in the future")
        return value


class LinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    target_url: str
    click_count: int
    created_at: datetime
    expires_at: datetime | None


class LinkCreateResponse(BaseModel):
    slug: str
    target_url: str
    short_url: str
    expires_at: datetime | None
    created_at: datetime


class ClickAnalytics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clicked_at: datetime
    user_agent: str | None
