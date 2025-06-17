#!/usr/bin/env python3
"""Simple test for progress=True functionality"""

import asyncio
import os
import lumnisai
from lumnisai.types import Scope


async def test_progress():
    """Test progress tracking"""
    client = lumnisai.AsyncClient(
        api_key=os.getenv("LUMNISAI_API_KEY"),
        scope=Scope.TENANT
    )
    
    print("Starting invoke with progress=True...\n")
    
    response = await client.invoke(
        "Count to 5 slowly, explaining each number",
        progress=True
    )
    
    print(f"\n=== Final Result ===\n{response.output_text}")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_progress())