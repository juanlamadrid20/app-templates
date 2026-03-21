#!/usr/bin/env python3
"""
Test remote MCP server deployed as a Databricks App.

This script tests the remote MCP server with OAuth authentication via the
Databricks SDK profile. The DatabricksMCPClient handles the OAuth flow
automatically using DatabricksOAuthClientProvider.

Custom MCP servers on Databricks Apps require OAuth — PAT auth is not supported.

Usage:
    python query_remote.py --profile <profile> --app-url <app-url>

Example:
    python query_remote.py \\
        --profile DEFAULT \\
        --app-url https://my-app-123456.aws.databricksapps.com
"""

import argparse
import sys

from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient


def main():
    parser = argparse.ArgumentParser(
        description="Test remote MCP server deployed as Databricks App"
    )

    parser.add_argument(
        "--profile", required=True, help="Databricks CLI profile name (must use OAuth auth)"
    )

    parser.add_argument(
        "--app-url", required=True, help="Databricks App URL (without /mcp suffix)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Testing Remote MCP Server - Databricks App")
    print("=" * 70)

    try:
        print(f"\nStep 1: Creating WorkspaceClient with profile '{args.profile}'...")
        workspace_client = WorkspaceClient(profile=args.profile)
        print(f"✓ WorkspaceClient created (host: {workspace_client.config.host})")
        print(f"  Auth type: {workspace_client.config.auth_type}")
        print()

        mcp_url = f"{args.app_url}/mcp"
        print(f"Step 2: Connecting to MCP server at {mcp_url}...")
        print("  (DatabricksOAuthClientProvider handles OAuth automatically)")
        mcp_client = DatabricksMCPClient(server_url=mcp_url, workspace_client=workspace_client)
        print("✓ MCP client created")
        print()

        print("Step 3: Listing available MCP tools...")
        print("-" * 70)
        tools = mcp_client.list_tools()
        print(f"✓ Found {len(tools) if isinstance(tools, list) else 'N/A'} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        print("-" * 70)
        print()

        for tool in tools:
            print(f"Step 4: Calling tool '{tool.name}'...")
            print("-" * 70)
            result = mcp_client.call_tool(tool.name)
            print(result)
            print("-" * 70)
            print()

        print("=" * 70)
        print("✓ All Tests Passed!")
        print("=" * 70)

    except Exception as e:
        print()
        print("=" * 70)
        print(f"✗ Error: {e}")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
