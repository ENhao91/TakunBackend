# Church Media Backend

FastAPI 後端專案，依照教會影音網站的 API 規格實作，支援分類與影片管理。

## 技術棧

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL / SQLite（本地測試）
- pytest

## 目錄結構

- `app/`：FastAPI 應用程式與分層程式碼
- `alembic/`：資料庫 migration
- `tests/`：API 測試

## 啟動方式

1. 建立虛擬環境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

2. 安裝依賴

```bash
python -m pip install -r requirements.txt
```

3. 設定環境變數

複製 `.env.example` 成 `.env`，填入 Neon PostgreSQL 實際連線資訊：

```bash
DB_URL=postgresql+psycopg://HOST:5432/DATABASE?sslmode=require
DB_USERNAME=YOUR_DATABASE_USERNAME
DB_PASSWORD=YOUR_DATABASE_PASSWORD
```

新增影片前，請先手動將影片上傳至 Google Drive，並取得影片分享網址。`POST /api/videos/create` 使用 `application/json`，欄位為 `title`、`description`、`categoryId` 和 `driveUrl`。後端驗證網址為 Google Drive 檔案連結後，將網址連同影片資料保存到資料庫；後端不會上傳或修改 Drive 檔案。請確認分享權限允許預期的觀眾觀看影片。

4. 啟動應用程式

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. 開啟 API 文件

- Swagger UI: http://localhost:8000/docs

## 測試

```bash
pytest -q
```

## 目前限制

- Google Drive 播放權限依分享連結及檔案權限設定而定；後端不會自動調整權限。
- 本地測試使用 SQLite，主要用於驗證 FastAPI / SQLAlchemy / API 邏輯；正式環境請使用 Neon PostgreSQL 的實際連線字串。
