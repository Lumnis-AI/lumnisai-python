import chainlit as cl
import lumnisai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Lumnis client
lumnis_client = lumnisai.AsyncClient()
user_id = "test_email@test.com"

@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It uses Lumnis AI to process the message with streaming and shows real-time updates.

    Args:
        message: The user's message.

    Returns:
        None.
    """
    
    try:
        # Use Lumnis to process the message with streaming
        async for update in await lumnis_client.invoke(
            prompt=message.content,
            stream=True,
            show_progress=True,
            user_id=user_id
        ):
            # Create a step for each update
            async with cl.Step(name=f"{update.state.upper()} - {update.message}") as step:
                # step.input = message.content
                
                # Show the current status and message
                step_output = f"Status: {update.state.upper()}"
                if update.message:
                    step_output += f"\nMessage: {update.message}"
                
                print(step_output)
                
                step.output = step_output
            
            # If we have the final output, send it as a message
            if hasattr(update, 'output_text') and update.output_text:
                await cl.Message(content=update.output_text).send()
                break
         
    except Exception as e:
        # Handle any errors
        await cl.Message(content=f"❌ Sorry, I encountered an error: {str(e)}").send()