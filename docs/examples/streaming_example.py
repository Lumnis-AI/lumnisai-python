#!/usr/bin/env python3
"""
Streaming responses example using tenant scope (default).
Shows real-time progress updates using invoke(stream=True).
"""

import asyncio
import lumnisai

async def main():
    # Auto-initializes on first use - no context manager needed  
    client = lumnisai.AsyncClient()
    
    print("Starting research task...")
    
    async for update in await client.invoke(
        "What is the current weather in Tokyo and boston? What is the latest news in AI and machine learning?",
        stream=True
    ):
            print(f"Status: {update.status}")
            
            # Show progress messages if available
            if update.progress and len(update.progress) > 0:
                latest = update.progress[-1]
                print(f"{latest.state.upper()}: {latest.message}")
            
            # Show final result
            if update.status == "succeeded" and update.output_text:
                print("\n" + "="*50)
                print("FINAL RESULT:")
                print("="*50)
                print(update.output_text)
            elif update.status == "failed":
                print("Task failed!")
                break
    
    # Optional cleanup
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())