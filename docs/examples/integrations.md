# Lumnis SDK Integration Examples

This guide demonstrates how to use the Lumnis SDK to manage integrations with external services like GitHub, Slack, and other platforms.

## Overview

The Lumnis SDK provides a comprehensive set of endpoints for managing OAuth connections and accessing tools from integrated apps. All integration methods are available directly on the client instance.

**New in this version**: App management endpoints allow tenants to control which apps are available for their users.

## Prerequisites

```python
import lumnisai
from lumnisai import AsyncClient, Client

# For async operations
client = AsyncClient(api_key="your-api-key")

# For sync operations
client = Client(api_key="your-api-key")
```

## App Management (New)

Before users can connect to external services, you need to ensure the apps are enabled for your tenant.

### Listing Available Apps

```python
async def check_available_apps():
    # List only enabled apps
    enabled = await client.list_apps()
    print(f"Enabled apps: {enabled.enabled_apps}")
    print(f"Total enabled: {enabled.total_enabled}")
    
    # List both enabled and available apps
    all_apps = await client.list_apps(include_available=True)
    print(f"Available apps: {all_apps.available_apps}")
    print(f"Total available: {all_apps.total_available}")
    
    return all_apps

# Run the async function
import asyncio
apps = asyncio.run(check_available_apps())
```

### Checking if an App is Enabled

```python
async def check_app_status(app_name: str):
    status = await client.is_app_enabled(app_name)
    print(f"{status.app_name} is {'enabled' if status.enabled else 'disabled'}")
    return status.enabled

# Check if GitHub is enabled
is_enabled = asyncio.run(check_app_status("github"))
```

### Enabling/Disabling Apps

```python
async def manage_app(app_name: str, enable: bool):
    result = await client.set_app_enabled(
        app_name,
        enabled=enable
    )
    
    action = "enabled" if result.enabled else "disabled"
    print(f"{result.app_name} has been {action}")
    print(f"Updated at: {result.updated_at}")
    
    return result

# Enable Slack for the tenant
asyncio.run(manage_app("slack", enable=True))

# Disable Jira for the tenant
asyncio.run(manage_app("jira", enable=False))
```

### Complete App Setup Flow

```python
async def setup_apps_for_tenant():
    """Ensure required apps are enabled for the tenant."""
    required_apps = ["github", "slack", "gmail"]
    
    async with client:
        # Check current status
        current = await client.list_apps(include_available=True)
        print(f"Currently enabled: {current.enabled_apps}")
        
        # Enable required apps that aren't already enabled
        for app in required_apps:
            if app.upper() not in current.enabled_apps:
                print(f"\nEnabling {app}...")
                result = await client.set_app_enabled(app, enabled=True)
                print(f"✓ {result.app_name} enabled")
            else:
                print(f"✓ {app.upper()} already enabled")
        
        # Verify final state
        final = await client.list_apps()
        print(f"\nFinal enabled apps: {final.enabled_apps}")

asyncio.run(setup_apps_for_tenant())
```

## Initiating OAuth Connections

### Async Example

```python
async def connect_to_github():
    # Initiate GitHub connection
    connection = await client.initiate_connection(
        user_id="user123",
        app_name="github",  # Will be uppercased automatically
        redirect_url="https://yourapp.com/oauth/callback"  # Optional custom redirect
    )
    
    print(f"Connection ID: {connection.connection_id}")
    print(f"Redirect user to: {connection.redirect_url}")
    
    # The user should be redirected to the OAuth URL
    # After authorization, they'll be redirected back to your app
    return connection

# Run the async function
import asyncio
connection = asyncio.run(connect_to_github())
```

### Sync Example

```python
# Initiate Slack connection
connection = client.initiate_connection(
    user_id="user123",
    app_name="slack"
)

print(f"OAuth URL: {connection.redirect_url}")
```

## Checking Connection Status

### Async Example

```python
async def check_github_status():
    status = await client.get_connection_status(
        user_id="user123",
        app_name="github"
    )
    
    print(f"App: {status.app_name}")
    print(f"Status: {status.status}")  # pending, active, failed, or expired
    print(f"Connected at: {status.connected_at}")
    
    if status.error_message:
        print(f"Error: {status.error_message}")
    
    return status

status = asyncio.run(check_github_status())
```

## Listing All User Connections

### Async Example

```python
async def list_user_connections():
    # List all connections
    all_connections = await client.list_connections("user123")
    
    for conn in all_connections.connections:
        print(f"{conn.app_name}: {conn.status}")
    
    # Filter specific apps
    filtered = await client.list_connections(
        "user123",
        app_filter="GITHUB,SLACK"
    )
    
    return all_connections

connections = asyncio.run(list_user_connections())
```

## Getting Available Tools

Once a user has active connections, you can retrieve the tools available from those apps:

### Async Example

```python
async def get_user_tools():
    # Get all tools from active connections
    tools_response = await client.get_integration_tools(user_id="user123")
    
    print(f"Total tools available: {tools_response.tool_count}")
    
    for tool in tools_response.tools:
        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"From app: {tool.app_name}")
        print(f"Parameters: {tool.parameters}")
    
    # Filter tools by specific apps
    github_tools = await client.get_integration_tools(
        user_id="user123",
        app_filter=["github"]
    )
    
    return tools_response

tools = asyncio.run(get_user_tools())
```

