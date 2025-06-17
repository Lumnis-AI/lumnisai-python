#!/usr/bin/env python3
"""
Basic API usage example with streamlined async pattern.
"""

import asyncio
import lumnisai

async def main():
    # Client defaults to tenant scope - auto-initializes on first use
    client = lumnisai.AsyncClient()
    
    response = await client.invoke(
        "Conduct deep research on the latest trends in AI and machine learning. Write a report on the top 5 trends in AI and machine learning."
    )
    print(response.output_text)
    
    # Optional cleanup
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())