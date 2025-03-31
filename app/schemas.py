from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = None
    expires_at: Optional[datetime] = Field(
        None,
        example="2023-12-31T23:59:59",
        description="Дата автоматического удаления ссылки"
    )

class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    clicks: int
    last_clicked_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class LinkUpdate(BaseModel):
    original_url: HttpUrl

class LinkSearchResult(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    clicks: int

    class Config:
        orm_mode = True