#!/usr/bin/env python3
"""Demo showing real-time progress tracking with flush=True fix"""

import asyncio
import time
import os
import lumnisai
from lumnisai.types import Scope


async def async_progress_demo():
    """Async demo with real-time progress"""
    print("=== Async Progress Demo ===")
    print("Watch for real-time status updates...\n")
    
    client = lumnisai.AsyncClient(
        api_key=os.getenv("LUMNISAI_API_KEY"),
        scope=Scope.TENANT
    )
    
    start_time = time.time()
    
    response = await client.invoke(
        "Research the history of Python programming language. Include its creation, major versions, and impact on the software industry. Take your time to provide a comprehensive overview.",
        progress=True
    )
    
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.1f} seconds")
    print(f"Output preview: {response.output_text[:150]}...")
    
    await client.close()


def sync_progress_demo():
    """Sync demo with real-time progress"""
    print("\n\n=== Sync Progress Demo ===")
    print("Watch for real-time status updates...\n")
    
    client = lumnisai.Client(
        api_key=os.getenv("LUMNISAI_API_KEY"),
        scope=Scope.TENANT
    )
    
    start_time = time.time()
    
    response = client.invoke(
        "List the top 5 most popular programming languages in 2024 with brief explanations.",
        progress=True
    )
    
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.1f} seconds")
    print(f"Output preview: {response.output_text[:150]}...")
    
    client.close()


async def main():
    """Run both demos"""
    # Run async demo
    await async_progress_demo()
    
    # Run sync demo
    sync_progress_demo()


if __name__ == "__main__":
    print("Progress Tracking Demo")
    print("=====================")
    print("The progress messages should appear in REAL-TIME as the task runs.")
    print("Previously, they would only appear after completion due to buffering.\n")
    
    asyncio.run(main())