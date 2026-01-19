"""Entry point for Blok MCP server.

Run with: python -m blok_mcp
"""

import asyncio
import logging
import sys

from blok_mcp.mcp_server import BlokMCPServer

# Ensure all logging goes to stderr for MCP stdio communication
logging.basicConfig(
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        server = BlokMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Shutting down Blok MCP server...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
