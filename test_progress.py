#!/usr/bin/env python3
"""Test progress=True functionality"""

import asyncio
import os
import lumnisai
from lumnisai.types import Scope


async def test_async_progress():
    """Test async client with progress=True"""
    print("=== Testing Async Client with progress=True ===\n")
    
    # Create client with TENANT scope to avoid user_id requirement
    client = lumnisai.AsyncClient(
        api_key=os.getenv("LUMNISAI_API_KEY"),
        scope=Scope.TENANT
    )
    
    try:
        print("Invoking with progress=True...")
        response = await client.invoke(
            "Write a haiku about Python programming",
            progress=True
        )
        
        print(f"\nFinal output:\n{response.output_text}")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
    finally:
        await client.close()


def test_sync_progress():
    """Test sync client with progress=True"""
    print("\n=== Testing Sync Client with progress=True ===\n")
    
    # Create client with TENANT scope to avoid user_id requirement
    client = lumnisai.Client(
        api_key=os.getenv("LUMNISAI_API_KEY"),
        scope=Scope.TENANT
    )
    
    try:
        print("Invoking with progress=True...")
        response = client.invoke(
            "Write a haiku about Python programming",
            progress=True
        )
        
        print(f"\nFinal output:\n{response.output_text}")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
    finally:
        client.close()


async def test_with_user_scope():
    """Test with user scope and progress"""
    print("\n=== Testing User Scope with progress=True ===\n")
    
    client = lumnisai.AsyncClient(
        api_key=os.getenv("LUMNISAI_API_KEY"),
        scope=Scope.USER
    )
    
    try:
        # First create a user
        import time
        timestamp = int(time.time())
        user = await client.create_user(
            email=f"test.progress.{timestamp}@example.com",
            first_name="Test",
            last_name="Progress"
        )
        print(f"Created user: {user.email}")
        
        print("\nInvoking with progress=True and user_id...")
        response = await client.invoke(
            "Write a haiku about Python programming",
            user_id=str(user.id),
            progress=True
        )
        
        print(f"\nFinal output:\n{response.output_text}")
        
        # Clean up
        await client.delete_user(user.id)
        print(f"\nDeleted user: {user.email}")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


if __name__ == "__main__":
    # Test async with tenant scope
    asyncio.run(test_async_progress())
    
    # Test sync with tenant scope
    test_sync_progress()
    
    # Test with user scope
    asyncio.run(test_with_user_scope())