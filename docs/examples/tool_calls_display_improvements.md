# Tool Calls Display Improvements for Lumnis AI SDK

## Overview

This document explores various approaches to improve the display of tool calls in streaming responses from the Lumnis AI SDK. Currently, tool calls are displayed inline with messages, but we want to create a more structured, hierarchical display that clearly shows which tool calls belong to which messages.

## Current Implementation

### Current Behavior
```python
# Current streaming display
async for update in await client.invoke("...", stream=True):
    print(f"{update.state.upper()} - {update.message}")
```

Output:
```
PROCESSING - Agent thinking...
PROCESSING - Analyzing request...
PROCESSING - Research latest trends...
PROCESSING - Send email with summary...
COMPLETED - Task completed successfully
```

### Current Data Structure
```python
class ProgressEntry(BaseModel):
    ts: datetime
    state: str
    message: str
    output_text: str | None = None
    tool_calls: list[dict[str, Any]] | None = None  # Recently added
```

## Proposed Improvements

### Approach 1: Simple Hierarchical Display

Create a simple display helper that formats tool calls with indentation:

```python
def display_progress_entry(entry: ProgressEntry, indent: str = "  "):
    """Display a progress entry with hierarchical tool calls."""
    # Display main message
    print(f"{entry.state.upper()} - {entry.message}")
    
    # Display tool calls if present
    if entry.tool_calls:
        for tool_call in entry.tool_calls:
            print(f"{indent}⧉ {tool_call.get('name', 'Unknown Tool')}")
            if 'arguments' in tool_call:
                for key, value in tool_call['arguments'].items():
                    print(f"{indent*2}• {key}: {value}")
            if 'result' in tool_call:
                print(f"{indent*2}→ {tool_call['result']}")

# Usage
async for entry in await client.invoke("...", stream=True):
    display_progress_entry(entry)
```

Expected Output:
```
PROCESSING - Researching AI trends...
  ⧉ web_search
    • query: latest AI agent trends 2025
    → Found 15 relevant articles
  ⧉ analyze_papers
    • topics: ['agentic models', 'LLM agents']
    → Analyzed 8 recent papers
PROCESSING - Composing email...
  ⧉ send_email
    • to: moriba.jaye@gmail.com
    • subject: AI Trends Summary
    → Email sent successfully
```

### Approach 2: Rich Terminal Display

Using the `rich` library for better terminal formatting:

```python
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

class RichProgressDisplay:
    def __init__(self):
        self.console = Console()
        self.current_tree = None
        
    def display_entry(self, entry: ProgressEntry):
        """Display progress entry with rich formatting."""
        # Create a panel for the main message
        panel = Panel(
            entry.message,
            title=f"[bold]{entry.state.upper()}[/bold]",
            border_style="blue" if entry.state == "processing" else "green"
        )
        self.console.print(panel)
        
        # Display tool calls as a tree
        if entry.tool_calls:
            tree = Tree("🔧 Tool Calls")
            for tool_call in entry.tool_calls:
                tool_node = tree.add(f"[cyan]{tool_call.get('name', 'Unknown')}[/cyan]")
                
                # Add arguments
                if 'arguments' in tool_call:
                    args_node = tool_node.add("[dim]Arguments[/dim]")
                    for key, value in tool_call['arguments'].items():
                        args_node.add(f"{key}: {value}")
                
                # Add result
                if 'result' in tool_call:
                    result_node = tool_node.add("[dim]Result[/dim]")
                    result_node.add(f"[green]{tool_call['result']}[/green]")
            
            self.console.print(tree)

# Usage
display = RichProgressDisplay()
async for entry in await client.invoke("...", stream=True):
    display.display_entry(entry)
```

### Approach 3: Interactive Terminal UI

Using `textual` for a full TUI experience:

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ScrollView, Tree
from textual.containers import Container, Vertical
from datetime import datetime
import asyncio

