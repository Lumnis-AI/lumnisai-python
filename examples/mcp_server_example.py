"""Example usage of MCP Server Management API."""
import asyncio
import os
from uuid import uuid4

import lumnisai


async def main():
    """Demonstrate MCP Server Management API functionality."""
    # Initialize client with API key from environment
    client = lumnisai.AsyncClient(
        api_key=os.environ.get("LUMNISAI_API_KEY"),
        tenant_id=os.environ.get("LUMNISAI_TENANT_ID"),
    )
    
    async with client:
        print("=== MCP Server Management API Demo ===\n")
        
        # 1. Create a tenant-scoped MCP server for GitHub integration
        print("1. Creating GitHub MCP server (tenant-scoped)...")
        github_server = await client.create_mcp_server(
            name=f"github-demo-{uuid4().hex[:8]}",
            transport="streamable_http",
            scope="tenant",
            description="GitHub API integration for the entire tenant",
            url="https://api.github.com/mcp/v1",
            headers={
                "Authorization": "Bearer ghp_your_github_token",
                "X-API-Version": "2022-11-28",
            },
        )
        print(f"✓ Created server: {github_server.name} (ID: {github_server.id})")
        
        # 2. Create a user-scoped MCP server for local Python tools
        print("\n2. Creating local Python tools server (user-scoped)...")
        user_email = "developer@example.com"  # Replace with actual user email
        python_server = await client.create_mcp_server(
            name=f"python-tools-{uuid4().hex[:8]}",
            transport="stdio",
            scope="user",
            user_identifier=user_email,
            description="Local Python tools for data processing",
            command="python",
            args=["-m", "mcp_server", "--mode", "tools"],
            env={
                "PYTHONPATH": "/usr/local/lib/python3.11/site-packages",
                "DEBUG": "true",
            },
        )
        print(f"✓ Created server: {python_server.name} for user {user_email}")
        
        # 3. List all MCP servers
        print("\n3. Listing all MCP servers...")
        all_servers = await client.list_mcp_servers()
        print(f"✓ Found {all_servers.total} servers:")
        for server in all_servers.servers:
            print(f"  - {server.name} ({server.scope}, {server.transport})")
        
        # 4. Get details of a specific server
        print(f"\n4. Getting details of {github_server.name}...")
        server_details = await client.get_mcp_server(github_server.id)
        print(f"  Name: {server_details.name}")
        print(f"  Transport: {server_details.transport}")
        print(f"  URL: {server_details.url}")
        print(f"  Active: {server_details.is_active}")
        print(f"  Created: {server_details.created_at}")
        
        # 5. Update server configuration
        print(f"\n5. Updating {python_server.name} configuration...")
        updated_server = await client.update_mcp_server(
            python_server.id,
            description="Enhanced Python tools with ML capabilities",
            env={
                "PYTHONPATH": "/usr/local/lib/python3.11/site-packages",
                "DEBUG": "false",
                "ENABLE_ML": "true",
            },
            is_active=True,
        )
        print(f"✓ Updated server description and environment")
        
        # 6. List tools (simulated - would work with actual MCP server)
        print(f"\n6. Listing tools from {github_server.name}...")
        try:
            tools = await client.list_mcp_server_tools(github_server.id)
            print(f"✓ Server provides {tools.total} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
        except Exception as e:
            print(f"  (Tools listing would work with a real MCP server)")
            print(f"  Error: {type(e).__name__}")
        
        # 7. Test server connection (simulated)
        print(f"\n7. Testing connection to {python_server.name}...")
        try:
            test_result = await client.test_mcp_server(python_server.id)
            if test_result.success:
                print(f"✓ Connection successful! Found {test_result.tool_count} tools")
            else:
                print(f"✗ Connection failed: {test_result.error_details}")
        except Exception as e:
            print(f"  (Connection test would work with a real MCP server)")
            print(f"  Error: {type(e).__name__}")
        
        # 8. Filter servers by scope
        print("\n8. Filtering servers by scope...")
        tenant_servers = await client.list_mcp_servers(scope="tenant")
        user_servers = await client.list_mcp_servers(
            scope="user", 
            user_identifier=user_email
        )
        print(f"✓ Tenant-scoped servers: {tenant_servers.total}")
        print(f"✓ User-scoped servers for {user_email}: {user_servers.total}")
        
        # 9. Clean up - delete the demo servers
        print("\n9. Cleaning up demo servers...")
        await client.delete_mcp_server(github_server.id)
        print(f"✓ Deleted {github_server.name}")
        await client.delete_mcp_server(python_server.id)
        print(f"✓ Deleted {python_server.name}")
        
        print("\n=== Demo completed successfully! ===")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())