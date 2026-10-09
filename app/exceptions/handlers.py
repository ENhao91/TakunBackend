from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = []
    for error in exc.errors():
        loc = ".".join(str(part) for part in error.get("loc", ()))
        msg = error.get("msg", "驗證失敗")
        if loc:
            messages.append(f"{loc}: {msg}")
        else:
            messages.append(msg)
    return JSONResponse(status_code=400, content={"message": "; ".join(messages)})


async def http_exception_handler(request: Request, exc):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


async def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": "伺服器發生未預期錯誤。"})


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unexpected_exception_handler)
