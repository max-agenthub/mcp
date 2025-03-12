"""Entry point for running MCP servers directly.

This module allows running MCP servers directly with python -m mcp_servers.
"""

import argparse
import asyncio
import logging
import sys

from mcp.server.stdio import stdio_server

from . import MCPServerRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_server(server_name: str) -> int:
    """Run an MCP server with stdio transport.
    
    Args:
        server_name: Name of the server to run
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Get server info from registry
    server_info = MCPServerRegistry.get_server(server_name)
    if not server_info:
        logger.error(f"Server '{server_name}' not found")
        return 1
    
    logger.info(f"Starting server: {server_name}")
    
    try:
        # Import the module
        import mcp_servers
        
        # Get the server instance
        server_instance = getattr(mcp_servers, f"{server_name}_server")
        await server_instance.initialize()
        server = await server_instance.create_server()
        
        logger.info(f"Server '{server_name}' initialized")
        
        # Run the server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
        
        return 0
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to create server '{server_name}': {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run an MCP server directly")
    parser.add_argument(
        "server_name",
        help="Name of the server to run",
        choices=[server.name for server in MCPServerRegistry.list_servers()],
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available servers",
    )
    
    args = parser.parse_args()
    
    # Handle --list flag
    if args.list:
        print("Available MCP servers:")
        for server in MCPServerRegistry.list_servers():
            print(f"  - {server.name}: {server.description}")
        return 0
    
    # Run the server
    return asyncio.run(run_server(args.server_name))


if __name__ == "__main__":
    sys.exit(main()) 