class ToolCallsDisplay(App):
    """Interactive display for streaming responses with tool calls."""
    
    CSS = """
    .message-box {
        border: solid green;
        margin: 1;
        padding: 1;
    }
    
    .tool-call {
        border: solid cyan;
        margin-left: 2;
        padding: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollView(id="messages")
        yield Footer()
    
    async def add_progress_entry(self, entry: ProgressEntry):
        """Add a new progress entry to the display."""
        messages = self.query_one("#messages", ScrollView)
        
        # Create message container
        message_widget = Static(
            f"[bold]{entry.state.upper()}[/bold]: {entry.message}",
            classes="message-box"
        )
        messages.mount(message_widget)
        
        # Add tool calls
        if entry.tool_calls:
            for tool_call in entry.tool_calls:
                tool_widget = Static(
                    f"🔧 {tool_call.get('name', 'Unknown')}\n"
                    f"   Args: {tool_call.get('arguments', {})}\n"
                    f"   Result: {tool_call.get('result', 'Pending...')}",
                    classes="tool-call"
                )
                messages.mount(tool_widget)
        
        # Auto-scroll to bottom
        messages.scroll_end()

# Usage
app = ToolCallsDisplay()
# Run in separate task and feed updates
```

### Approach 4: JSON-based Display with Collapsible Sections

For Jupyter notebooks or web interfaces:

```python
from IPython.display import display, HTML, Javascript
import json
import uuid

class CollapsibleProgressDisplay:
    def __init__(self):
        self.entries = []
        self.display_id = str(uuid.uuid4())
        
    def add_entry(self, entry: ProgressEntry):
        """Add and display a progress entry with collapsible tool calls."""
        entry_id = f"entry_{len(self.entries)}"
        
        html = f"""
        <div class="progress-entry" style="margin: 10px 0; border-left: 3px solid #4CAF50; padding-left: 10px;">
            <div style="font-weight: bold; color: #333;">
                <span style="color: {'#2196F3' if entry.state == 'processing' else '#4CAF50'};">
                    {entry.state.upper()}
                </span> - {entry.message}
            </div>
        """
        
        if entry.tool_calls:
            html += f"""
            <details style="margin-left: 20px; margin-top: 5px;">
                <summary style="cursor: pointer; color: #666;">
                    🔧 {len(entry.tool_calls)} tool call(s)
                </summary>
                <div style="margin-left: 20px; margin-top: 5px;">
            """
            
            for i, tool_call in enumerate(entry.tool_calls):
                html += f"""
                <div style="background: #f5f5f5; padding: 8px; margin: 5px 0; border-radius: 4px;">
                    <strong>{tool_call.get('name', 'Unknown')}</strong>
                    <pre style="margin: 5px 0; font-size: 0.9em;">{json.dumps(tool_call.get('arguments', {}), indent=2)}</pre>
                    {f'<div style="color: green;">→ {tool_call.get("result", "")}</div>' if 'result' in tool_call else ''}
                </div>
                """
            
            html += "</div></details>"
        
        html += "</div>"
        
        display(HTML(html))
        self.entries.append(entry)

# Usage in Jupyter
display_handler = CollapsibleProgressDisplay()
async for entry in await client.invoke("...", stream=True):
    display_handler.add_entry(entry)
```

### Approach 5: Structured Logging Format

For production environments with log aggregation:

```python
import json
import logging
from typing import Dict, Any

class StructuredProgressLogger:
    def __init__(self, logger_name: str = "lumnis.progress"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        # Create JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log_entry(self, entry: ProgressEntry, context: Dict[str, Any] = None):
        """Log progress entry in structured format."""
        log_data = {
            "timestamp": entry.ts.isoformat(),
            "state": entry.state,
            "message": entry.message,
            "context": context or {}
        }
        
        if entry.tool_calls:
            log_data["tool_calls"] = [
                {
                    "name": tc.get("name"),
                    "arguments": tc.get("arguments"),
                    "result": tc.get("result"),
                    "duration_ms": tc.get("duration_ms")
                }
                for tc in entry.tool_calls
            ]
        
        if entry.output_text:
            log_data["output_text"] = entry.output_text[:500]  # Truncate for logs
        
        self.logger.info(json.dumps(log_data))

# Usage
logger = StructuredProgressLogger()
async for entry in await client.invoke("...", stream=True):
    logger.log_entry(entry, context={"user_id": "user-123", "session_id": "sess-456"})
```

## Implementation Recommendations

### 1. Extend ProgressEntry Model

Consider extending the ProgressEntry model to include more structured tool call information:

```python
class ToolCall(BaseModel):
    """Structured tool call information."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: Any | None = None
    status: Literal["pending", "running", "completed", "failed"] = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    
    @property
    def duration_ms(self) -> int | None:
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return None

