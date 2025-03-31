import asyncio
from datetime import datetime
from .database import SessionLocal
from .models import Link


async def delete_expired_links_task(link_id: int, run_at: datetime):
    """Фоновая задача для удаления просроченной ссылки"""
    delay = (run_at - datetime.utcnow()).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)

    db = SessionLocal()
    try:
        link = db.query(Link).get(link_id)
        if link and link.expires_at <= datetime.utcnow():
            link.is_active = False
            db.commit()
    finally:
        db.close()