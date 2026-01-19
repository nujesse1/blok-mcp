"""Session state management for MCP server."""

from dataclasses import dataclass
from typing import Optional

from blok_mcp.auth.authenticator import BlokAuthenticator, AuthenticationError
from blok_mcp.client.api_client import BlokAPIClient


@dataclass
class SessionState:
    """Authentication session state."""

    access_token: str
    refresh_token: str
    email: str
    user_id: str
    tenant_id: str


class SessionManager:
    """Manages authentication state and provides authenticated API client."""

    def __init__(self, blok_api_url: str):
        """Initialize session manager.

        Args:
            blok_api_url: Base URL for Blok API
        """
        self.blok_api_url = blok_api_url
        self.authenticator = BlokAuthenticator(blok_api_url)
        self._session: Optional[SessionState] = None
        self._client: Optional[BlokAPIClient] = None

    @property
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self._session is not None

    @property
    def session_info(self) -> Optional[dict]:
        """Get current session information.

        Returns:
            Dictionary with session details or None if not authenticated
        """
        if not self._session:
            return None

        return {
            "email": self._session.email,
            "user_id": self._session.user_id,
            "tenant_id": self._session.tenant_id,
        }

    def set_token(self, access_token: str, email: str = "", user_id: str = "", tenant_id: str = ""):
        """Set authentication from a pre-supplied token.

        Args:
            access_token: JWT access token
            email: Optional user email
            user_id: Optional user ID
            tenant_id: Optional tenant ID
        """
        # Close any existing client first
        if self._client:
            # Note: This is sync, so we can't properly close async client
            self._client = None

        self._session = SessionState(
            access_token=access_token,
            refresh_token="",
            email=email,
            user_id=user_id,
            tenant_id=tenant_id,
        )

        # Create new API client for this session
        self._client = BlokAPIClient(
            access_token=self._session.access_token,
            base_url=self.blok_api_url,
        )

    async def clear_client(self):
        """Close and clear the API client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def authenticate_async(self, email: str, password: str) -> SessionState:
        """Authenticate user and store session (async version).

        Args:
            email: User email address
            password: User password

        Returns:
            Session state with authentication info

        Raises:
            AuthenticationError: If authentication fails
        """
        # Close any existing client first
        await self.clear_client()

        # Run Supabase authentication flow
        session_info = self.authenticator.authenticate(email, password)

        # Create session state
        self._session = SessionState(
            access_token=session_info["access_token"],
            refresh_token=session_info["refresh_token"],
            email=session_info["email"],
            user_id=session_info["user_id"],
            tenant_id=session_info["tenant_id"],
        )

        # Create new API client for this session
        self._client = BlokAPIClient(
            access_token=self._session.access_token,
            base_url=self.blok_api_url,
        )

        return self._session

    def authenticate(self, email: str, password: str) -> SessionState:
        """Authenticate user and store session (sync version for compatibility).

        Note: This creates a client but doesn't properly clean up old ones.
        Use authenticate_async() for proper resource management.

        Args:
            email: User email address
            password: User password

        Returns:
            Session state with authentication info

        Raises:
            AuthenticationError: If authentication fails
        """
        # Run Supabase authentication flow
        session_info = self.authenticator.authenticate(email, password)

        # Create session state
        self._session = SessionState(
            access_token=session_info["access_token"],
            refresh_token=session_info["refresh_token"],
            email=session_info["email"],
            user_id=session_info["user_id"],
            tenant_id=session_info["tenant_id"],
        )

        # Create new API client for this session
        # Note: This doesn't close the old client, which could leak resources
        self._client = BlokAPIClient(
            access_token=self._session.access_token,
            base_url=self.blok_api_url,
        )

        return self._session

    def get_client(self) -> BlokAPIClient:
        """Get authenticated API client.

        Returns:
            Authenticated Blok API client

        Raises:
            RuntimeError: If not authenticated
        """
        if not self._session or not self._client:
            raise RuntimeError(
                "Not authenticated. Call authenticate() first or provide email/password to the tool."
            )

        return self._client

    async def clear(self):
        """Clear current session and close client."""
        await self.clear_client()
        self._session = None