class ProgressEntry(BaseModel):
    ts: datetime = Field(description="Timestamp")
    state: str = Field(description="Current state")
    message: str
    output_text: str | None = None
    tool_calls: list[ToolCall] | None = None  # Use structured ToolCall
```

### 2. Built-in Display Methods

Add display methods directly to the SDK:

```python
class AsyncClient:
    async def invoke_with_display(
        self,
        messages: str,
        *,
        display_mode: Literal["simple", "rich", "json"] = "simple",
        show_tool_calls: bool = True,
        **kwargs
    ):
        """Invoke with built-in display formatting."""
        display_handler = self._get_display_handler(display_mode)
        
        async for entry in await self.invoke(messages, stream=True, **kwargs):
            display_handler.show(entry, show_tool_calls=show_tool_calls)
            
            if entry.output_text:
                return entry
```

### 3. Callback-based Approach

Allow custom callbacks for maximum flexibility:

```python
from typing import Protocol

class ProgressCallback(Protocol):
    """Protocol for progress callbacks."""
    def on_state_change(self, entry: ProgressEntry) -> None: ...
    def on_tool_call_start(self, tool_call: ToolCall) -> None: ...
    def on_tool_call_complete(self, tool_call: ToolCall) -> None: ...
    def on_completion(self, final_output: str) -> None: ...

class CustomProgressHandler:
    """Example custom progress handler."""
    def on_state_change(self, entry: ProgressEntry):
        print(f"[{entry.ts.strftime('%H:%M:%S')}] {entry.state}: {entry.message}")
    
    def on_tool_call_start(self, tool_call: ToolCall):
        print(f"  ▶ Starting {tool_call.name}...")
    
    def on_tool_call_complete(self, tool_call: ToolCall):
        print(f"  ✓ {tool_call.name} completed in {tool_call.duration_ms}ms")
    
    def on_completion(self, final_output: str):
        print(f"\n{'='*50}\nFinal Output:\n{final_output}")

# Usage
handler = CustomProgressHandler()
async for entry in await client.invoke("...", stream=True, progress_callback=handler):
    # Callback methods are called automatically
    pass
```

## Incremental Update Handling

### Current Implementation Limitation

The current SDK implementation has a limitation - it only tracks new progress entries but **doesn't detect when existing entries get updated with new tool calls**:

```python
# From lumnisai/async_client.py - CURRENT LIMITATION
async def _create_stream_generator(...):
    last_message_count = 0
    
    while True:
        current = await self.responses.get(response.response_id, wait=wait_timeout)
        current_msg_count = len(current.progress) if current.progress else 0
        
        if current_msg_count > last_message_count and current.progress:
            # ISSUE: Only yields NEW entries, not UPDATED ones with new tool calls
            for i in range(last_message_count, current_msg_count):
                yield current.progress[i]
            last_message_count = current_msg_count
