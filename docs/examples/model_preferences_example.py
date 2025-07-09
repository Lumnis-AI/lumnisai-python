"""
Model Preferences Example for Lumnis SDK

This example demonstrates how to configure and use model preferences
to control which LLM models are used for different use cases.
"""

import asyncio
from typing import Dict

import lumnisai
from lumnisai.models import ModelPreferenceCreate
from lumnisai.types import ModelType


def sync_example():
    """Synchronous example of model preferences management."""
    client = lumnisai.Client()
    
    print("🤖 Model Preferences Management Example\n")
    
    # 1. Configure API keys for providers
    print("1️⃣ Configuring API keys...")
    # Note: Replace with your actual API keys
    client.add_api_key(
        provider="OPENAI_API_KEY",
        api_key="sk-..."  # Your OpenAI API key
    )
    client.add_api_key(
        provider="ANTHROPIC_API_KEY", 
        api_key="sk-ant-..."  # Your Anthropic API key
    )
    
    # 2. Get current model preferences
    print("\n2️⃣ Getting current model preferences...")
    preferences = client.get_model_preferences(include_defaults=True)
    
    print(f"Tenant ID: {preferences.tenant_id}")
    print(f"Number of configured preferences: {len(preferences.preferences)}")
    
    if preferences.defaults_applied:
        print(f"Defaults applied for: {', '.join(preferences.defaults_applied)}")
    
    # Display current preferences
    for pref in preferences.preferences:
        print(f"  • {pref.model_type}: {pref.provider}:{pref.model_name} (Active: {pref.is_active})")
    
    # 3. Display current preferences in detail
    print("\n3️⃣ Current preferences details...")
    for pref in preferences.preferences:
        status = "✅ Active" if pref.is_active else "❌ Inactive"
        print(f"  {pref.model_type}: {pref.provider}:{pref.model_name} - {status}")
        print(f"    Created: {pref.created_at}")
        print(f"    Updated: {pref.updated_at}")
    
    # 4. Test model preference updates
    print("\n4️⃣ Testing preference updates...")
    print("Updating REASONING_MODEL preference...")
    
    # Update preferences
    updated_prefs = client.update_model_preferences({
        "REASONING_MODEL": {
            "provider": "openai",
            "model_name": "o1"
        }
    })
    print(f"  Updated {len(updated_prefs.preferences)} preferences")
    
    # 5. Bulk update model preferences
    print("\n5️⃣ Bulk updating model preferences...")
    
    # Update multiple preferences at once using update_bulk
    new_preferences = {
        "FAST_MODEL": {
            "provider": "openai",
            "model_name": "gpt-4o-mini"
        },
        "SMART_MODEL": {
            "provider": "openai",
            "model_name": "gpt-4o"
        }
    }
    
    updated = client.update_model_preferences(new_preferences)
    print(f"Updated {len(updated.preferences)} preferences")
    
    # 6. Update another preference
    print("\n6️⃣ Updating another model preference...")
    single_update = client.update_model_preferences({
        "CHEAP_MODEL": {
            "provider": "google_genai",
            "model_name": "gemini-2.0-flash-lite"
        }
    })
    print(f"Updated preferences: {len(single_update.preferences)}")
    
    # 7. Use model overrides in a response
    print("\n7️⃣ Creating response with model override...")
    
    # This will use the specified model instead of the configured preference
    response = client.responses.create(
        messages=[
            {"role": "user", "content": "Write a haiku about AI"}
        ],
        model_overrides={
            "smart_model": "anthropic:claude-3-7-sonnet-20250219"
        }
    )
    
    print(f"Response: {response.output_text}")
    
    # 8. Show final preferences
    print("\n8️⃣ Final preferences summary...")
    final_prefs = client.get_model_preferences()
    print(f"Total preferences configured: {len(final_prefs.preferences)}")
    for pref in final_prefs.preferences:
        print(f"  {pref.model_type}: {pref.provider}:{pref.model_name}")


