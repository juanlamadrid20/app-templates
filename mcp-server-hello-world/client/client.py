#!/usr/bin/env python3
"""
MCP client for the custom MCP server (local or remote Databricks App).

Local:  python client/client.py --app-url http://localhost:8000
Remote: python client/client.py --profile DEFAULT --app-url https://your-app.aws.databricksapps.com
"""

import argparse
import sys

from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient


def main():
    parser = argparse.ArgumentParser(description="List and call MCP server tools")
    parser.add_argument(
        "--profile",
        default=None,
        help="Databricks CLI profile (required for remote App; omit for local server)",
    )
    parser.add_argument(
        "--app-url",
        default="http://localhost:8000",
        help="Server base URL (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    mcp_url = f"{args.app_url.rstrip('/')}/mcp"

    try:
        if args.profile:
            workspace_client = WorkspaceClient(profile=args.profile)
            mcp_client = DatabricksMCPClient(
                server_url=mcp_url,
                workspace_client=workspace_client,
            )
        else:
            mcp_client = DatabricksMCPClient(server_url=mcp_url)

        print("Tools:")
        print("-" * 50)
        tools = mcp_client.list_tools()
        for tool in tools:
            print(f"  {tool.name}: {tool.description}")
        print("-" * 50)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
