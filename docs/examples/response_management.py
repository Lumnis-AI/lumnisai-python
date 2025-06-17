#!/usr/bin/env python3
"""
Response management examples using tenant scope (default).
Shows how to create, monitor, and manage responses.
"""

import asyncio
import lumnisai

async def main():
    # Auto-initializes on first use
    client = lumnisai.AsyncClient()
    
    # Create a response without waiting for completion
    print("=== Creating response without waiting ===")
    response = await client.responses.create(
        messages=[{"role": "user", "content": "Write a detailed analysis of renewable energy trends"}]
    )
    print(f"Created response: {response.response_id}")
    print(f"Initial status: {response.status}")
    
    # Poll for completion manually
    print(f"\n=== Manually polling for completion ===")
    final_response = await client.get_response(
        response.response_id,
        wait=30.0  # Wait up to 30 seconds
    )
    print(f"Final status: {final_response.status}")
    if final_response.output_text:
        print(f"Result: {final_response.output_text[:200]}...")
    
    # List all responses (tenant-wide)
    print(f"\n=== Listing all responses ===")
    responses = await client.list_responses(limit=5)
    print(f"Found {len(responses.responses)} responses:")
    for r in responses.responses:
        print(f"  - {r.response_id}: {r.status} (created: {r.created_at})")
    
    # Create another response for cancellation demo
    print(f"\n=== Testing response cancellation ===")
    long_response = await client.responses.create(
        messages=[{"role": "user", "content": "Write a comprehensive 50-page research paper on quantum computing"}]
    )
    print(f"Created long-running response: {long_response.response_id}")
    
    # Give it a moment to start processing
    await asyncio.sleep(2)
    
    # Cancel the response
    cancelled_response = await client.cancel_response(long_response.response_id)
    print(f"Cancelled response status: {cancelled_response.status}")
    
    # Verify cancellation
    check_response = await client.get_response(long_response.response_id)
    print(f"Verified status: {check_response.status}")
    
    # Example with idempotency key
    print(f"\n=== Using idempotency key ===")
    idempotency_key = "unique-task-2024-001"
    
    # First call
    response1 = await client.invoke(
        "Calculate the square root of 144",
        idempotency_key=idempotency_key
    )
    print(f"First call - Response ID: {response1.response_id}")
    print(f"Result: {response1.output_text}")
    
    # Second call with same idempotency key - should return same response
    response2 = await client.invoke(
        "Calculate the square root of 144",
        idempotency_key=idempotency_key
    )
    print(f"Second call - Response ID: {response2.response_id}")
    print(f"Same response ID? {response1.response_id == response2.response_id}")
    
    # Cleanup
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())