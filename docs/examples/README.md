# LumnisAI Python SDK Examples

This directory contains comprehensive examples demonstrating various features of the LumnisAI Python SDK. All examples use **tenant scope** (the default), making them simple to run and understand.

## Quick Setup

Before running any examples, make sure you have:

1. **Installed the SDK**:
   ```bash
   pip install lumnisai
   ```

2. **Set your API key**:
   ```bash
   export LUMNISAI_API_KEY="your-api-key"
   ```

## Examples Overview

### Basic Usage

- **[`basic_sync.py`](basic_sync.py)** - Simple synchronous client usage
- **[`basic_async.py`](basic_async.py)** - Simple asynchronous client usage  
- **[`api_usage.py`](api_usage.py)** - Basic API interaction example

### Advanced Features

- **[`streaming_example.py`](streaming_example.py)** - Real-time streaming responses with progress updates
- **[`progress_example.py`](progress_example.py)** - Simple progress tracking with progress=True
- **[`conversation_messages.py`](conversation_messages.py)** - Different message formats and conversation patterns
- **[`thread_management.py`](thread_management.py)** - Creating and managing conversation threads
- **[`response_management.py`](response_management.py)** - Advanced response handling, cancellation, and idempotency
- **[`error_handling.py`](error_handling.py)** - Comprehensive error handling patterns
- **[`user_management.py`](user_management.py)** - Full user CRUD operations and lifecycle management

## Running Examples

Each example is a standalone Python script. Run them directly:

```bash
# Basic examples
python docs/examples/basic_sync.py
python docs/examples/basic_async.py

# Advanced examples
python docs/examples/streaming_example.py
python docs/examples/progress_example.py
python docs/examples/conversation_messages.py
python docs/examples/thread_management.py
python docs/examples/response_management.py
python docs/examples/error_handling.py
python docs/examples/user_management.py
```

## Example Categories

### 🚀 Getting Started
Start with these if you're new to the SDK:
- `basic_sync.py` - Simplest possible usage
- `basic_async.py` - Async version of basic usage
- `api_usage.py` - Standard API interaction

### 📡 Real-time Features  
Learn about streaming and progress tracking:
- `streaming_example.py` - Stream responses as they're generated
- `progress_example.py` - Simple progress tracking with progress=True

### 💬 Conversations
Build conversational applications:
- `conversation_messages.py` - Message formatting and conversation history
- `thread_management.py` - Persistent conversation threads

### 🔧 Advanced Usage
Power user features:
- `response_management.py` - Response lifecycle, cancellation, idempotency
- `error_handling.py` - Robust error handling patterns
- `user_management.py` - User CRUD operations, bulk imports, lifecycle management

## Key Features Demonstrated

- **Tenant Scope (Default)**: All examples use the default tenant scope for simplicity
- **User Management**: Full CRUD operations for user accounts
- **Async/Await Patterns**: Modern Python async programming
- **Error Handling**: Comprehensive exception handling
- **Progress Tracking**: Real-time progress updates and callbacks
- **Conversation Management**: Threads and message history
- **Response Management**: Creation, monitoring, and cancellation
- **Streaming**: Real-time response streaming

## Environment Setup

### Required Environment Variables

```bash
export LUMNISAI_API_KEY="your-api-key"
```

### Optional Environment Variables

```bash
export LUMNISAI_BASE_URL="https://api.lumnis.ai"  # Custom base URL
export LUMNISAI_TENANT_ID="your-tenant-id"       # Usually auto-detected
```

## Common Patterns

### Basic Pattern (Sync)
```python
import lumnisai

with lumnisai.Client() as client:
    response = client.invoke("Your prompt here")
    print(response.output_text)
```

### Basic Pattern (Async)
```python
import asyncio
import lumnisai

async def main():
    # Auto-initializes on first use - no context manager needed
    client = lumnisai.AsyncClient()
    response = await client.invoke("Your prompt here")
    print(response.output_text)
    
    # Optional cleanup for advanced users
    await client.close()

asyncio.run(main())
```

### Advanced Pattern (Async with Context Manager)
```python
import asyncio
import lumnisai

async def main():
    # Still supported for advanced users who want explicit lifecycle
    async with lumnisai.AsyncClient() as client:
        response = await client.invoke("Your prompt here")
        print(response.output_text)

asyncio.run(main())
```

### Streaming Pattern
```python
async def stream_example():
    # Auto-initializes on first use
    client = lumnisai.AsyncClient()
    async for update in await client.invoke("Your prompt here", stream=True):
        print(f"Status: {update.status}")
        if update.status == "succeeded":
            print(update.output_text)
    
    # Optional cleanup
    await client.close()
```

## Troubleshooting

### Common Issues

1. **Missing API Key**: Set `LUMNISAI_API_KEY` environment variable
2. **Import Errors**: Install the SDK with `pip install lumnisai`
3. **Authentication**: Verify your API key is valid
4. **Network Issues**: Check internet connectivity and firewall settings

### Getting Help

- Check the main [README](../../README.md) for detailed documentation
- Review error messages - the SDK provides clear error descriptions
- Look at similar examples for patterns

## Contributing

When adding new examples:
- Use tenant scope (default) for simplicity
- Include comprehensive comments
- Add error handling
- Update this README with example descriptions
- Test examples before submitting