#!/usr/bin/env python3
"""
Error handling examples using tenant scope (default).
Shows how to handle different types of errors gracefully.
"""

import asyncio
import lumnisai
from lumnisai.exceptions import (
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
    TransportError,
    LumnisAIError
)

async def authentication_error_example():
    """Demonstrate authentication error handling."""
    print("=== Authentication Error Example ===")
    try:
        # This will fail with invalid API key
        client = lumnisai.AsyncClient(api_key="invalid-key")
        response = await client.invoke("Test message")
        await client.close()
    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
        print(f"Error code: {e.code}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")

async def validation_error_example():
    """Demonstrate validation error handling."""
    print("\n=== Validation Error Example ===")
    try:
        client = lumnisai.AsyncClient()
        # This might fail with validation error
        response = await client.responses.create(
            messages=[]  # Empty messages should cause validation error
        )
        await client.close()
    except ValidationError as e:
        print(f"Validation failed: {e.message}")
        print(f"Error code: {e.code}")
        if e.detail:
            print(f"Details: {e.detail}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")

async def not_found_error_example():
    """Demonstrate not found error handling."""
    print("\n=== Not Found Error Example ===")
    try:
        client = lumnisai.AsyncClient()
        # Try to get a non-existent response
        response = await client.get_response("00000000-0000-0000-0000-000000000000")
        await client.close()
    except NotFoundError as e:
        print(f"Resource not found: {e.message}")
        print(f"Error code: {e.code}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")

async def rate_limit_error_example():
    """Demonstrate rate limit error handling."""
    print("\n=== Rate Limit Error Example ===")
    # Note: This is hard to demo without actually hitting rate limits
    # So we'll show the handling pattern
    
    try:
        client = lumnisai.AsyncClient()
        # Make many requests quickly (this might trigger rate limiting)
        for i in range(10):
            response = await client.invoke(f"Quick test {i}")
            print(f"Request {i} completed")
        await client.close()
    except RateLimitError as e:
        print(f"Rate limit exceeded: {e.message}")
        print(f"Error code: {e.code}")
        if hasattr(e, 'retry_after') and e.retry_after:
            print(f"Retry after: {e.retry_after} seconds")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")

async def transport_error_example():
    """Demonstrate transport error handling."""
    print("\n=== Transport Error Example ===")
    try:
        # Use an invalid base URL to trigger transport error
        client = lumnisai.AsyncClient(base_url="https://invalid-url-that-does-not-exist.com")
        response = await client.invoke("Test message")
        await client.close()
    except TransportError as e:
        print(f"Transport error: {e.message}")
        print(f"Error code: {e.code}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")

async def comprehensive_error_handling():
    """Demonstrate comprehensive error handling."""
    print("\n=== Comprehensive Error Handling ===")
    
    client = lumnisai.AsyncClient()
    try:
        response = await client.invoke(
            "Write a comprehensive analysis of climate change impacts"
        )
        print("Success! Response received.")
        print(f"Response length: {len(response.output_text)} characters")
        
    except AuthenticationError:
        print("❌ Authentication failed - check your API key")
    except ValidationError as e:
        print(f"❌ Request validation failed: {e.message}")
    except RateLimitError as e:
        print(f"⏰ Rate limit exceeded - please wait and retry")
        if hasattr(e, 'retry_after') and e.retry_after:
            print(f"   Retry after: {e.retry_after} seconds")
    except NotFoundError:
        print("❌ Requested resource not found")
    except TransportError:
        print("🌐 Network or connectivity issue")
    except LumnisAIError as e:
        print(f"❌ LumnisAI API error: {e.message}")
        print(f"   Error code: {e.code}")
    except Exception as e:
        print(f"💥 Unexpected error: {type(e).__name__}: {e}")
    finally:
        await client.close()

async def main():
    await authentication_error_example()
    await validation_error_example() 
    await not_found_error_example()
    await rate_limit_error_example()
    await transport_error_example()
    await comprehensive_error_handling()

if __name__ == "__main__":
    asyncio.run(main())