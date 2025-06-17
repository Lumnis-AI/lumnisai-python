#!/usr/bin/env python3
"""
Message format examples using tenant scope (default).
Shows different ways to structure conversation messages.
"""

import asyncio
import lumnisai

async def string_message_example():
    """Simple string message example."""
    client = lumnisai.AsyncClient()
    
    print("=== String Message Example ===")
    response = await client.invoke(
        prompt="What is the capital of France?"
    )
    print(f"Response: {response.output_text}")
    
    await client.close()

async def single_message_object_example():
    """Single message object example."""
    client = lumnisai.AsyncClient()
    
    print("\n=== Single Message Object Example ===")
    response = await client.invoke(
        messages={
            "role": "user",
            "content": "Explain photosynthesis in simple terms"
        }
    )
    print(f"Response: {response.output_text}")
    
    await client.close()

async def conversation_history_example():
    """Multiple messages (conversation history) example."""
    client = lumnisai.AsyncClient()
    
    print("\n=== Conversation History Example ===")
    
    # Simulate a conversation with context
    conversation = [
        {"role": "user", "content": "What is machine learning?"},
        {"role": "assistant", "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task."},
        {"role": "user", "content": "Can you give me a practical example?"}
    ]
    
    response = await client.invoke(messages=conversation)
    print(f"Response: {response.output_text}")
    
    await client.close()

async def complex_conversation_example():
    """More complex conversation with system context."""
    client = lumnisai.AsyncClient()
    
    print("\n=== Complex Conversation Example ===")
    
    conversation = [
        {"role": "system", "content": "You are a helpful programming tutor specializing in Python."},
        {"role": "user", "content": "I'm new to Python. What should I learn first?"},
        {"role": "assistant", "content": "Great choice! Start with Python basics: variables, data types, control structures (if/else, loops), functions, and then move to data structures like lists and dictionaries."},
        {"role": "user", "content": "Can you show me a simple example of a function?"}
    ]
    
    response = await client.invoke(messages=conversation)
    print(f"Response: {response.output_text}")
    
    await client.close()

async def main():
    await string_message_example()
    await single_message_object_example()
    await conversation_history_example()
    await complex_conversation_example()

if __name__ == "__main__":
    asyncio.run(main())