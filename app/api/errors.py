"""The error envelope and the handlers that guarantee every failure uses it."""

import logging
from typing import Any, Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# The six codes in the assessment pdf plus two 1. a malformed request 
# that never reaches our own validation 2. a bug in this service. 
ErrorCode = Literal[
    "file_too_large",
    "unsupported_format",
    "empty_file",
    "missing_file",
    "invalid_language",
    "provider_error",
    "invalid_request",
    "internal_error",
]

_STATUS_BY_CODE: dict[ErrorCode, int] = {
    "missing_file": 400,
    "empty_file": 400,
    "invalid_language": 400,
    "file_too_large": 413,
    "unsupported_format": 415,
    "invalid_request": 422,
    "internal_error": 500,
    "provider_error": 502,
}


class ErrorBody(BaseModel):
    code: ErrorCode
    message: str
    detail: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    error: ErrorBody


class ApiError(Exception):
    """A failure we chose to raise, carrying its own envelope fields."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code: ErrorCode = code
        self.message = message
        self.detail = detail or {}
        self.status_code = _STATUS_BY_CODE[code]


def _envelope(
    status_code: int,
    code: ErrorCode,
    message: str,
    detail: dict[str, Any],
) -> JSONResponse:
    body = ErrorResponse(error=ErrorBody(code=code, message=message, detail=detail))
    return JSONResponse(status_code=status_code, content=body.model_dump())


async def handle_api_error(request: Request, exc: Exception) -> JSONResponse:
    """Every failure this service raises on purpose."""
    assert isinstance(exc, ApiError)
    return _envelope(exc.status_code, exc.code, exc.message, exc.detail)


async def handle_request_validation_error(
    request: Request, exc: Exception
) -> JSONResponse:
    """FastAPI's own 422, reshaped into the envelope.

    The routes validate their uploads themselves so this stays unreachable in
    normal use, but an unreshaped 422 would still break the contract.
    """
    assert isinstance(exc, RequestValidationError)
    fields = [
        {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
        for error in exc.errors()
    ]
    return _envelope(
        _STATUS_BY_CODE["invalid_request"],
        "invalid_request",
        "The request could not be validated.",
        {"fields": fields},
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """A bug in this service. Logged in full, described to the caller in general terms."""
    logger.exception("Unhandled error serving %s %s", request.method, request.url.path)
    return _envelope(
        _STATUS_BY_CODE["internal_error"],
        "internal_error",
        "The service failed while handling this request.",
        {},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, handle_api_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
