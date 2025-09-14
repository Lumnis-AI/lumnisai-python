#!/usr/bin/env python3
"""
Example demonstrating streaming with tool calls display.
Shows how to use the new display_progress function.
"""

import asyncio
from lumnisai import AsyncClient, display_progress

async def main():
    client = AsyncClient()
    
    print("=== Streaming with Tool Calls Display ===\n")
    
    # Example 1: Simple replacement for the old print statement
    print("Example 1: Using display_progress (one-liner replacement)")
    print("-" * 50)
    
    async for update in await client.invoke(
        """
        What are the latest trends in AI agents and machine learning? 
        What are agentic models? 
        Send email to moriba.jaye@gmail.com with a summary.
        """,
        stream=True,
        user_id="user@example.com"
    ):
        # Old way:
        # print(f"{update.state.upper()} - {update.message}")
        
        # New way - displays message AND tool calls:
        display_progress(update)
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Custom handling if needed
    print("Example 2: Custom handling for final output")
    print("-" * 50)
    
    async for update in await client.invoke(
        "Search for Python best practices and create a summary document.",
        stream=True,
        user_id="user@example.com"
    ):
        # Use display_progress for all updates
        display_progress(update)
        
        # Special handling for final output
        if update.output_text:
            print("\n" + "="*50)
            print("FINAL OUTPUT:")
            print("="*50)
            print(update.output_text)
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())