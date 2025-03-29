from pydantic import BaseModel
from datetime import datetime

class LinkBase(BaseModel):
    original_url: str

class LinkCreate(LinkBase):
    custom_alias: str = None
    expires_at: datetime = None

class Link(LinkBase):
    short_code: str
    created_at: datetime
    expires_at: datetime = None
    clicks: int
    last_accessed: datetime = None

    class Config:
        orm_mode = True