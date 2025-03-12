"""Base MCP server interface and registry.

This module defines the base interface for all MCP servers to implement and provides
a registry to manage available servers.
"""

import abc
import typing as t
from dataclasses import dataclass
from enum import Enum, auto

from mcp import server, types


class ServerType(Enum):
    """Type of server implementation."""
    
    STDIO = auto()
    SSE = auto()


@dataclass
class ServerInfo:
    """Information about a registered server."""
    
    name: str
    description: str
    server_type: ServerType
    command: str
    args: list[str] = None
    env: dict[str, str] = None
    
    def __post_init__(self):
        """Initialize default values for args and env."""
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}


class MCPServerRegistry:
    """Registry of available MCP servers."""
    
    _servers: dict[str, ServerInfo] = {}
    
    @classmethod
    def register(cls, server_info: ServerInfo) -> None:
        """Register a server with the registry.
        
        Args:
            server_info: Information about the server to register
        """
        cls._servers[server_info.name] = server_info
    
    @classmethod
    def get_server(cls, name: str) -> t.Optional[ServerInfo]:
        """Get a server by name.
        
        Args:
            name: Name of the server to get
            
        Returns:
            Server information if found, None otherwise
        """
        return cls._servers.get(name)
    
    @classmethod
    def list_servers(cls) -> list[ServerInfo]:
        """List all registered servers.
        
        Returns:
            List of all registered servers
        """
        return list(cls._servers.values())


class BaseMCPServer(abc.ABC):
    """Base class for all MCP servers."""
    
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the server."""
        pass
    
    @abc.abstractmethod
    async def create_server(self) -> server.Server:
        """Create an MCP server instance.
        
        Returns:
            An MCP server instance
        """
        pass
    
    @property
    @abc.abstractmethod
    def server_info(self) -> ServerInfo:
        """Get information about this server.
        
        Returns:
            Server information
        """
        pass 