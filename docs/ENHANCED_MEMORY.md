# Enhanced Memory Architecture

This document details the enhanced hierarchical memory system implemented in the AI Agent.

## Overview

The enhanced memory system uses a tiered approach to memory management, providing more robust and efficient context handling for the agent. This architecture improves conversation coherence, context retention, and enables more sophisticated use of historical information.

## Memory Hierarchy

The memory system is structured in three distinct tiers:

### 1. Short-Term Memory
- **Purpose**: Store recent conversation turns (last 5-20 messages)
- **Implementation**: In-memory FIFO queue with persistence
- **Lifespan**: Maintained during active conversation
- **Primary Use**: Immediate context for responses

### 2. Working Memory (Upcoming)
- **Purpose**: Store important information from the current session
- **Implementation**: Structured key-value store with entity extraction
- **Lifespan**: Maintained during session lifetime
- **Primary Use**: Reference information that needs to be recalled frequently

### 3. Long-Term Memory (Upcoming)
- **Purpose**: Store historical conversations and key facts
- **Implementation**: Vector database with semantic search
- **Lifespan**: Persistent across sessions
- **Primary Use**: Selectively retrieve relevant context based on query

## Short-Term Memory Implementation

The short-term memory component, currently the primary memory system in Phase 1, is implemented in `src/memory/short_term.py`.

### Key Features

- **FIFO Queue**: Uses a deque with configurable maximum size
- **Session Filtering**: Filters memory by session ID
- **Persistence**: Saves memory state to disk between restarts
- **Formatted Output**: Converts memory to prompt-friendly text

### Core Methods

```python
def add(self, memory_item: MemoryItem) -> None:
    """Add a memory item to short-term memory."""
    self.memory_queue.append(memory_item)
    if self.persistence_path:
        self._save_to_disk()

def get_all(self, session_id: Optional[str] = None) -> List[MemoryItem]:
    """Get all memory items, optionally filtered by session ID."""
    if session_id:
        return [item for item in self.memory_queue if item.session_id == session_id]
    return list(self.memory_queue)

def to_formatted_text(self, session_id: Optional[str] = None) -> str:
    """Convert memory items to formatted text for prompt construction."""
    items = self.get_all(session_id)
    formatted_text = ""
    
    message_items = [item for item in items if item.type == MemoryType.MESSAGE]
    for item in message_items:
        if isinstance(item, MessageMemoryItem):
            role = "User" if item.role == "human" else "Assistant"
            formatted_text += f"{role}: {item.content}\n\n"
    
    return formatted_text
```

## Memory Manager

The `MemoryManager` class in `src/memory/manager.py` serves as the central coordinator for all memory components. It provides a unified interface for storing, retrieving, and managing memories across different tiers.

### Key Features

- **Unified Interface**: Single point of interaction for all memory operations
- **Configuration Management**: Uses a centralized configuration system
- **Persistence Control**: Manages persistence across memory components
- **Extensible Design**: Ready for integration with future memory tiers

### Core Methods

```python
def store_message(self, session_id: str, user_id: str, content: str, role: str, metadata: Optional[Dict[str, Any]] = None) -> MessageMemoryItem:
    """Store a conversation message in memory."""
    message_item = MessageMemoryItem(
        session_id=session_id,
        user_id=user_id,
        content=content,
        role=role,
        metadata=metadata or {}
    )
    
    # Store in short-term memory
    self.short_term.add(message_item)
    return message_item

def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[MessageMemoryItem]:
    """Get recent conversation history for a session."""
    all_items = self.short_term.get_all(session_id=session_id)
    message_items = [
        item for item in all_items 
        if isinstance(item, MessageMemoryItem)
    ]
    
    # Return the most recent 'limit' items
    limit = limit or self.config["short_term"]["max_size"]
    return message_items[-limit:] if message_items else []
```

## Memory Models

The memory system uses Pydantic models defined in `src/memory/models.py` for type-safe memory operations.

### Base Memory Item

```python
class MemoryItem(BaseModel):
    """Base model for all memory items."""
    id: Optional[str] = Field(None, description="Unique identifier")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    type: MemoryType = Field(..., description="Type of memory")
    content: str = Field(..., description="Content of the memory item")
    importance: float = Field(0.5, description="Importance score")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### Specialized Memory Items

- **MessageMemoryItem**: Stores conversation messages with role
- **SummaryMemoryItem**: Stores conversation summaries
- **FactMemoryItem**: Stores extracted facts/entities

## Configuration System

The memory system uses a configuration module (`src/memory/config.py`) that provides centralized settings management.

### Configuration Structure

```python
MEMORY_CONFIG = {
    # Short-term memory settings
    "short_term": {
        "max_size": int(os.getenv("MEMORY_SHORT_TERM_SIZE", "10")),
        "include_in_prompt": True
    },
    
    # Working memory settings (for future implementation)
    "working": {
        "enabled": False,
        "max_facts": 100,
        "importance_threshold": 0.7
    },
    
    # Long-term memory settings (for future implementation)
    "long_term": {
        "enabled": False,
        "similarity_threshold": 0.75,
        "max_results": 5
    },
    
    # General memory settings
    "general": {
        "persistence_enabled": True,
        "persistence_dir": os.getenv("MEMORY_PERSISTENCE_DIR", "./memory_data"),
        "token_limit": 4000
    }
}
```

The configuration can be modified via environment variables or programmatically with the `update_memory_config()` function.

## API Integration

The memory system is integrated with the API in `src/agent/app.py`:

```python
# Initialize the memory manager
memory_dir = os.path.join(os.path.dirname(__file__), '../../memory_data')
memory_manager = MemoryManager(
    short_term_size=10,
    persistence_dir=memory_dir
)

@app.post("/api/agent")
async def process_agent_request(request: AgentRequest):
    # Store in memory system
    memory_manager.store_message(
        session_id=request.session_id,
        user_id=request.user_id,
        content=request.query,
        role="human"
    )
    
    # Get conversation history from memory
    formatted_history = memory_manager.get_formatted_history(session_id=request.session_id)
    
    # (rest of the function)
```

The API also provides endpoints for memory inspection and management:

- `GET /memory-stats`: View memory statistics
- `POST /memory/clear/{session_id}`: Clear memory for a session

## CLI Integration

The memory system is integrated with the CLI interface in `cli.py`:

```python
# Memory commands in interactive mode
if user_input.lower() == '!memory':
    show_memory_stats(session_id)
    continue

if user_input.lower() == '!clear':
    memory_manager.clear_session(session_id)
    console.print("[bold yellow]Memory cleared for this session.[/]")
    continue
```

## Future Enhancements (Planned)

### Phase 2: Vector Database Integration
- Implement long-term memory with vector database
- Add embedding generation for semantic search
- Create migration scripts for existing conversations

### Phase 3: Working Memory & Summarization
- Implement working memory for key facts
- Add entity extraction and fact storage
- Develop automatic summarization capabilities

### Phase 4: Optimization
- Implement token usage optimization
- Add smart context selection
- Create caching mechanisms for frequent queries

## Testing

The memory system includes comprehensive unit tests:

- `tests/unit/test_short_term_memory.py`: Tests for short-term memory
- `tests/unit/test_memory_manager.py`: Tests for memory manager

These tests verify:
- Memory storage and retrieval
- Session filtering
- FIFO queue behavior
- Persistence functionality
- Formatted output generation 