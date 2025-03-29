from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    short_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=True)
    clicks = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)