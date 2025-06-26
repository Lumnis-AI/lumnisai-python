# LumnisAI Python SDK
[![PyPI version](https://badge.fury.io/py/lumnisai.svg)](https://badge.fury.io/py/lumnisai)
[![Python versions](https://img.shields.io/pypi/pyversions/lumnisai.svg)](https://pypi.org/project/lumnisai/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The official Python SDK for the [LumnisAI](https://lumnis.ai) multi-tenant AI platform. Build agent-oriented applications with support for multiple AI providers, user scoping, and conversation threads.

## Features

- **Multi-tenant Architecture**: Scope operations to tenants or individual users
- **User Management**: Full CRUD operations for user accounts with cascade deletion
- **Multiple AI Providers**: Support for OpenAI, Anthropic, Google, and Azure
- **Async & Sync APIs**: Both synchronous and asynchronous client interfaces
- **Conversation Threads**: Maintain conversation context across interactions
- **Progress Tracking**: Real-time progress updates with customizable callbacks
- **Type Safety**: Full type hints and Pydantic models for robust development
- **Error Handling**: Comprehensive exception hierarchy for different error scenarios

## Installation

```bash
pip install lumnisai
```

For development:

```bash
pip install lumnisai[dev]
```

## Quick Start

### Synchronous Client

```python
import lumnisai

# Initialize client (defaults to user scope)
client = lumnisai.Client()

# Simple AI interaction (requires user_id in user scope)
response = client.invoke(
    "Analyze the latest trends in machine learning",
    user_id="user-123"
)

print(response.output_text)
```

### Asynchronous Client

```python
import asyncio
import lumnisai

async def main():
    # Auto-initializes on first use (defaults to user scope)
    client = lumnisai.AsyncClient()
    response = await client.invoke(
        "Write a summary of quantum computing advances",
        user_id="user-123"
    )
    print(response.output_text)
    
    # Optional cleanup
    await client.close()

asyncio.run(main())
```

### Streaming Responses

```python
async def stream_example():
    # Auto-initializes on first use (defaults to user scope)
    client = lumnisai.AsyncClient()
    async for update in await client.invoke(
        "Conduct research on renewable energy trends",
        stream=True,
        user_id="user-123"
    ):
        print(f"Status: {update.status}")
        if update.status == "succeeded":
            print(f"Final result: {update.output_text}")
    
    # Optional cleanup
    await client.close()

asyncio.run(stream_example())
```

## Invoke API: Unified Interface

The `invoke()` method provides a unified interface for both blocking and streaming responses:

```python
# Blocking response (default)
response = await client.invoke("Hello world", user_id="user-123")
print(response.output_text)

# Streaming response  
async for update in await client.invoke("Hello world", stream=True, user_id="user-123"):
    print(f"Status: {update.status}")
    if update.status == "succeeded":
        print(update.output_text)
```

**Benefits:**
- **Single method** - No confusion between `invoke()` vs `invoke_stream()`
- **Clear parameter** - `stream=True` makes intent obvious
- **Type safety** - Proper type hints for both use cases
- **Backwards compatible** - `invoke_stream()` still works (deprecated)

## Configuration

### Environment Variables

Set up your environment with the following variables:

```bash
export LUMNISAI_API_KEY="your-api-key"
export LUMNISAI_BASE_URL="https://api.lumnis.ai"  # Optional
export LUMNISAI_TENANT_ID="your-tenant-id"       # Optional - auto-detected from API key
```

### Client Configuration

```python
client = lumnisai.Client(
    api_key="your-api-key",           # Required
    base_url="https://api.lumnis.ai", # Optional
    tenant_id="your-tenant-id",       # Optional - auto-detected from API key
    timeout=30.0,                     # Request timeout
    max_retries=3,                    # Retry attempts
    scope=Scope.USER                  # Default scope
)
```

**Note on Tenant ID**: The `tenant_id` parameter is optional because each API key is automatically scoped to a specific tenant. The SDK will extract the tenant context from your API key. You only need to explicitly provide `tenant_id` if you're using a special cross-tenant API key (rare).

## Understanding Scopes: Tenant vs User

LumnisAI operates in a **multi-tenant architecture** where each tenant can have multiple users. Understanding the difference between tenant and user scope is crucial for proper implementation.

**Important**: As of v0.2.0, the SDK defaults to **User scope** for better security and data isolation. This is a breaking change from earlier versions.

### Tenant Scope vs User Scope

| Aspect | **Tenant Scope** | **User Scope** |
|--------|------------------|----------------|
| **Purpose** | System-wide operations for the entire organization | User-specific operations and data isolation |
| **Data Access** | Access to all tenant data | Access only to user's own data |
| **Use Cases** | Admin dashboards, analytics, system operations | End-user applications, personal assistants |
| **Permissions** | Requires admin-level API keys | Standard user API keys |
| **user_id** | ❌ Must NOT be provided | ✅ Required |

### When to Use Each Scope

**Use Tenant Scope when:**
- Building admin dashboards or management interfaces
- Performing system-wide analytics or reporting
- Implementing tenant-level configuration changes
- Running background jobs that affect all users
- You have admin-level permissions

**Use User Scope when:**
- Building end-user applications (chatbots, assistants)
- Each user should only see their own data
- Implementing user-specific features
- Building customer-facing applications
- Following principle of least privilege

### User-Scoped Operations

```python
# Method 1: Pass user_id to each call
client = lumnisai.Client(scope=Scope.USER)
response = client.invoke("Hello", user_id="user-123")

# Method 2: Create user-scoped client
user_client = client.for_user("user-123")
response = user_client.invoke("Hello")

# Method 3: Temporary user context
with client.as_user("user-123") as user_client:
    response = user_client.invoke("Hello")

# Method 4: Explicit user scope with user_id
client = lumnisai.Client(scope=Scope.USER)
response = client.invoke("Hello", user_id="user-123")
```

### Tenant-Scoped Operations

```python
# Use tenant scope (requires proper permissions)
client = lumnisai.Client(scope=Scope.TENANT)

# System-wide queries (no user_id needed)
response = client.invoke("Generate monthly usage report")

# List all users' responses
all_responses = client.list_responses()

# Access tenant-level settings
tenant_info = client.tenant.get()
```

### Scope Validation and Error Handling

The SDK automatically validates scope usage and provides clear error messages:

```python
import lumnisai
from lumnisai.exceptions import MissingUserId, TenantScopeUserIdConflict

# ❌ This will raise MissingUserId
try:
    client = lumnisai.Client(scope=Scope.USER)
    response = client.invoke("Hello")  # Missing user_id
except MissingUserId:
    print("user_id is required when scope is USER")

# ❌ This will raise TenantScopeUserIdConflict  
try:
    client = lumnisai.Client(scope=Scope.TENANT)
    response = client.invoke("Hello", user_id="user-123")  # user_id not allowed
except TenantScopeUserIdConflict:
    print("user_id must not be provided when scope is TENANT")
```

## User Management

Manage users within your tenant with full CRUD operations:

```python
# Create a new user
user = await client.create_user(
    email="alice@example.com",
    first_name="Alice",
    last_name="Johnson"
)

# Get user by ID or email
user = await client.get_user("550e8400-e29b-41d4-a716-446655440000")
user = await client.get_user("alice@example.com")

# Update user information
updated_user = await client.update_user(
    user.id,
    first_name="Alicia",
    last_name="Smith"
)

# List all users with pagination
users_response = await client.list_users(page=1, page_size=20)
for user in users_response.users:
    print(f"{user.email} - {user.first_name} {user.last_name}")

# Delete user (cascades to all user data)
await client.delete_user(user.id)
```

### Synchronous User Management

```python
# Works the same with sync client
client = lumnisai.Client()

user = client.create_user(
    email="bob@example.com",
    first_name="Bob",
    last_name="Wilson"
)

users = client.list_users(page_size=50)
print(f"Total users: {users.pagination.total}")
```

## Conversation Threads

```python
# Create a new thread
thread = client.create_thread(
    user_id="user-123",
    title="Research Project"
)

# Continue conversation in thread
response1 = client.invoke(
    "What is machine learning?",
    user_id="user-123",
    thread_id=thread.thread_id
)

response2 = client.invoke(
    "Can you give me specific examples?",
    user_id="user-123", 
    thread_id=thread.thread_id
)

# List user's threads
threads = client.list_threads(user_id="user-123")
```

## Progress Tracking

Enable automatic progress printing with the `show_progress=True` parameter:

```python
# Automatic progress tracking (prints status and message updates)
response = await client.invoke(
    "Research the latest AI developments and write a report",
    user_id="user-123",
    show_progress=True  # Prints status changes and progress messages
)

# Output example:
# Status: in_progress
# PLANNING: Starting research on AI developments
# RESEARCHING: Gathering information from recent sources
# WRITING: Composing comprehensive report
# Status: succeeded
```

**Benefits:**
- **Simple** - Just add `show_progress=True`
- **Automatic** - No custom callbacks needed
- **Clean output** - Only prints when status or messages change
- **Works everywhere** - Both sync and async clients

## External API Keys

Manage API keys for different AI providers:

```python
# Add OpenAI API key for a user
client.external_api_keys.create(
    user_id="user-123",
    provider="openai",
    api_key="sk-...",
    mode="byo"  # Bring Your Own
)

# List user's API keys
keys = client.external_api_keys.list(user_id="user-123")

# Delete API key
client.external_api_keys.delete(key_id)
```

## Error Handling

```python
import lumnisai
from lumnisai.exceptions import (
    AuthenticationError,
    MissingUserId,
    TenantScopeUserIdConflict,
    ValidationError,
    RateLimitError,
    NotFoundError
)

try:
    response = client.invoke("Hello", user_id="user-123")
except AuthenticationError:
    print("Invalid API key")
except MissingUserId:
    print("User ID required for user-scoped operations")
except TenantScopeUserIdConflict:
    print("Cannot specify user_id with tenant scope")
except ValidationError as e:
    print(f"Invalid request: {e}")
except RateLimitError:
    print("Rate limit exceeded")
except NotFoundError:
    print("Resource not found")
```

## Advanced Usage

### Message Format

```python
# String format (converted to user message)
response = client.invoke("Hello world", user_id="user-123")

# Single message object
response = client.invoke(
    {"role": "user", "content": "Hello world"},
    user_id="user-123"
)

# Multiple messages (conversation history)
response = client.invoke([
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "Give me an example"}
], user_id="user-123")
```

### Response Management

```python
# Create response without waiting
response = await client.responses.create(
    messages=[{"role": "user", "content": "Hello"}],
    user_id="user-123"
)

# Poll for completion manually
final_response = await client.get_response(
    response.response_id,
    wait=30.0  # Wait up to 30 seconds
)

# Cancel a response
cancelled = await client.cancel_response(response.response_id)

# List user's responses
responses = client.list_responses(user_id="user-123", limit=10)
```

### Idempotency

```python
# Ensure exactly-once processing
response = client.invoke(
    "Important calculation",
    user_id="user-123",
    idempotency_key="calc-2024-001"
)

# Subsequent calls with same key return original response
duplicate = client.invoke(
    "Important calculation", 
    user_id="user-123",
    idempotency_key="calc-2024-001"  # Same key
)

assert response.response_id == duplicate.response_id
```

## Development

### Installation

```bash
git clone https://github.com/lumnisai/lumnisai-python.git
cd lumnisai-python

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and package in development mode
uv sync --dev
uv pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test files
python local_dev/test_01_auth.py
python local_dev/test_02_basic.py

# Run with coverage
pytest --cov=lumnisai
```

### Code Quality

```bash
# Formatting
black .
isort .

# Linting
ruff check .

# Type checking
mypy lumnisai/
```

## API Reference

### Core Classes

- **`Client`**: Synchronous client for LumnisAI API
- **`AsyncClient`**: Asynchronous client for LumnisAI API
- **`ResponseObject`**: Represents an AI response with progress tracking
- **`ThreadObject`**: Represents a conversation thread

### Enums

- **`Scope`**: `USER` or `TENANT` - defines operation scope
- **`ApiProvider`**: `OPENAI`, `ANTHROPIC`, `GOOGLE`, `AZURE`
- **`ApiKeyMode`**: `BRING_YOUR_OWN`, `USE_PLATFORM`

### Resources

- **`responses`**: Manage AI responses
- **`threads`**: Manage conversation threads  
- **`external_api_keys`**: Manage external provider API keys
- **`tenant`**: Tenant-level operations
- **`users`**: User management (CRUD operations)

## Support

- **Documentation**: [https://lumnisai.github.io/lumnisai-python](https://lumnisai.github.io/lumnisai-python)
- **Issues**: [https://github.com/lumnisai/lumnisai-python/issues](https://github.com/lumnisai/lumnisai-python/issues)
- **Email**: [dev@lumnis.ai](mailto:dev@lumnis.ai)

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up the development environment
- Running tests and code quality checks
- Submitting pull requests
- Code style guidelines

---

Built with ❤️ by the [LumnisAI](https://lumnis.ai) team