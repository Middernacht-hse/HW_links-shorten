from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
import datetime
from .database import get_db
from fastapi import Query
from typing import List
from fastapi import BackgroundTasks
from .task import delete_expired_links_task

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/links/shorten", response_model=schemas.LinkResponse)
async def create_short_link(
        link: schemas.LinkCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    if link.custom_alias and crud.get_link_by_short_code(db, link.custom_alias):
        raise HTTPException(status_code=400, detail="Custom alias already exists")
    db_link = crud.create_link(db, link)

    if link.expires_at:
        # Запланировать проверку перед самым expires_at
        delay = (link.expires_at - datetime.datetime.utcnow()).total_seconds()
        background_tasks.add_task(
            delete_expired_links_task,
            db_link.id,
            run_at=link.expires_at
        )

    return db_link

@app.get("/links/search", response_model=List[schemas.LinkResponse])
def search_links(
    original_url: str = Query(..., description="Part of URL to search for"),
    db: Session = Depends(get_db)
):
    """Search links by original URL (partial match)"""
    print()
    links = crud.search_links(db, original_url)
    if not links:
        raise HTTPException(
            status_code=404,
            detail="No links found matching the search criteria"
        )
    return links

@app.get("/links/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    link = crud.get_link_by_short_code(db, short_code)
    if not link or not link.is_active:
        raise HTTPException(status_code=404, detail="Link not found or expired")
    link.clicks += 1
    link.last_clicked_at = datetime.datetime.utcnow()
    db.commit()
    return RedirectResponse(url=link.original_url)

@app.get("/links/{short_code}/stats", response_model=schemas.LinkResponse)
def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    link = crud.get_link_by_short_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link

@app.delete("/links/{short_code}")
def delete_short_link(short_code: str, db: Session = Depends(get_db)):
    if not crud.delete_link(db, short_code):
        raise HTTPException(status_code=404, detail="Link not found")
    return {"message": "Link deleted successfully"}

@app.put("/links/{short_code}", response_model=schemas.LinkResponse)
def update_link(
    short_code: str,
    link_update: schemas.LinkUpdate,
    db: Session = Depends(get_db)
):
    """Обновляет оригинальный URL для короткой ссылки"""
    updated_link = crud.update_link_url(db, short_code, str(link_update.original_url))
    if not updated_link:
        raise HTTPException(status_code=404, detail="Link not found")
    return updated_link
