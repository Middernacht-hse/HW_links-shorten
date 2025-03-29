import string
import random
from sqlalchemy.orm import Session
from . import models, schemas

def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits  # Буквы (A-Z, a-z) и цифры (0-9)
    return ''.join(random.choice(characters) for _ in range(length))

def create_link(db: Session, link: schemas.LinkCreate):
    short_code = link.custom_alias if link.custom_alias else generate_short_code()
    db_link = models.Link(
        original_url=link.original_url,
        short_code=short_code,
        expires_at=link.expires_at
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def get_link_by_short_code(db: Session, short_code: str):
    return db.query(models.Link).filter(models.Link.short_code == short_code).first()

def update_link(db: Session, short_code: str, original_url: str):
    db_link = get_link_by_short_code(db, short_code)
    if db_link:
        db_link.original_url = original_url
        db.commit()
        db.refresh(db_link)
    return db_link

def delete_link(db: Session, short_code: str):
    db_link = get_link_by_short_code(db, short_code)
    if db_link:
        db.delete(db_link)
        db.commit()
    return db_link

def get_link_stats(db: Session, short_code: str):
    return get_link_by_short_code(db, short_code)

def search_link_by_url(db: Session, original_url: str):
    return db.query(models.Link).filter(models.Link.original_url == original_url).first()