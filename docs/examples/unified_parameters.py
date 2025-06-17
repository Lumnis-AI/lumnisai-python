#!/usr/bin/env python3
"""
Example demonstrating the unified parameter naming for invoke() method.

This example shows the three ways to call invoke():
1. messages= for structured message objects (recommended)
2. prompt= for simple string prompts (convenient) 
3. task= for backward compatibility (deprecated)
"""

import asyncio
import warnings
import lumnisai

async def main():
    client = lumnisai.AsyncClient()
    
    print("=== Unified Parameter Examples ===\n")
    
    # 1. Using the new 'prompt' parameter (convenient for strings)
    print("1. Using prompt= parameter (recommended for simple strings):")
    response = await client.invoke(
        prompt="What are the benefits of the new parameter naming?"
    )
    print(f"Response: {response.output_text[:100]}...\n")
    
    # 2. Using the new 'messages' parameter (recommended for structured messages)
    print("2. Using messages= parameter (recommended for structured messages):")
    response = await client.invoke(
        messages=[
            {"role": "user", "content": "Explain the difference between messages and prompt parameters"}
        ]
    )
    print(f"Response: {response.output_text[:100]}...\n")
    
    # 3. Using complex conversation with messages parameter
    print("3. Using messages= with conversation history:")
    conversation = [
        {"role": "system", "content": "You are a helpful API documentation assistant."},
        {"role": "user", "content": "How does parameter unification improve developer experience?"},
        {"role": "assistant", "content": "Parameter unification makes APIs more intuitive by aligning high-level and low-level parameter names."},
        {"role": "user", "content": "Can you give me a specific example?"}
    ]
    response = await client.invoke(messages=conversation)
    print(f"Response: {response.output_text[:100]}...\n")
    
    # 4. Backward compatibility - using deprecated 'task' parameter  
    print("4. Using deprecated task= parameter (shows warning):")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = await client.invoke(
            task="This uses the old task parameter"
        )
        if w:
            print(f"⚠️  Warning: {w[0].message}")
        print(f"Response: {response.output_text[:100]}...\n")
    
    # 5. Error handling - multiple parameters
    print("5. Error handling example (multiple parameters):")
    try:
        response = await client.invoke(
            messages="Hello",
            prompt="World"
        )
    except ValueError as e:
        print(f"❌ Expected error: {e}\n")
    
    # 6. Error handling - no parameters
    print("6. Error handling example (no parameters):")
    try:
        response = await client.invoke()
    except ValueError as e:
        print(f"❌ Expected error: {e}\n")
    
    await client.close()
    
    print("✅ All examples completed successfully!")
    print("\nRecommendations:")
    print("- Use prompt= for simple string inputs")
    print("- Use messages= for structured conversations") 
    print("- Migrate away from task= (deprecated)")

if __name__ == "__main__":
    asyncio.run(main())