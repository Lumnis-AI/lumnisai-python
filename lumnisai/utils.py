"""Utility functions for the LumnisAI SDK."""

from typing import Any
from .models.response import ProgressEntry


def display_progress(update: ProgressEntry, indent: str = "\t") -> None:
    """Display a progress update with optional tool calls.
    
    Simple one-liner replacement for:
        print(f"{update.state.upper()} - {update.message}")
    
    Now just use:
        display_progress(update)
    
    This will display the message and any associated tool calls. The SDK now
    yields both new messages and tool call updates (with state="tool_update").
    
    Args:
        update: A ProgressEntry from streaming
        indent: Indentation string for tool calls (default: tab)
    """
    # Special handling for tool updates (just show the tools, not the message)
    if update.state == "tool_update":
        # For tool updates, only show the tool calls
        if hasattr(update, 'tool_calls') and update.tool_calls:
            for tool_call in update.tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                tool_args = tool_call.get('args', {})
                
                print(f"{indent}→ {tool_name}", end="")
                if tool_args:
                    # Format args compactly
                    args_str = ", ".join(f"{k}={repr(v)}" for k, v in tool_args.items())
                    print(f"({args_str})")
                else:
                    print()
    else:
        # Display main message
        print(f"{update.state.upper()} - {update.message}")
        
        # Display tool calls if present
        if hasattr(update, 'tool_calls') and update.tool_calls:
            for tool_call in update.tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                tool_args = tool_call.get('args', {})
                
                print(f"{indent}→ {tool_name}", end="")
                if tool_args:
                    # Format args compactly
                    args_str = ", ".join(f"{k}={repr(v)}" for k, v in tool_args.items())
                    print(f"({args_str})")
                else:
                    print()


def format_progress_entry(state: str, message: str, tool_calls: list[dict[str, Any]] | None = None) -> str:
    """Format a progress entry with optional tool calls.
    
    Args:
        state: The state of the progress entry (e.g., 'processing', 'completed')
        message: The progress message
        tool_calls: Optional list of tool calls associated with this message
        
    Returns:
        Formatted string with message and indented tool calls
    """
    lines = [f"{state.upper()}: {message}"]
    
    if tool_calls:
        for tool_call in tool_calls:
            tool_name = tool_call.get('name', 'unknown')
            tool_args = tool_call.get('args', {})
            
            if tool_args:
                # Format args compactly
                args_str = ", ".join(f"{k}={repr(v)}" for k, v in tool_args.items())
                lines.append(f"\t→ {tool_name}({args_str})")
            else:
                lines.append(f"\t→ {tool_name}")
    
    return '\n'.join(lines)


class ProgressTracker:
    """Track and format progress entries to avoid duplicates."""
    
    def __init__(self):
        self.seen_messages = set()
        self.message_tool_calls = {}  # Dict[message_key, Set[tool_call_key]]
    
    def format_new_entries(self, state: str, message: str, tool_calls: list[dict[str, Any]] | None = None) -> str | None:
        """Format new progress entries, returning None if nothing new to display.
        
        Args:
            state: The state of the progress entry
            message: The progress message
            tool_calls: Optional list of tool calls
            
        Returns:
            Formatted string if there are new entries to display, None otherwise
        """
        message_key = f"{state}:{message}"
        output_lines = []
        
        # Check if this is a new message
        if message_key not in self.seen_messages:
            output_lines.append(f"{state.upper()}: {message}")
            self.seen_messages.add(message_key)
            self.message_tool_calls[message_key] = set()
        
        # Check for new tool calls
        if tool_calls and message_key in self.message_tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                tool_args = tool_call.get('args', {})
                tool_key = f"{tool_name}:{str(tool_args)}"
                
                if tool_key not in self.message_tool_calls[message_key]:
                    if tool_args:
                        args_str = ", ".join(f"{k}={repr(v)}" for k, v in tool_args.items())
                        output_lines.append(f"\t→ {tool_name}({args_str})")
                    else:
                        output_lines.append(f"\t→ {tool_name}")
                    self.message_tool_calls[message_key].add(tool_key)
        
        return '\n'.join(output_lines) if output_lines else None