### Working with Tool Parameters

```python
# Example of a GitHub tool
tool = tools.tools[0]  # e.g., GITHUB_CREATE_ISSUE

# Access parameter schema
if tool.parameters.type == "object" and tool.parameters.properties:
    print("Required parameters:")
    for param_name, param_info in tool.parameters.properties.items():
        required = param_name in (tool.parameters.required or [])
        print(f"  - {param_name}: {param_info['type']} {'(required)' if required else '(optional)'}")
        if 'description' in param_info:
            print(f"    Description: {param_info['description']}")
```

## Complete Integration Flow Example

Here's a complete example showing the full OAuth flow with app management:

```python
import asyncio
from lumnisai import AsyncClient

async def complete_integration_flow():
    client = AsyncClient(api_key="your-api-key")
    user_id = "user123"
    app_name = "github"
    
    async with client:
        # Step 1: Ensure app is enabled for tenant
        print("Step 1: Checking if GitHub is enabled...")
        app_status = await client.is_app_enabled(app_name)
        
        if not app_status.enabled:
            print(f"Enabling {app_name} for tenant...")
            await client.set_app_enabled(app_name, enabled=True)
            print("✓ GitHub enabled")
        else:
            print("✓ GitHub already enabled")
        
        # Step 2: Check if user already connected
        try:
            existing_status = await client.get_connection_status(
                user_id=user_id,
                app_name=app_name
            )
            if existing_status.status == "active":
                print(f"\n✓ User already connected to {app_name}")
                # Skip to step 5
        except Exception:
            # User not connected yet
            pass
        
        # Step 3: Initiate connection
        print("\nStep 3: Initiating GitHub connection...")
        connection = await client.initiate_connection(
            user_id=user_id,
            app_name=app_name
        )
        print(f"Redirect URL: {connection.redirect_url}")
        print(f"Connection ID: {connection.connection_id}")
        
        # Step 4: User completes OAuth (happens externally)
        print("\nStep 4: Waiting for user to complete OAuth...")
        # In a real app, you'd handle the OAuth callback here
        
        # Step 5: Check connection status
        print("\nStep 5: Checking connection status...")
        await asyncio.sleep(2)  # Simulate wait
        
        status = await client.get_connection_status(
            user_id=user_id,
            app_name=app_name
        )
        print(f"Connection status: {status.status}")
        
        # Step 6: Get available tools (if connected)
        if status.status == "active":
            print("\nStep 6: Getting available tools...")
            tools = await client.get_integration_tools(user_id=user_id)
            print(f"Available tools: {tools.tool_count}")
            
            for tool in tools.tools[:3]:  # Show first 3 tools
                print(f"  - {tool.name}: {tool.description}")
        
        # Step 7: List all connections
        print("\nStep 7: Listing all connections...")
        all_connections = await client.list_connections(user_id)
        for conn in all_connections.connections:
            print(f"  - {conn.app_name}: {conn.status}")

# Run the complete flow
asyncio.run(complete_integration_flow())
```

## Error Handling

```python
from lumnisai.exceptions import LumnisError

async def safe_connection_initiation():
    try:
        connection = await client.initiate_connection(
            user_id="user123",
            app_name="github"
        )
        return connection
    except LumnisError as e:
        print(f"Integration error: {e}")
        # Handle specific error cases
        if "401" in str(e):
            print("Authentication failed - check your API key")
        elif "404" in str(e):
            print("User not found")
        else:
            print(f"Unexpected error: {e}")
        return None
```

## Available Apps

The following apps are enabled by default for all tenants:

- **GITHUB** - GitHub integration for repository management
- **SLACK** - Slack integration for messaging
- **GMAIL** - Gmail integration for email
- **JIRA** - Jira integration for issue tracking
- **NOTION** - Notion integration for documentation

## Best Practices

1. **Check app availability first** - Before attempting to connect users, ensure the app is enabled for your tenant.

2. **Always use uppercase app names** - The SDK automatically uppercases app names, but using uppercase in your code makes it clearer.

3. **Store connection IDs** - Save the `connection_id` returned from `initiate_connection` for tracking OAuth completion.

4. **Poll for status updates** - After initiating a connection, periodically check the status until it becomes "active" or "failed".

5. **Handle errors gracefully** - OAuth flows can fail for various reasons (user cancellation, invalid credentials, etc.).

6. **Cache tool information** - Tool schemas don't change frequently, so consider caching the results of `get_tools`.

7. **Use app filters** - When listing connections or tools, use filters to reduce response size and improve performance.

8. **Tenant-wide impact** - Remember that enabling/disabling apps affects all users in your tenant.

## Notes

- The `auth_mode` and `connection_params` fields in `initiate_connection` are reserved for future non-OAuth authentication methods.
- The `/v1/integrations/non-oauth/required-fields/{app_name}` endpoint is planned for future API key-based integrations.
- All integration data is isolated per tenant based on the API key used.