```

**The Problem:**
- ❌ **Missing tool call updates**: If entry #3 gets a new tool call added, it won't be yielded again
- ❌ **Incomplete streaming**: Users won't see tool calls that are added to existing messages
- ✅ **New messages work**: Only completely new progress entries are detected

### Improved Implementation: Track Both Messages and Tool Calls

To properly handle incremental updates, we need to track tool calls within each progress entry:

```python
async def _create_stream_generator_improved(self, ...):
    """Improved generator that yields on new messages OR new tool calls."""
    last_message_count = 0
    tool_call_counts = {}  # Track tool calls per message index
    
    while True:
        current = await self.responses.get(response.response_id, wait=wait_timeout)
        current_msg_count = len(current.progress) if current.progress else 0
        
        # Check for new messages
        if current_msg_count > last_message_count and current.progress:
            for i in range(last_message_count, current_msg_count):
                entry = current.progress[i]
                # Track initial tool call count for new entries
                tool_call_counts[i] = len(entry.tool_calls) if entry.tool_calls else 0
                yield entry
            last_message_count = current_msg_count
        
        # Check for new tool calls in existing messages
        for i in range(min(last_message_count, current_msg_count)):
            if i < len(current.progress):
                entry = current.progress[i]
                current_tc_count = len(entry.tool_calls) if entry.tool_calls else 0
                previous_tc_count = tool_call_counts.get(i, 0)
                
                if current_tc_count > previous_tc_count:
                    # Yield update with only the NEW tool calls
                    new_tool_calls = entry.tool_calls[previous_tc_count:] if entry.tool_calls else []
                    update_entry = ProgressEntry(
                        ts=entry.ts,
                        state=entry.state,
                        message=f"Tool calls added to: {entry.message}",
                        tool_calls=new_tool_calls
                    )
                    yield update_entry
                    tool_call_counts[i] = current_tc_count
        
        # Check if completed
        if current.status in ("succeeded", "failed", "cancelled"):
            # ... completion logic ...
            break
```

### Alternative: Delta-based Updates

Another approach is to yield delta updates that clearly indicate what's new:

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class StreamUpdate:
    """Represents an incremental update in the stream."""
    type: Literal["new_message", "new_tool_calls", "completed"]
    entry: ProgressEntry | None = None
    new_tool_calls: list[dict] | None = None
    message_index: int | None = None

async def _create_delta_stream_generator(self, ...):
    """Generator that yields delta updates for precise tracking."""
    progress_snapshot = []
    
    while True:
        current = await self.responses.get(response.response_id, wait=wait_timeout)
        
        # Compare with snapshot to find changes
        current_progress = current.progress or []
        
        # Check for new messages
        for i in range(len(progress_snapshot), len(current_progress)):
            yield StreamUpdate(
                type="new_message",
                entry=current_progress[i],
                message_index=i
            )
            progress_snapshot.append({
                'message': current_progress[i].message,
                'tool_calls': current_progress[i].tool_calls.copy() if current_progress[i].tool_calls else []
            })
        
        # Check for new tool calls in existing messages
        for i in range(min(len(progress_snapshot), len(current_progress))):
            current_entry = current_progress[i]
            snapshot_entry = progress_snapshot[i]
            
            current_tc = current_entry.tool_calls or []
            snapshot_tc = snapshot_entry['tool_calls']
            
            if len(current_tc) > len(snapshot_tc):
                # New tool calls detected
                new_calls = current_tc[len(snapshot_tc):]
                yield StreamUpdate(
                    type="new_tool_calls",
                    new_tool_calls=new_calls,
                    message_index=i,
                    entry=current_entry
                )
                snapshot_entry['tool_calls'] = current_tc.copy()
        
        # Check if completed
        if current.status in ("succeeded", "failed", "cancelled"):
            yield StreamUpdate(type="completed", entry=current_progress[-1] if current_progress else None)
            break
```

### Display Implementation with Improved Tracking

Using the improved implementation that tracks both messages and tool calls:

