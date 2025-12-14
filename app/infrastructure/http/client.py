from __future__ import annotations

import httpx


def build_httpx_client(
    timeout_s: float = 10.0,
    headers: dict[str, str] | None = None,
) -> httpx.AsyncClient:
    """
    Factory for a shared httpx.AsyncClient instance.

    Created at application startup and closed on shutdown.
    """
    return httpx.AsyncClient(
        headers=headers,
        timeout=httpx.Timeout(timeout_s),
    )
