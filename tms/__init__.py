"""Read-only Test Management System (TMS) integration.

The package is intentionally split into small, replaceable boundaries:

* ``models`` - typed API/test-case models shared by every provider.
* ``provider`` - the protocol a real Zephyr/Jira adapter can implement.
* ``client`` - the HTTP implementation of that protocol.
* ``mock_api`` / ``mock_data`` - a deterministic local REST API.
* ``mcp_server`` - an MCP stdio bridge exposing search/get tools.
"""

__version__ = "0.1.0"