```python
class ImprovedProgressDisplay:
    """Display handler that properly tracks messages and tool calls."""
    
    def __init__(self):
        self.displayed_messages = set()  # Track displayed message IDs
        self.displayed_tool_calls = {}   # message_index -> set of tool call IDs
    
    def display_update(self, update: StreamUpdate):
        """Display a stream update based on its type."""
        if update.type == "new_message":
            print(f"{update.entry.state.upper()} - {update.entry.message}")
            self.displayed_messages.add(update.message_index)
            
            # Display initial tool calls if any
            if update.entry.tool_calls:
                for tc in update.entry.tool_calls:
                    print(f"  ⧉ {tc.get('name')}")
        
        elif update.type == "new_tool_calls":
            # Tool calls added to existing message
            print(f"  [Updated] New tool calls for message #{update.message_index}:")
            for tc in update.new_tool_calls:
                print(f"    ⧉ {tc.get('name')}")
        
        elif update.type == "completed":
            if update.entry and update.entry.output_text:
                print(f"\n{'='*50}")
                print("FINAL OUTPUT:")
                print(update.entry.output_text)

# Usage with improved generator
display = ImprovedProgressDisplay()
async for update in improved_stream_generator():
    display.display_update(update)
```

### Advanced: Tracking Tool Call Updates

If you need to track tool call status changes (e.g., pending → running → completed), implement a stateful tracker:

```python
class ToolCallTracker:
    """Track tool call status changes across progress entries."""
    
    def __init__(self):
        self.tool_calls = {}  # id -> ToolCall
        
    def process_entry(self, entry: ProgressEntry):
        """Process entry and detect tool call updates."""
        if not entry.tool_calls:
            return []
            
        updates = []
        for tool_call in entry.tool_calls:
            tc_id = tool_call.get('id')
            if tc_id not in self.tool_calls:
                # New tool call
                updates.append(('new', tool_call))
                self.tool_calls[tc_id] = tool_call
            else:
                # Check for status change
                old_status = self.tool_calls[tc_id].get('status')
                new_status = tool_call.get('status')
                if old_status != new_status:
                    updates.append(('updated', tool_call))
                    self.tool_calls[tc_id] = tool_call
        
        return updates

# Usage
tracker = ToolCallTracker()
async for entry in await client.invoke("...", stream=True):
    print(f"{entry.state.upper()} - {entry.message}")
    
    # Track tool call updates
    updates = tracker.process_entry(entry)
    for update_type, tool_call in updates:
        if update_type == 'new':
            print(f"  ▶ Starting: {tool_call.get('name')}")
        elif update_type == 'updated':
            print(f"  ✓ Updated: {tool_call.get('name')} → {tool_call.get('status')}")
```

### Batching Considerations

The API may batch multiple tool calls in a single `ProgressEntry`:

```python
# Single ProgressEntry might contain multiple tool calls
ProgressEntry(
    state="processing",
    message="Executing multiple searches",
    tool_calls=[
        {"name": "web_search", "arguments": {"query": "AI trends"}},
        {"name": "web_search", "arguments": {"query": "ML papers"}},
        {"name": "analyze_results", "arguments": {"count": 2}}
    ]
)
```

Display handlers should be prepared for this:

```python
def display_progress_entry(entry: ProgressEntry):
    print(f"{entry.state.upper()} - {entry.message}")
    
    if entry.tool_calls:
        # Handle multiple tool calls in one entry
        if len(entry.tool_calls) > 1:
            print(f"  ⧉ Executing {len(entry.tool_calls)} tool calls:")
            for tc in entry.tool_calls:
                print(f"    • {tc.get('name')}")
        else:
            # Single tool call
            tc = entry.tool_calls[0]
            print(f"  ⧉ {tc.get('name')}")
```

## Testing and Validation

### Test Cases

1. **Basic Tool Call Display**
   - Single tool call
   - Multiple sequential tool calls
   - Nested tool calls

