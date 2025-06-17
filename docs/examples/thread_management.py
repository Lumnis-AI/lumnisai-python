#!/usr/bin/env python3
"""
Thread management examples using tenant scope (default).
Shows how to create and manage conversation threads.
"""

import asyncio
import lumnisai

async def main():
    # Auto-initializes on first use
    client = lumnisai.AsyncClient()
    
    # Create a new thread
    print("=== Creating a new thread ===")
    thread = await client.create_thread(title="Python Learning Session")
    print(f"Created thread: {thread.thread_id}")
    print(f"Thread title: {thread.title}")
    
    # First message in the thread
    print("\n=== First message in thread ===")
    response1 = await client.invoke(
        "I want to learn Python programming. Where should I start?",
        thread_id=thread.thread_id
    )
    print(f"Response 1: {response1.output_text}")
    
    # Continue the conversation in the same thread
    print("\n=== Continuing conversation in thread ===")
    response2 = await client.invoke(
        "What about data structures? Which ones are most important?",
        thread_id=thread.thread_id
    )
    print(f"Response 2: {response2.output_text}")
    
    # Another follow-up
    print("\n=== Another follow-up in thread ===")
    response3 = await client.invoke(
        "Can you give me a practical coding exercise?",
        thread_id=thread.thread_id
    )
    print(f"Response 3: {response3.output_text}")
    
    # List all threads (tenant-wide)
    print("\n=== Listing all threads ===")
    threads = await client.list_threads(limit=5)
    print(f"Found {len(threads.threads)} threads:")
    for t in threads.threads:
        print(f"  - {t.thread_id}: {t.title or 'No title'}")
    
    # Get thread details
    print(f"\n=== Getting thread details ===")
    thread_details = await client.get_thread(thread.thread_id)
    print(f"Thread {thread_details.thread_id}:")
    print(f"  Title: {thread_details.title}")
    print(f"  Created: {thread_details.created_at}")
    print(f"  Updated: {thread_details.updated_at}")
    
    # List responses in the thread (optional - showing how to get thread history)
    print(f"\n=== Responses in this thread ===")
    responses = await client.list_responses(limit=10)
    thread_responses = [r for r in responses.responses if r.thread_id == thread.thread_id]
    print(f"Found {len(thread_responses)} responses in this thread")
    
    # Clean up - delete the thread
    print(f"\n=== Cleaning up thread ===")
    await client.delete_thread(thread.thread_id)
    print(f"Deleted thread {thread.thread_id}")
    
    # Cleanup
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())