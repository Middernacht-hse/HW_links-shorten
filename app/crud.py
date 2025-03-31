from sqlalchemy.orm import Session
from . import models, schemas
import secrets
import string
from datetime import datetime
from sqlalchemy import and_, or_

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def create_link(db: Session, link: schemas.LinkCreate):
    short_code = link.custom_alias or generate_short_code()
    db_link = models.Link(
        original_url=str(link.original_url),
        short_code=short_code,
        custom_alias=link.custom_alias,
        expires_at=link.expires_at
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def get_link_by_short_code(db: Session, short_code: str):
    return db.query(models.Link).filter(models.Link.short_code == short_code).first()

def delete_link(db: Session, short_code: str):
    db_link = get_link_by_short_code(db, short_code)
    if db_link:
        db.delete(db_link)
        db.commit()
        return True
    return False

def update_link_url(
    db: Session,
    short_code: str,
    new_url: str
):
    """Обновляет оригинальный URL для указанной короткой ссылки"""
    link = get_link_by_short_code(db, short_code)
    if link:
        link.original_url = new_url
        db.add(link)
        db.commit()
        db.refresh(link)
    return link


def search_links(db: Session, original_url: str):
    return db.query(models.Link).filter(models.Link.original_url.contains(original_url)).all()


def get_active_link(db: Session, short_code: str):
    """Получает активную непросроченную ссылку"""
    now = datetime.utcnow()
    return db.query(models.Link).filter(
        models.Link.short_code == short_code,
        models.Link.is_active == True,
        or_(
            models.Link.expires_at.is_(None),
            models.Link.expires_at > now
        )
    ).first()


async def delete_expired_links(db: Session):
    """Удаляет все просроченные ссылки"""
    now = datetime.utcnow()
    expired_links = db.query(models.Link).filter(
        and_(
            models.Link.expires_at.is_not(None),
            models.Link.expires_at <= now,
            models.Link.is_active == True
        )
    ).all()

    for link in expired_links:
        link.is_active = False

    db.commit()
    return len(expired_links)