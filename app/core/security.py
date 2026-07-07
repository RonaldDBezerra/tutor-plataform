"""Security helpers for administrative API access."""

from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

admin_api_key_header = APIKeyHeader(
    name="X-ADMIN-KEY",
    auto_error=False,
    scheme_name="AdminApiKey",
    description="Provide the configured admin API key through the X-ADMIN-KEY header.",
)


def require_admin_api_key(api_key: str | None = Security(admin_api_key_header)) -> None:
    """Validate the admin API key provided by the client."""

    expected_api_key = settings.ADMIN_API_KEY
    if not expected_api_key or api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
        )
