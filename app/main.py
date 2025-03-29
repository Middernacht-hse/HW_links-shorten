from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from .cache import redis_client

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/links/shorten", response_model=schemas.Link)
def create_short_link(link: schemas.LinkCreate, db: Session = Depends(get_db)):
    return crud.create_link(db, link)

@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    cached_url = redis_client.get(short_code)
    if cached_url:
        return {"url": cached_url.decode("utf-8")}

    db_link = crud.get_link_by_short_code(db, short_code)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    redis_client.set(short_code, db_link.original_url)
    return {"url": db_link.original_url}

@app.delete("/links/{short_code}")
def delete_short_link(short_code: str, db: Session = Depends(get_db)):
    crud.delete_link(db, short_code)
    redis_client.delete(short_code)
    return {"message": "Link deleted"}

@app.put("/links/{short_code}")
def update_short_link(short_code: str, original_url: str, db: Session = Depends(get_db)):
    db_link = crud.update_link(db, short_code, original_url)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    redis_client.set(short_code, db_link.original_url)
    return db_link

@app.get("/links/{short_code}/stats", response_model=schemas.Link)
def get_link_statistics(short_code: str, db: Session = Depends(get_db)):
    db_link = crud.get_link_stats(db, short_code)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link

@app.get("/links/search")
def search_link(original_url: str, db: Session = Depends(get_db)):
    db_link = crud.search_link_by_url(db, original_url)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link