2. **Error Handling**
   - Failed tool calls
   - Timeout scenarios
   - Partial results

3. **Performance**
   - Large number of tool calls
   - Rapid updates
   - Memory usage with long-running streams

### Example Test Implementation

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_tool_call_display():
    """Test tool call display formatting."""
    # Create mock progress entry
    entry = ProgressEntry(
        ts=datetime.now(),
        state="processing",
        message="Executing search",
        tool_calls=[
            {
                "name": "web_search",
                "arguments": {"query": "test"},
                "result": "Found 10 results"
            }
        ]
    )
    
    # Test simple display
    display = SimpleProgressDisplay()
    output = display.format_entry(entry)
    assert "web_search" in output
    assert "Found 10 results" in output
```

## Migration Path

### Phase 1: Add Tool Call Support (Current)
- ✅ Add `tool_calls` field to ProgressEntry
- ⬜ Parse tool calls from API responses
- ⬜ Include in streaming updates

### Phase 2: Basic Display Improvements
- ⬜ Implement simple hierarchical display
- ⬜ Add to examples and documentation
- ⬜ Gather user feedback

### Phase 3: Advanced Features
- ⬜ Rich terminal support
- ⬜ Jupyter notebook integration
- ⬜ Callback system

### Phase 4: Production Features
- ⬜ Structured logging
- ⬜ Metrics and monitoring
- ⬜ Performance optimization

## Recommended Implementation Path

### Immediate Fix Required

The SDK's `_create_stream_generator` method needs to be updated to detect both:
1. **New progress entries** (messages) - ✅ Currently working
2. **New tool calls in existing entries** - ❌ Currently missing

### Recommended Solution

Implement the **Improved Generator** approach that tracks tool call counts per message:

```python
# File: lumnisai/async_client.py
async def _create_stream_generator(self, ...):
    last_message_count = 0
    tool_call_counts = {}  # ADD: Track tool calls per message
    
    while True:
        current = await self.responses.get(response.response_id, wait=wait_timeout)
        current_msg_count = len(current.progress) if current.progress else 0
        
        # Existing: Check for new messages
        if current_msg_count > last_message_count and current.progress:
            for i in range(last_message_count, current_msg_count):
                entry = current.progress[i]
                tool_call_counts[i] = len(entry.tool_calls) if entry.tool_calls else 0
                yield entry
            last_message_count = current_msg_count
        
        # NEW: Check for tool call updates in existing messages
        for i in range(min(last_message_count, current_msg_count)):
            if i < len(current.progress):
                entry = current.progress[i]
                current_tc_count = len(entry.tool_calls) if entry.tool_calls else 0
                previous_tc_count = tool_call_counts.get(i, 0)
                
                if current_tc_count > previous_tc_count:
                    # Create an update entry with just the new tool calls
                    new_tool_calls = entry.tool_calls[previous_tc_count:]
                    yield ProgressEntry(
                        ts=datetime.now(),
                        state="tool_update",  # Special state for tool updates
                        message=f"[Tool calls for: {entry.message[:50]}...]",
                        tool_calls=new_tool_calls
                    )
                    tool_call_counts[i] = current_tc_count
        
        # Rest of the implementation...
```

### Why This Approach?

1. **Backward Compatible**: Existing code continues to work
2. **Minimal Changes**: Only adds tool call tracking to current implementation
3. **Clear Updates**: Tool call updates are clearly marked with `state="tool_update"`
4. **Efficient**: Only yields actual changes, not full re-renders

## Conclusion

The current SDK implementation has a critical limitation where tool calls added to existing progress entries are not streamed to the user. This needs to be fixed by:

1. **Tracking tool call counts** per progress entry
2. **Yielding updates** when tool calls are added to existing entries
3. **Providing clear display helpers** for formatting these updates

The recommended implementation maintains backward compatibility while ensuring users see all updates in real-time - both new messages and new tool calls.
