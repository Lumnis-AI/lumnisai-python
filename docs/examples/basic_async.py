#!/usr/bin/env python3
"""
Basic asynchronous client example using tenant scope (default).
"""

import asyncio
import lumnisai

async def main():
    # Initialize async client (defaults to tenant scope)
    # Auto-initializes on first use - no context manager needed
    client = lumnisai.AsyncClient()
    
    response = await client.invoke(
        prompt="Explain the benefits of asynchronous programming in Python"
    )
    
    print("Response:")
    print(response.output_text)
    
    # Optional: explicit cleanup for advanced users
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())