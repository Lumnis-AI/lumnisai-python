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
    
    async for entry in await client.invoke(
        "What is the current weather in Tokyo and boston? What is the latest news in AI and machine learning?",
        stream=True
    ):
            # Show progress updates
            print(f"{entry.state.upper()}: {entry.message}")
            
            # Show final result if available
            if entry.output_text:
                print("\n" + "="*50)
                print("FINAL RESULT:")
                print("="*50)
                print(entry.output_text)
    
    # Optional cleanup
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())