"""Supabase authentication for Blok API."""

import httpx
from typing import Optional


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class BlokAuthenticator:
    """Handles authentication with Blok API via Supabase signin endpoint."""

    def __init__(self, blok_api_url: str):
        """Initialize authenticator with API URL.

        Args:
            blok_api_url: Base URL for Blok API (e.g., https://app.joinblok.co)
        """
        self.blok_api_url = blok_api_url.rstrip("/")

    def authenticate(self, email: str, password: str) -> dict:
        """Authenticate via Supabase signin endpoint.

        Args:
            email: User email address
            password: User password

        Returns:
            Dictionary with authentication info:
                - access_token: JWT access token for API calls
                - refresh_token: Token for refreshing access
                - email: User email
                - user_id: Supabase user ID
                - tenant_id: Organization tenant ID

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            response = httpx.post(
                f"{self.blok_api_url}/api/v1/auth/signin",
                json={"email": email, "password": password},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            # Validate required fields
            access_token = data.get("access_token")
            if not access_token:
                raise AuthenticationError("No access token in response")

            return {
                "access_token": access_token,
                "refresh_token": data.get("refresh_token", ""),
                "email": data.get("email", email),
                "user_id": data.get("user_id", ""),
                "tenant_id": data.get("tenant_id", ""),
            }

        except httpx.HTTPStatusError as e:
            error_msg = "Authentication failed"

            try:
                error_data = e.response.json()
                detail = error_data.get("detail", "")
                if detail:
                    error_msg = f"{error_msg}: {detail}"
            except Exception:
                pass

            if e.response.status_code == 401:
                raise AuthenticationError("Invalid email or password")
            elif e.response.status_code == 404:
                raise AuthenticationError("User not found")
            else:
                raise AuthenticationError(error_msg)

        except httpx.RequestError as e:
            raise AuthenticationError(f"Network error during authentication: {e}")
