"""
Tools module for the MCP server.

This module defines all the tools (functions) that the MCP server exposes to clients.
Tools are the core functionality of an MCP server - they are callable functions that
AI assistants and other clients can invoke to perform specific actions.

Each tool should:
- Have a clear, descriptive name
- Include comprehensive docstrings (used by AI to understand when to call the tool)
- Return structured data (typically dict or list)
- Handle errors gracefully
"""

from server import utils


def load_tools(mcp_server):
    """
    Register all MCP tools with the server.

    This function is called during server initialization to register all available
    tools with the MCP server instance. Tools are registered using the @mcp_server.tool
    decorator, which makes them available to clients via the MCP protocol.

    Args:
        mcp_server: The FastMCP server instance to register tools with. This is the
                   main server object that handles tool registration and routing.

    Example:
        To add a new tool, define it within this function using the decorator:

        @mcp_server.tool
        def my_new_tool(param: str) -> dict:
            '''Description of what the tool does.'''
            return {"result": f"Processed {param}"}
    """

    @mcp_server.tool
    def health() -> dict:
        """
        Check the health of the MCP server and Databricks connection.

        This is a simple diagnostic tool that confirms the server is running properly.
        It's useful for:
        - Monitoring and health checks
        - Testing the MCP connection
        - Verifying the server is responsive

        Returns:
            dict: A dictionary containing:
                - status (str): The health status ("healthy" if operational)
                - message (str): A human-readable status message

        Example response:
            {
                "status": "healthy",
                "message": "Custom MCP Server is healthy and connected to Databricks Apps."
            }
        """
        return {
            "status": "healthy",
            "message": "Custom MCP Server is healthy and connected to Databricks Apps.",
        }

    @mcp_server.tool
    def get_current_user() -> dict:
        """
        Get information about the current authenticated user.

        This tool retrieves details about the user who is currently authenticated
        with the MCP server. When deployed as a Databricks App, this returns
        information about the end user making the request. When running locally,
        it returns information about the developer's Databricks identity.

        Useful for:
        - Personalizing responses based on the user
        - Authorization checks
        - Audit logging
        - User-specific operations

        Returns:
            dict: A dictionary containing:
                - display_name (str): The user's display name
                - user_name (str): The user's username/email
                - active (bool): Whether the user account is active

        Example response:
            {
                "display_name": "John Doe",
                "user_name": "john.doe@example.com",
                "active": true
            }

        Raises:
            Returns error dict if authentication fails or user info cannot be retrieved.
        """
        try:
            w = utils.get_user_authenticated_workspace_client()
            user = w.current_user.me()
            return {
                "display_name": user.display_name,
                "user_name": user.user_name,
                "active": user.active,
            }
        except Exception as e:
            return {"error": str(e), "message": "Failed to retrieve user information"}

    @mcp_server.tool
    def list_clusters(limit: int = 25) -> dict:
        """
        List Databricks clusters in the workspace.

        Returns a summary of clusters (all-purpose, job, etc.) with their name, id,
        state, and runtime. Uses app-level (service principal) authentication, so
        it reflects what the app can see in the workspace, not just the current user's
        clusters.

        Useful for:
        - Discovering available compute for running notebooks or jobs
        - Checking cluster state (running, terminated, etc.) before running workloads
        - Helping users choose or start a cluster

        Args:
            limit: Maximum number of clusters to return (default 25). Use to avoid
                   large responses in workspaces with many clusters.

        Returns:
            dict: A dictionary containing:
                - clusters (list): List of cluster summaries, each with:
                    - cluster_id (str): Unique cluster identifier
                    - name (str): Cluster name
                    - state (str): Current state (e.g. RUNNING, TERMINATED)
                    - spark_version (str): DBR version
                - count (int): Number of clusters returned

        Example response:
            {
                "clusters": [
                    {
                        "cluster_id": "1234-567890-abc123",
                        "name": "my-cluster",
                        "state": "RUNNING",
                        "spark_version": "14.3.x-scala2.12"
                    }
                ],
                "count": 1
            }
        """
        try:
            w = utils.get_workspace_client()
            clusters = []
            for i, c in enumerate(w.clusters.list()):
                if i >= limit:
                    break
                clusters.append({
                    "cluster_id": c.cluster_id,
                    "name": c.cluster_name or "(unnamed)",
                    "state": getattr(c.state, "value", str(c.state)) if c.state else "UNKNOWN",
                    "spark_version": c.spark_version or "—",
                })
            return {"clusters": clusters, "count": len(clusters)}
        except Exception as e:
            return {"error": str(e), "message": "Failed to list clusters", "clusters": [], "count": 0}
