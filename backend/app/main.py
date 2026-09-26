"""FastAPI entrypoint. One process. Synthetic state lives only in this process."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import load_local_env
from app.errors import AppError
from app.logging_config import configure_logging, get_logger, request_id_var
from app.reasoning.factory import build_provider
from app.reasoning.provider import DecisionProvider
from app.runtime import Runtime

logger = get_logger(__name__)


def create_app(
    provider: DecisionProvider | None = None,
    data_dir: Path | None = None,
    *,
    use_atlas: bool | None = None,
    force_fake_embeddings: bool = False,
) -> FastAPI:
    configure_logging()
    repo_root = Path(__file__).resolve().parents[2]
    if provider is None:
        load_local_env(repo_root)
        provider = build_provider()
    runtime = Runtime(
        data_dir or (repo_root / "data"),
        provider,
        repo_root / "domain_packs",
        use_atlas=use_atlas,
        force_fake_embeddings=force_fake_embeddings,
    )
    app = FastAPI(title="Mulanous Lite", version="0.1.0")
    app.state.runtime = runtime
    _add_middleware(app)
    app.include_router(router, prefix="/api")
    _add_error_handlers(app)
    return app


def _add_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def bind_request_id(request: Request, call_next):  # type: ignore[no-untyped-def]
        token = request_id_var.set(uuid.uuid4().hex[:12])
        request_id = request_id_var.get()
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response


def _add_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": "Invalid request"})

    @app.exception_handler(Exception)
    async def unexpected(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("request_failed error_type=%s", type(exc).__name__)
        return JSONResponse(status_code=500, content={"error": "The request failed safely"})


app = create_app()
