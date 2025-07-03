# LumnisAI Python SDK
[![PyPI version](https://badge.fury.io/py/lumnisai.svg)](https://badge.fury.io/py/lumnisai)
[![Python versions](https://img.shields.io/pypi/pyversions/lumnisai.svg)](https://pypi.org/project/lumnisai/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The official Python SDK for the [LumnisAI](https://lumnis.ai) multi-tenant AI platform. Build agent-oriented applications with support for multiple AI providers, user scoping, and conversation threads.

## Features

- **Multi-tenant Architecture**: Scope operations to tenants or individual users
- **User Management**: Full CRUD operations for user accounts with cascade deletion
- **Multiple AI Providers**: Support for OpenAI, Anthropic, Google, and Azure
- **Model Preferences**: Configure preferred models for different use cases (cheap, fast, smart, reasoning, vision)
- **Async & Sync APIs**: Both synchronous and asynchronous client interfaces
- **Conversation Threads**: Maintain conversation context across interactions
- **Structured Output**: Get responses in JSON format using Pydantic models
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

## Structured Output

Get AI responses in structured JSON format using Pydantic models. Perfect for extracting specific data, building APIs, or integrating with other systems.

### Basic Usage

```python
from pydantic import BaseModel, Field

# Define your output structure
class ProductInfo(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(description="Price in USD")
    in_stock: bool = Field(description="Whether item is in stock")

# Pass the model directly to invoke
response = client.invoke(
    "Tell me about the iPhone 15 Pro",
    response_format=ProductInfo,  # Pass Pydantic model class
    user_id="user-123"
)

# Access structured data
if response.structured_response:
    product = ProductInfo(**response.structured_response)
    print(f"{product.name}: ${product.price} ({'In Stock' if product.in_stock else 'Out of Stock'})")
```

### Complex Nested Structures

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class BusinessInfo(BaseModel):
    name: str
    category: str
    address: Address
    rating: Optional[float] = Field(None, ge=0, le=5)

response = await client.invoke(
    "Tell me about Tesla's headquarters",
    response_format=BusinessInfo,
    user_id="user-123"
)

if response.structured_response:
    business = BusinessInfo(**response.structured_response)
    print(f"{business.name} ({business.category})")
    print(f"Location: {business.address.city}, {business.address.country}")
```

### Response Format Instructions

Add specific instructions for how the structured output should be formatted:

```python
class WeatherData(BaseModel):
    temperature: str
    conditions: str
    humidity: str

response = client.invoke(
    "What's the weather in Paris?",
    response_format=WeatherData,
    response_format_instructions="Use Celsius for temperature and include the % symbol for humidity",
    user_id="user-123"
)
```

### Using JSON Schema Directly

You can also pass a JSON schema dictionary instead of a Pydantic model:

```python
response = client.invoke(
    "Analyze this product review",
    response_format={
        "type": "object",
        "properties": {
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
            "score": {"type": "number", "minimum": 0, "maximum": 10},
            "summary": {"type": "string"}
        },
        "required": ["sentiment", "score", "summary"]
    },
    user_id="user-123"
)
```

### Important Notes

- Both `output_text` and `structured_response` are returned in the response
- If the AI cannot generate valid structured output, `structured_response` may be `None`
- Always validate the structured response before using it
- The structured output feature works with both sync and async clients

## Model Preferences

Configure which LLM models to use for different scenarios. The SDK supports five model types:
- **CHEAP_MODEL**: Cost-effective for simple tasks
- **FAST_MODEL**: Low latency for quick responses
- **SMART_MODEL**: High quality for complex tasks
- **REASONING_MODEL**: Advanced reasoning and logic
- **VISION_MODEL**: Image understanding capabilities

### Configuring Model Preferences

```python
# First, configure API keys for providers
client.add_api_key(provider="OPENAI_API_KEY", api_key="sk-...")
client.add_api_key(provider="ANTHROPIC_API_KEY", api_key="sk-ant-...")

# Get current preferences
preferences = client.get_model_preferences()
for pref in preferences.preferences:
    print(f"{pref.model_type}: {pref.provider}:{pref.model_name}")

# Update preferences (bulk update)
client.update_model_preferences({
    "FAST_MODEL": {"provider": "openai", "model_name": "gpt-4o-mini"},
    "SMART_MODEL": {"provider": "anthropic", "model_name": "claude-3-7-sonnet-20250219"}
})
```

### Runtime Model Overrides

Override model selection for specific requests:

```python
# Create response with model override
response = client.responses.create(
    messages=[
        {"role": "user", "content": "Solve this complex problem"}
    ],
    model_overrides={
        "smart_model": "anthropic:claude-3-7-sonnet-20250219"
    }
)

# Override multiple models
response = client.responses.create(
    messages=[
        {"role": "user", "content": "Analyze this data"}
    ],
    model_overrides={
        "fast_model": "openai:gpt-4o-mini",
        "smart_model": "openai:gpt-4o",
        "reasoning_model": "openai:o1"
    }
)
```


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

## API Key Management (External API Keys)

Configure API keys for different AI providers to use their models:

### Supported Providers

All available API key providers:
- `OPENAI_API_KEY` - OpenAI models (GPT-4, etc.)
- `ANTHROPIC_API_KEY` - Anthropic Claude models
- `GOOGLE_API_KEY` - Google Gemini models
- `COHERE_API_KEY` - Cohere models
- `GROQ_API_KEY` - Groq cloud models
- `NVIDIA_API_KEY` - NVIDIA models
- `FIREWORKS_API_KEY` - Fireworks AI models
- `MISTRAL_API_KEY` - Mistral AI models
- `TOGETHER_API_KEY` - Together AI models
- `XAI_API_KEY` - xAI Grok models
- `PPLX_API_KEY` - Perplexity models
- `HUGGINGFACE_API_KEY` - Hugging Face models
- `DEEPSEEK_API_KEY` - DeepSeek models
- `IBM_API_KEY` - IBM models

### Managing API Keys

```python
# Add API keys
client.add_api_key(
    provider="OPENAI_API_KEY",
    api_key="sk-..."
)

client.add_api_key(
    provider="ANTHROPIC_API_KEY",
    api_key="sk-ant-..."
)

# List your API keys
keys = client.list_api_keys()
for key in keys:
    print(f"Provider: {key.provider}, Active: {key.is_active}")

# Delete an API key
client.delete_api_key("OPENAI_API_KEY")
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