async def async_example():
    """Asynchronous example with concurrent operations."""
    async with lumnisai.AsyncClient() as client:
        print("\n🚀 Async Model Preferences Example\n")
        
        # Concurrent operations
        print("Running multiple checks concurrently...")
        
        # Get and update preferences concurrently
        preferences_task = client.get_model_preferences()
        update_task = client.update_model_preferences({
            "FAST_MODEL": {"provider": "openai", "model_name": "gpt-4o-mini"},
            "SMART_MODEL": {"provider": "openai", "model_name": "gpt-4o"}
        })
        
        preferences, updated_prefs = await asyncio.gather(
            preferences_task,
            update_task
        )
        
        print(f"✅ Got {len(preferences.preferences)} current preferences")
        print(f"✅ Updated {len(updated_prefs.preferences)} preferences")
        
        # Use different models for different types of requests
        print("\n🎯 Using different models for different tasks...")
        
        tasks = [
            # Fast model for simple task
            client.invoke(
                "What is 2+2?",
                model_overrides={"fast_model": "openai:gpt-4o-mini"},
                user_id="user-123"
            ),
            # Smart model for complex task
            client.invoke(
                "Explain quantum computing in simple terms",
                model_overrides={"smart_model": "openai:gpt-4o"},
                user_id="user-123"
            ),
            # Reasoning model for logic task
            client.invoke(
                "If all roses are flowers and some flowers fade quickly, what can we conclude?",
                model_overrides={"reasoning_model": "openai:o1"},
                user_id="user-123"
            ),
        ]
        
        responses = await asyncio.gather(*tasks)
        
        print("Fast model response:", responses[0].output_text[:50] + "...")
        print("Smart model response:", responses[1].output_text[:50] + "...")
        print("Reasoning model response:", responses[2].output_text[:50] + "...")


def advanced_example():
    """Advanced example with error handling and best practices."""
    client = lumnisai.Client()
    
    print("\n🎓 Advanced Model Preferences Example\n")
    
    # Best practice: Set commonly available models
    print("Setting commonly available model preferences...")
    
    # Set preferences for well-known models
    try:
        # Update multiple preferences at once
        updated = client.update_model_preferences({
            ModelType.SMART_MODEL: {
                "provider": "openai",
                "model_name": "gpt-4o"
            },
            ModelType.FAST_MODEL: {
                "provider": "openai", 
                "model_name": "gpt-4o-mini"
            }
        })
        print(f"✅ Updated {len(updated.preferences)} preferences")
        
    except Exception as e:
        print(f"❌ Error setting preferences: {e}")
        print("Make sure you have configured the required API keys")
    
    # Example: Dynamic model selection based on task
    print("\n📊 Dynamic model selection based on task complexity...")
    
    def select_model_for_task(task_description: str) -> Dict[str, str]:
        """Select appropriate model based on task complexity."""
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ["simple", "basic", "quick", "what is"]):
            return {"fast_model": "openai:gpt-4o-mini"}
        elif any(word in task_lower for word in ["reasoning", "logic", "deduce", "conclude"]):
            return {"reasoning_model": "openai:o1"}
        elif any(word in task_lower for word in ["image", "picture", "visual", "describe"]):
            return {"vision_model": "openai:gpt-4o-2024-08-06"}
        else:
            return {"smart_model": "openai:gpt-4o"}
    
    tasks = [
        "What is the capital of France?",
        "Solve this logic puzzle: If A implies B and B implies C, what can we deduce?",
        "Write a comprehensive analysis of climate change impacts",
    ]
    
    for task in tasks:
        model_override = select_model_for_task(task)
        model_type = list(model_override.keys())[0]
        model_name = list(model_override.values())[0]
        
        print(f"\nTask: {task[:50]}...")
        print(f"Selected: {model_type} = {model_name}")
        
        try:
            response = client.invoke(
                task,
                model_overrides=model_override,
                user_id="user-123"
            )
            print(f"Response: {response.output_text[:100]}...")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("🔧 Lumnis SDK - Model Preferences Examples\n")
    
    print("=" * 60)
    sync_example()
    
    print("\n" + "=" * 60)
    asyncio.run(async_example())
    
    print("\n" + "=" * 60)
    advanced_example()
    
    print("\n✅ All examples completed!")