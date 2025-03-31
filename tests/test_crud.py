from datetime import datetime, timedelta
from app.schemas import LinkCreate
from app.crud import create_link, get_link_by_short_code, delete_link

def test_create_link(db):
    link = LinkCreate(original_url="https://example.com/")
    db_link = create_link(db, link)
    assert db_link.original_url == "https://example.com/"
    assert len(db_link.short_code) == 6

def test_get_link(db):
    link = LinkCreate(original_url="https://example.com/")
    db_link = create_link(db, link)
    found_link = get_link_by_short_code(db, db_link.short_code)
    assert found_link is not None
    assert found_link.original_url == "https://example.com/"

def test_delete_link(db):
    link = LinkCreate(original_url="https://example.com/")
    db_link = create_link(db, link)
    assert delete_link(db, db_link.short_code) is True
    assert get_link_by_short_code(db, db_link.short_code) is None