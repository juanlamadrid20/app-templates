#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Test Remote MCP Server - Databricks App"
echo "=========================================="
echo ""

# Step 1: Get Databricks profile name
read -p "Enter Databricks profile name (e.g., DEFAULT, dogfood): " profile_name
if [ -z "$profile_name" ]; then
    echo "❌ Error: Profile name is required"
    exit 1
fi

echo "✓ Using profile: $profile_name"
echo ""

# Step 2: Get Databricks App name
read -p "Enter Databricks App name (e.g., mcp-hello-world): " app_name
if [ -z "$app_name" ]; then
    echo "❌ Error: App name is required"
    exit 1
fi

echo "✓ Using app: $app_name"
echo ""

# Step 3: Get app information to extract URL
echo "Step 1: Getting app information..."
app_info=$(databricks apps get "$app_name" --profile "$profile_name" 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to get app information"
    echo "$app_info"
    exit 1
fi

# Extract app URL
if command -v jq &> /dev/null; then
    app_url=$(echo "$app_info" | jq -r '.url' 2>/dev/null)
    if [ "$app_url" = "null" ] || [ -z "$app_url" ]; then
        app_url=""
    fi
else
    app_url=$(echo "$app_info" | grep -E '^\s*"url":' | sed 's/.*"url":"\([^"]*\)".*/\1/')
fi

if [ -z "$app_url" ]; then
    echo "❌ Error: Could not extract app URL from app info"
    exit 1
fi

echo "✓ App URL: $app_url"
echo ""

# Step 4: Run the test (DatabricksMCPClient handles OAuth automatically)
echo "Step 2: Testing remote MCP server..."
echo "  OAuth authentication is handled automatically by DatabricksMCPClient."
echo ""

cd "$PROJECT_ROOT"

uv run python "$SCRIPT_DIR/query_remote.py" \
    --profile "$profile_name" \
    --app-url "$app_url"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Remote MCP Server Test Complete!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "✗ Remote MCP Server Test Failed"
    echo "=========================================="
    exit 1
fi

