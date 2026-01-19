"""HTTP/SSE server for Blok MCP - used for Render deployment."""

import logging
import os
import sys
from typing import Optional

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn

from blok_mcp.config import config
from blok_mcp.mcp_server import BlokMCPServer

# Set up logging
logging.basicConfig(
    level=logging.INFO if config.debug else logging.WARNING,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app() -> Starlette:
    """Create the Starlette application with SSE transport."""

    # Create the MCP server instance
    pre_auth_token = config.access_token if config.access_token else None
    auto_auth_email = config.email if config.email and config.password else None
    auto_auth_password = config.password if config.email and config.password else None

    mcp_server = BlokMCPServer(
        pre_auth_token=pre_auth_token,
        auto_auth_email=auto_auth_email,
        auto_auth_password=auto_auth_password,
    )

    # Create SSE transport
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        """Handle SSE connections."""
        # Check for session token in header (for pre-auth)
        session_token = request.headers.get("X-Session-Token")
        if session_token and not mcp_server.session_manager.is_authenticated:
            logger.info("Setting session from X-Session-Token header")
            mcp_server.session_manager.set_token(session_token)

        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_server.server.run(
                streams[0],
                streams[1],
                mcp_server.server.create_initialization_options(),
            )

    async def handle_messages(request: Request):
        """Handle POST messages from SSE clients."""
        await sse.handle_post_message(request.scope, request.receive, request._send)

    async def health_check(request: Request):
        """Health check endpoint for Render."""
        return JSONResponse({"status": "ok", "service": "blok-mcp"})

    # Create routes
    routes = [
        Route("/health", health_check, methods=["GET"]),
        Route("/sse/", handle_sse, methods=["GET"]),
        Route("/messages/", handle_messages, methods=["POST"]),
        # Also support /sse without trailing slash
        Route("/sse", handle_sse, methods=["GET"]),
    ]

    app = Starlette(
        debug=config.debug,
        routes=routes,
    )

    return app


def main():
    """Run the HTTP server."""
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"Starting Blok MCP HTTP server on {host}:{port}")
    logger.info(f"Blok API URL: {config.blok_api_url}")

    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
