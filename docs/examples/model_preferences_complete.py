"""
Complete Model Preferences Example

This example shows the complete workflow for using model preferences
with the Lumnis SDK, matching the documented API.
"""

import lumnisai

# Initialize client
client = lumnisai.Client(api_key="your-lumnis-api-key")

# 1. Configure API keys for providers you want to use
print("🔑 Configuring API keys...")
client.add_api_key(
    provider="OPENAI_API_KEY",
    api_key="your-openai-key"
)

client.add_api_key(
    provider="ANTHROPIC_API_KEY",
    api_key="your-anthropic-key"
)

# List configured API keys
keys = client.list_api_keys()
for key in keys:
    print(f"Provider: {key.provider}, Active: {key.is_active}")

# 2. Set your model preferences
print("\n⚙️ Setting model preferences...")
client.update_model_preferences({
    "SMART_MODEL": {
        "provider": "anthropic",
        "model_name": "claude-3-7-sonnet-20250219"
    },
    "FAST_MODEL": {
        "provider": "openai",
        "model_name": "gpt-4o-mini"
    }
})

# Get current preferences
preferences = client.get_model_preferences()
print(f"Configured preferences: {len(preferences.preferences)}")

# 3. Create a response using your preferences
print("\n💬 Creating response with default preferences...")
response = client.responses.create(
    messages=[
        {"role": "user", "content": "What model are you using?"}
    ]
)
print(f"Response: {response.output_text}")

# 4. Override model at runtime
print("\n🔄 Creating response with model override...")
response_with_override = client.responses.create(
    messages=[
        {"role": "user", "content": "What model are you using now?"}
    ],
    model_overrides={
        "smart_model": "openai:gpt-4o-2024-08-06"
    }
)
print(f"Override response: {response_with_override.output_text}")

# 5. Update preferences again
print("\n📝 Updating preferences again...")
client.update_model_preferences({
    "SMART_MODEL": {
        "provider": "openai",
        "model_name": "gpt-4o-2024-08-06"
    }
})

# 6. Verify current preferences
print("\n✅ Verifying updated preferences...")
updated_preferences = client.get_model_preferences()
for pref in updated_preferences.preferences:
    if pref.model_type in ["SMART_MODEL"]:
        status = "✅ Active" if pref.is_active else "❌ Inactive"
        print(f"  {pref.model_type}: {pref.provider}:{pref.model_name} - {status}")

# 7. Final preferences check
print("\n🏁 Final preferences check...")
final_preferences = client.get_model_preferences()
print(f"Total configured preferences: {len(final_preferences.preferences)}")

# 8. Clean up - delete an API key
print("\n🧹 Cleaning up...")
client.delete_api_key("OPENAI_API_KEY")
print("Deleted OpenAI API key")