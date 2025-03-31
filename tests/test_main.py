from datetime import datetime, timedelta
from app.schemas import LinkCreate
from app import crud

def test_create_short_link(client):
    # Успешное создание ссылки
    response = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com", "custom_alias": "test"}
    )
    assert response.status_code == 200
    assert response.json()["short_code"] == "test"

    # Ошибка при повторном использовании alias
    response = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com", "custom_alias": "test"}
    )
    assert response.status_code == 400

def test_redirect_link(client, db):
    # Создаем ссылку
    link = LinkCreate(original_url="https://example.com")
    link = crud.create_link(db, link)

    # Проверяем редирект
    response = client.get("/links/" + link.short_code, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"

def test_delete_link(client, db):
    link = LinkCreate(original_url="https://example.com")
    db_link = crud.create_link(db, link)

    # Удаляем ссылку
    response = client.delete(f"/links/{db_link.short_code}")
    assert response.status_code == 200
    assert response.json()["message"] == "Link deleted successfully"

    # Проверяем, что ссылка удалена
    response = client.get(f"/links/{db_link.short_code}/stats")
    assert response.status_code == 404