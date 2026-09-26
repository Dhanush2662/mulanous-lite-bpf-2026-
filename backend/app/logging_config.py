"""Request-scoped logging. Never log secrets or full prompts."""

from __future__ import annotations

import logging
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

_FORMAT = "%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s"
_configured = False


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging() -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(level=logging.INFO, format=_FORMAT)
    for handler in logging.getLogger().handlers:
        handler.addFilter(RequestIdFilter())
    _configured = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
