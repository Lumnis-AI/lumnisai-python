#!/usr/bin/env python3
"""
Simple progress tracking example using progress=True parameter.
Shows automatic progress printing for status and message updates.
"""

import asyncio
import lumnisai
from lumnisai.types import Scope

async def demo_progress():
    """Demonstrate automatic progress tracking."""
    
    # Auto-initializes on first use (using TENANT scope for demo)
    client = lumnisai.AsyncClient(scope=Scope.TENANT)
    
    print("=== Example: Progress Tracking ===")
    print("Running task with progress=True...")
    print()
    
    response = await client.invoke(
        "Write a brief summary of the latest machine learning concepts and most recent advancements",
        show_progress=True  # This enables automatic progress printing
    )
    
    print()
    print("=== Task Complete ===")
    print(f"Final output: {response.output_text[:200]}...")
    
    # Cleanup
    await client.close()

async def demo_no_progress():
    """Demonstrate without progress tracking (silent)."""
    
    client = lumnisai.AsyncClient(scope=Scope.TENANT)
    
    print("\n" + "="*50)
    print("=== Example: No Progress (Silent) ===")
    print("Running task without progress...")
    
    response = await client.invoke(
        "Explain quantum computing in simple terms"
        # progress=False is the default, so we don't need to specify it
    )
    
    print("Task completed silently!")
    print(f"Result: {response.output_text[:100]}...")
    
    # Cleanup
    await client.close()

async def main():
    await demo_progress()
    await demo_no_progress()

if __name__ == "__main__":
    asyncio.run(main())