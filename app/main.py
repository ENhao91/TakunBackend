from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.categories import router as categories_router
from app.api.routes.videos import router as videos_router
from app.exceptions.handlers import register_exception_handlers

app = FastAPI(title="Church Video API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(categories_router)
app.include_router(videos_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
