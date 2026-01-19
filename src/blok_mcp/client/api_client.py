"""Authenticated HTTP client for Blok API."""

import httpx
from typing import Any, Optional


class APIError(Exception):
    """Raised when API request fails."""
    pass


class BlokAPIClient:
    """Async HTTP client with automatic Bearer token injection."""

    def __init__(self, access_token: str, base_url: str, timeout: float = 30.0):
        """Initialize API client.

        Args:
            access_token: JWT access token from authentication
            base_url: Base URL for Blok API (e.g., https://app.joinblok.co)
            timeout: Request timeout in seconds
        """
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    def _build_url(self, path: str) -> str:
        """Build full URL with /api/v1 prefix.

        Args:
            path: API path (e.g., /personas or personas)

        Returns:
            Full URL
        """
        # Remove leading slash if present
        path = path.lstrip("/")

        # Add /api/v1 prefix if not present
        if not path.startswith("api/v1/"):
            path = f"api/v1/{path}"

        return f"{self.base_url}/{path}"

    def _get_headers(self, extra_headers: Optional[dict] = None) -> dict:
        """Build request headers with Bearer token.

        Args:
            extra_headers: Additional headers to include

        Returns:
            Headers dictionary
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        if extra_headers:
            headers.update(extra_headers)

        return headers

    async def get(self, path: str, params: Optional[dict] = None, **kwargs) -> Any:
        """Send GET request to Blok API.

        Args:
            path: API path
            params: Query parameters
            **kwargs: Additional httpx request arguments

        Returns:
            Response JSON data

        Raises:
            APIError: If request fails
        """
        try:
            url = self._build_url(path)
            headers = self._get_headers(kwargs.pop("headers", None))

            response = await self.client.get(
                url,
                headers=headers,
                params=params,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_msg = f"API request failed ({e.response.status_code})"

            try:
                error_data = e.response.json()
                detail = error_data.get("detail", "")
                if detail:
                    error_msg = f"{error_msg}: {detail}"
            except Exception:
                pass

            raise APIError(error_msg) from e

        except httpx.RequestError as e:
            raise APIError(f"Network error: {e}") from e

    async def post(
        self,
        path: str,
        json: Optional[dict] = None,
        **kwargs,
    ) -> Any:
        """Send POST request to Blok API.

        Args:
            path: API path
            json: JSON body data
            **kwargs: Additional httpx request arguments

        Returns:
            Response JSON data

        Raises:
            APIError: If request fails
        """
        try:
            url = self._build_url(path)
            headers = self._get_headers(kwargs.pop("headers", None))

            response = await self.client.post(
                url,
                headers=headers,
                json=json,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_msg = f"API request failed ({e.response.status_code})"

            try:
                error_data = e.response.json()
                detail = error_data.get("detail", "")
                if detail:
                    error_msg = f"{error_msg}: {detail}"
            except Exception:
                pass

            raise APIError(error_msg) from e

        except httpx.RequestError as e:
            raise APIError(f"Network error: {e}") from e

    async def aclose(self):
        """Close the HTTP client properly."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
