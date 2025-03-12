"""MCP Proxy.

A MCP server that proxies requests to a remote MCP server.
"""

__version__ = "0.5.0"

# Make sure src/mcp_servers is in the Python path
import sys
import os
from pathlib import Path

# Get the parent directory of the mcp_proxy package
src_dir = Path(__file__).parent.parent.absolute()

# Add the src directory to the Python path if it's not already there
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now we can import from mcp_servers
try:
    import mcp_servers
except ImportError:
    # When installed as a package, the mcp_servers module is inside mcp_proxy
    try:
        import mcp_proxy.mcp_servers as mcp_servers
    except ImportError:
        # If mcp_servers is not available, print a warning
        import logging
        logging.warning("mcp_servers module not found. Local MCP servers will not be available.")
