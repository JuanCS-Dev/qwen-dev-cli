"""
Async HTTP Client.

SCALE & SUSTAIN Phase 3.1 - Async Everywhere.

Async HTTP client using httpx with connection pooling.
Falls back to aiohttp or requests in thread pool if httpx not available.

Author: JuanCS Dev
Date: 2025-11-26
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

# Try to import httpx (preferred), fallback options
try:
    import httpx
    HTTP_CLIENT = 'httpx'
except ImportError:
    httpx = None
    try:
        import aiohttp
        HTTP_CLIENT = 'aiohttp'
    except ImportError:
        aiohttp = None
        HTTP_CLIENT = 'requests'


@dataclass
class HttpResponse:
    """HTTP response wrapper."""

    status_code: int
    headers: Dict[str, str]
    content: bytes
    url: str
    elapsed_ms: float = 0.0

    @property
    def text(self) -> str:
        """Response body as text."""
        return self.content.decode('utf-8', errors='replace')

    @property
    def ok(self) -> bool:
        """Check if request succeeded (2xx status)."""
        return 200 <= self.status_code < 300

    def json(self) -> Any:
        """Parse response as JSON."""
        import json
        return json.loads(self.content)

    def raise_for_status(self) -> None:
        """Raise exception for 4xx/5xx status codes."""
        if not self.ok:
            raise HttpError(
                f"HTTP {self.status_code} for {self.url}",
                status_code=self.status_code,
                response=self
            )


class HttpError(Exception):
    """HTTP request error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[HttpResponse] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


@dataclass
class HttpClient:
    """
    Async HTTP client with connection pooling.

    Usage:
        async with HttpClient() as client:
            response = await client.get('https://api.example.com/data')
            data = response.json()
    """

    base_url: str = ''
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    max_connections: int = 100
    _client: Any = field(default=None, repr=False)

    async def __aenter__(self) -> 'HttpClient':
        """Enter async context."""
        await self._init_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context."""
        await self.close()

    async def _init_client(self) -> None:
        """Initialize the underlying HTTP client."""
        if HTTP_CLIENT == 'httpx' and httpx:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout,
                limits=httpx.Limits(max_connections=self.max_connections)
            )
        elif HTTP_CLIENT == 'aiohttp' and aiohttp:
            connector = aiohttp.TCPConnector(limit=self.max_connections)
            timeout_obj = aiohttp.ClientTimeout(total=self.timeout)
            self._client = aiohttp.ClientSession(
                base_url=self.base_url if self.base_url else None,
                headers=self.headers,
                connector=connector,
                timeout=timeout_obj
            )

    async def close(self) -> None:
        """Close the client and release connections."""
        if self._client:
            if HTTP_CLIENT == 'httpx':
                await self._client.aclose()
            elif HTTP_CLIENT == 'aiohttp':
                await self._client.close()
            self._client = None

    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        data: Optional[Union[bytes, str, Dict]] = None,
        timeout: Optional[float] = None
    ) -> HttpResponse:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Additional headers
            params: Query parameters
            json: JSON body
            data: Form data or raw body
            timeout: Request timeout

        Returns:
            HttpResponse object
        """
        import time
        start = time.monotonic()

        timeout = timeout or self.timeout
        merged_headers = {**self.headers, **(headers or {})}

        if HTTP_CLIENT == 'httpx' and self._client:
            response = await self._client.request(
                method,
                url,
                headers=merged_headers,
                params=params,
                json=json,
                data=data,
                timeout=timeout
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            return HttpResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                url=str(response.url),
                elapsed_ms=elapsed_ms
            )

        elif HTTP_CLIENT == 'aiohttp' and self._client:
            full_url = f"{self.base_url}{url}" if self.base_url and not url.startswith('http') else url
            async with self._client.request(
                method,
                full_url,
                headers=merged_headers,
                params=params,
                json=json,
                data=data
            ) as response:
                content = await response.read()
                elapsed_ms = (time.monotonic() - start) * 1000
                return HttpResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    content=content,
                    url=str(response.url),
                    elapsed_ms=elapsed_ms
                )

        else:
            # Fallback to requests in thread pool
            import requests as req
            loop = asyncio.get_event_loop()

            def sync_request():
                full_url = f"{self.base_url}{url}" if self.base_url else url
                return req.request(
                    method,
                    full_url,
                    headers=merged_headers,
                    params=params,
                    json=json,
                    data=data,
                    timeout=timeout
                )

            response = await loop.run_in_executor(None, sync_request)
            elapsed_ms = (time.monotonic() - start) * 1000
            return HttpResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                url=response.url,
                elapsed_ms=elapsed_ms
            )

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> HttpResponse:
        """Make GET request."""
        return await self.request('GET', url, headers=headers, params=params, timeout=timeout)

    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        data: Optional[Union[bytes, str, Dict]] = None,
        timeout: Optional[float] = None
    ) -> HttpResponse:
        """Make POST request."""
        return await self.request('POST', url, headers=headers, json=json, data=data, timeout=timeout)

    async def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        data: Optional[Union[bytes, str, Dict]] = None,
        timeout: Optional[float] = None
    ) -> HttpResponse:
        """Make PUT request."""
        return await self.request('PUT', url, headers=headers, json=json, data=data, timeout=timeout)

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> HttpResponse:
        """Make DELETE request."""
        return await self.request('DELETE', url, headers=headers, timeout=timeout)

    async def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        data: Optional[Union[bytes, str, Dict]] = None,
        timeout: Optional[float] = None
    ) -> HttpResponse:
        """Make PATCH request."""
        return await self.request('PATCH', url, headers=headers, json=json, data=data, timeout=timeout)


# Convenience functions for one-off requests
async def get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    timeout: float = 30.0
) -> HttpResponse:
    """Make a GET request."""
    async with HttpClient(timeout=timeout) as client:
        return await client.get(url, headers=headers, params=params)


async def post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None,
    data: Optional[Union[bytes, str, Dict]] = None,
    timeout: float = 30.0
) -> HttpResponse:
    """Make a POST request."""
    async with HttpClient(timeout=timeout) as client:
        return await client.post(url, headers=headers, json=json, data=data)


__all__ = [
    'HttpClient',
    'HttpResponse',
    'HttpError',
    'get',
    'post',
    'HTTP_CLIENT',
]
