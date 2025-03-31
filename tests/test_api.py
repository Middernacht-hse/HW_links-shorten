import pytest
from fastapi import status
from datetime import datetime, timedelta
import time


def test_create_short_link(client):
    """Тестируем создание короткой ссылки через API"""
    response = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "short_code" in data
    assert len(data["short_code"]) == 6


def test_create_custom_link(client):
    """Тестируем создание кастомной ссылки"""
    response = client.post(
        "/links/shorten",
        json={
            "original_url": "https://example.com",
            "custom_alias": "test123"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["short_code"] == "test123"


def test_create_invalid_url(client):
    """Тестируем обработку невалидного URL"""
    response = client.post(
        "/links/shorten",
        json={"original_url": "not-a-url"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_link_url(client, db):
    # Сначала создаем тестовую ссылку
    create_res = client.post(
        "/links/shorten",
        json={"original_url": "https://old-example.com"}
    )
    short_code = create_res.json()["short_code"]

    # Тестируем обновление
    update_res = client.put(
        f"/links/{short_code}",
        json={"original_url": "https://new-example.com"}
    )

    assert update_res.status_code == 200
    assert update_res.json()["original_url"] == "https://new-example.com/"


def test_update_nonexistent_link(client):
    response = client.put(
        "/links/invalid_code",
        json={"original_url": "https://example.com"}
    )
    assert response.status_code == 404


def test_search_links(client, db):
    # 1. Сначала создаём тестовые данные
    test_urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://other-site.com/main"
    ]

    for i, url in enumerate(test_urls):
        response = client.post(
            "/links/shorten",
            json={
                "original_url": url,
                "custom_alias": "test" + str(i)
            }
        )
        assert response.status_code == 200

    client.get("/links/test0")
    response = client.get("/links/test0/stats")

    # 2. Тестируем поиск
    response = client.get("/links/search?original_url=example.com")

    # 3. Проверяем результаты
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert all("example.com" in link["original_url"] for link in results)
    assert not any("other-site" in link["original_url"] for link in results)

def test_search_links_empty(client):
    response = client.get("/links/search?original_url=nonexistent.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "No links found matching the search criteria"


def test_expired_link_auto_deletion(client, db):
    # 1. Создаем ссылку с коротким сроком жизни (2 секунды)
    expires_at = (datetime.utcnow() + timedelta(seconds=2)).isoformat()
    print(expires_at)
    res = client.post(
        "/links/shorten",
        json={
            "original_url": "https://expiring.com",
            "expires_at": expires_at
        }
    )
    assert res.status_code == 200
    short_code = res.json()["short_code"]
    print(short_code)

    # 2. Проверяем, что ссылка сразу доступна
    redirect_res = client.get(f"/links/{short_code}", follow_redirects=False)
    assert redirect_res.status_code == 307
    assert redirect_res.headers["location"] == "https://expiring.com/"

    # 3. Ждем истечения срока (3 секунды для гарантии)
    time.sleep(3)

    # 4. Проверяем, что теперь ссылка не найдена
    expired_res = client.get(f"/{short_code}")
    assert expired_res.status_code == 404
