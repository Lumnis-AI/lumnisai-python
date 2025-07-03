#!/usr/bin/env python3
"""Example script demonstrating Lumnis SDK integration functionality."""

import asyncio
import os
from lumnisai import AsyncClient


async def main():
    # Get API key from environment
    api_key = os.getenv("LUMNIS_API_KEY")
    if not api_key:
        print("Please set LUMNIS_API_KEY environment variable")
        return

    # Create client
    client = AsyncClient(api_key=api_key)
    
    async with client:
        print("Lumnis SDK Integration Example")
        print("=" * 50)
        
        user_id = "demo_user_123"
        
        # 0. Check and manage apps (NEW)
        print("\n0. Checking app availability...")
        try:
            # List all apps
            apps = await client.list_apps(include_available=True)
            print(f"   Enabled apps: {apps.enabled_apps}")
            print(f"   Available apps: {apps.available_apps[:5]}...")  # Show first 5
            
            # Check if GitHub is enabled
            github_status = await client.is_app_enabled("github")
            if not github_status.enabled:
                print("   GitHub is not enabled. Enabling it now...")
                result = await client.set_app_enabled("github", enabled=True)
                print(f"   ✓ {result.app_name} enabled at {result.updated_at}")
            else:
                print("   ✓ GitHub is already enabled")
        except Exception as e:
            print(f"   Error managing apps: {e}")
        
        # 1. Initiate a GitHub connection
        print("\n1. Initiating GitHub connection...")
        try:
            connection = await client.initiate_connection(
                user_id=user_id,
                app_name="github"
            )
            print(f"   Connection ID: {connection.connection_id}")
            print(f"   Redirect URL: {connection.redirect_url}")
            print(f"   Status: {connection.status}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 2. Check connection status
        print("\n2. Checking connection status...")
        try:
            status = await client.get_connection_status(
                user_id=user_id,
                app_name="github"
            )
            print(f"   App: {status.app_name}")
            print(f"   Status: {status.status}")
            if status.connected_at:
                print(f"   Connected at: {status.connected_at}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 3. List all connections
        print("\n3. Listing all user connections...")
        try:
            connections = await client.list_connections(user_id)
            print(f"   Total connections: {len(connections.connections)}")
            for conn in connections.connections:
                print(f"   - {conn.app_name}: {conn.status}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 4. Get available tools
        print("\n4. Getting available tools...")
        try:
            tools = await client.get_integration_tools(user_id=user_id)
            print(f"   Total tools: {tools.tool_count}")
            for tool in tools.tools[:5]:  # Show first 5 tools
                print(f"   - {tool.name}")
                print(f"     Description: {tool.description}")
                print(f"     From app: {tool.app_name}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n" + "=" * 50)
        print("Example completed!")


if __name__ == "__main__":
    asyncio.run(main())