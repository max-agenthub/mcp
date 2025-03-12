"""Server manager for handling local and remote MCP servers.

This module provides functionality to manage and route to different MCP servers.
"""

import typing as t
import logging
import os
import asyncio
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.sse import sse_client
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import the MCP server registry directly from mcp_servers
# Make sure src directory is in sys.path (handled in __init__.py)
from mcp_servers import MCPServerRegistry

from .proxy_server import create_proxy_server

logger = logging.getLogger(__name__)


class ServerManager:
    """Manager for MCP servers.
    
    This class manages both local and remote MCP servers and provides
    a unified interface for creating and connecting to them.
    """
    
    def __init__(self) -> None:
        """Initialize the server manager."""
        self._active_servers: dict[str, Server] = {}
    
    def list_available_servers(self) -> list[str]:
        """List all available servers.
        
        Returns:
            List of server names
        """
        return [server.name for server in MCPServerRegistry.list_servers()]
    
    def get_server_info(self, name: str) -> t.Optional[dict[str, t.Any]]:
        """Get information about a server.
        
        Args:
            name: Name of the server
            
        Returns:
            Dictionary with server information
        """
        server_info = MCPServerRegistry.get_server(name)
        if not server_info:
            return None
        
        return {
            "name": server_info.name,
            "description": server_info.description,
            "server_type": server_info.server_type.name,
        }
    
    async def create_local_server(self, name: str) -> t.Optional[Server]:
        """Create a local MCP server.
        
        Args:
            name: Name of the server to create
            
        Returns:
            The created server or None if not found
        """
        server_info = MCPServerRegistry.get_server(name)
        if not server_info:
            logger.error(f"Server '{name}' not found")
            return None
        
        logger.info(f"Creating local server: {name}")
        
        # Import the server instance directly from mcp_servers
        try:
            # Import the module containing the server instance
            import mcp_servers
            
            # Get the server instance dynamically (e.g., slack_server, googlesheets_server)
            server_instance = getattr(mcp_servers, f"{name}_server")
            await server_instance.initialize()
            server = await server_instance.create_server()
            
            # Store the server
            self._active_servers[name] = server
            
            return server
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to create server '{name}': {e}")
            return None
    
    async def create_remote_server_connection(
        self, url: str, headers: dict[str, t.Any] = None
    ) -> t.Optional[ClientSession]:
        """Create a connection to a remote SSE MCP server.
        
        Args:
            url: URL of the remote server
            headers: Optional headers for the connection
            
        Returns:
            A client session for the remote server
        """
        try:
            streams = await sse_client(url=url, headers=headers)
            session = ClientSession(*streams)
            return session
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to connect to remote server at {url}: {e}")
            return None
    
    async def create_stdio_server_connection(
        self, command: str, args: list[str] = None, env: dict[str, str] = None
    ) -> t.Optional[ClientSession]:
        """Create a connection to a stdio MCP server.
        
        Args:
            command: Command to run
            args: Optional arguments for the command
            env: Optional environment variables
            
        Returns:
            A client session for the stdio server
        """
        try:
            params = StdioServerParameters(
                command=command,
                args=args or [],
                env=env or {},
            )
            streams = await stdio_client(params)
            session = ClientSession(*streams)
            return session
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to connect to stdio server '{command}': {e}")
            return None
    
    async def create_proxy_server(self, remote_app: ClientSession) -> Server:
        """Create a proxy server that forwards requests to a remote server.
        
        Args:
            remote_app: The remote server session
            
        Returns:
            A proxy server
        """
        return await create_proxy_server(remote_app)

server_manager = ServerManager() 