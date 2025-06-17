#!/usr/bin/env python3
"""
Basic synchronous client example using tenant scope (default).
"""

import lumnisai

def main():
    # Initialize client (defaults to tenant scope)
    # Context manager automatically handles cleanup
    with lumnisai.Client() as client:
        # Simple AI interaction using the new 'prompt' parameter
        response = client.invoke(
            prompt="What are the key benefits of using Python for data science?"
        )
        
        print("Response:")
        print(response.output_text)

if __name__ == "__main__":
    main()