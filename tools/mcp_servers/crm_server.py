"""
MCP server exposing the Client CRM (Google Sheet) as standardized tools.

Run standalone for testing:
    mcp dev tools/mcp_servers/crm_server.py

This wraps the same sheets_tool.py functions you already built and tested,
but exposes them through the MCP protocol instead of direct function calls.
"""

import sys
import os

# Make sure the project root is on the path so we can import tools.sheets_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from mcp.server.fastmcp import FastMCP
from tools.sheets_tool import get_client_record, update_client_status

mcp = FastMCP("crm-server")


@mcp.tool()
def lookup_client(email: str) -> dict:
    """Look up a client's CRM record by their email address.

    Returns their name, status, current monthly rate, and any notes.
    Use this before drafting a reply to an existing client so you can
    ground your response in real account data instead of guessing.
    """
    record = get_client_record(email)
    if record is None:
        return {"found": False, "message": f"No client found with email {email}"}
    return {"found": True, "record": record}


@mcp.tool()
def change_client_status(email: str, new_status: str) -> dict:
    """Update a client's status in the CRM (e.g. 'active', 'prospect', 'paused').

    Use this when a client's relationship status changes, such as converting
    a prospect to an active client after they agree to terms.
    """
    success = update_client_status(email, new_status)
    if not success:
        return {"success": False, "message": f"No client found with email {email}"}
    return {"success": True, "message": f"Updated {email} to status '{new_status}'"}


if __name__ == "__main__":
    mcp.run()