import os

os.environ.setdefault("DB_URL", "sqlite:///./test_backend.db")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_video_create_openapi_accepts_drive_url_as_json():
    operation = app.openapi()["paths"]["/api/videos/create"]["post"]
    content = operation["requestBody"]["content"]
    assert "application/json" in content

    schema_ref = content["application/json"]["schema"]["$ref"]
    fields = app.openapi()["components"]["schemas"][schema_ref.rsplit("/", 1)[-1]]["properties"]
    assert {"title", "description", "categoryId", "driveUrl"}.issubset(fields)
    assert "file" not in fields


def test_list_categories_returns_empty_list():
    response = client.post("/api/categories/list", json={})
    assert response.status_code == 200
    assert response.json() == []


def test_create_category_and_list_it():
    payload = {"name": "醫治疾病"}
    response = client.post("/api/categories/create", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "醫治疾病"
    assert data["sortOrder"] >= 1

    list_response = client.post("/api/categories/list", json={})
    assert list_response.status_code == 200
    names = [item["name"] for item in list_response.json()]
    assert "醫治疾病" in names


def test_create_category_alias_route_adds_category():
    response = client.post("/api/categories/add", json={"name": "新建分類測試"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "新建分類測試"

    list_response = client.post("/api/categories/list", json={})
    assert list_response.status_code == 200
    names = [item["name"] for item in list_response.json()]
    assert "新建分類測試" in names


def test_rejects_blank_category_name():
    response = client.post("/api/categories/create", json={"name": "   "})
    assert response.status_code == 400


def test_create_video_requires_valid_category():
    response = client.post(
        "/api/videos/create",
        json={
            "title": "測試影片",
            "description": "說明",
            "categoryId": 9999,
            "driveUrl": "https://drive.google.com/file/d/1UVLkCL002rJxerw7X8YRb0GC6us9JUIS/view?usp=drive_link",
        },
    )
    assert response.status_code == 404


def test_video_create_stores_drive_url_and_search_is_case_insensitive():
    create_category = client.post("/api/categories/create", json={"name": "禱告"})
    category_id = create_category.json()["id"]
    drive_url = "https://drive.google.com/file/d/1UVLkCL002rJxerw7X8YRb0GC6us9JUIS/view?usp=drive_link"
    create_response = client.post(
        "/api/videos/create",
        json={
            "title": "禱告見證",
            "description": "不要命中這個描述",
            "categoryId": category_id,
            "driveUrl": drive_url,
        },
    )
    assert create_response.status_code == 200
    created_video = create_response.json()
    assert created_video["playbackUrl"] == drive_url

    response = client.post("/api/videos/search", json={"keyword": "禱告", "page": 0, "size": 20})
    assert response.status_code == 200
    payload = response.json()
    assert payload["totalElements"] >= 1
    search_item = next(item for item in payload["items"] if item["title"] == "禱告見證")
    assert search_item["description"] == "不要命中這個描述"
    assert search_item["playbackUrl"] == drive_url

    list_response = client.post(
        "/api/videos/list",
        json={"categoryId": category_id, "page": 0, "size": 20},
    )
    assert list_response.status_code == 200
    list_item = next(item for item in list_response.json()["items"] if item["title"] == "禱告見證")
    assert list_item["description"] == "不要命中這個描述"
    assert list_item["playbackUrl"] == drive_url


def test_create_video_rejects_non_google_drive_urls():
    category_response = client.post("/api/categories/create", json={"name": "不合法連結測試"})
    response = client.post(
        "/api/videos/create",
        json={
            "title": "測試影片",
            "categoryId": category_response.json()["id"],
            "driveUrl": "https://example.com/video.mp4",
        },
    )
    assert response.status_code == 400
