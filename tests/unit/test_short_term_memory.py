"""
Unit tests for the short-term memory component.
"""
import os
import tempfile
import pytest
from datetime import datetime
from typing import Dict, Any

from src.memory.models import MessageMemoryItem, MemoryType, MessageRole
from src.memory.short_term import ShortTermMemory


def create_test_message(
    session_id: str = "test-session",
    user_id: str = "test-user",
    content: str = "Test message",
    role: str = "human",
    metadata: Dict[str, Any] = None
) -> MessageMemoryItem:
    """Create a test message memory item."""
    return MessageMemoryItem(
        session_id=session_id,
        user_id=user_id,
        content=content,
        role=role, 
        metadata=metadata or {},
        created_at=datetime.now()
    )


class TestShortTermMemory:
    """Test suite for ShortTermMemory class."""
    
    def test_init(self):
        """Test initialization with default values."""
        memory = ShortTermMemory()
        assert memory.max_size == 20
        assert memory.persistence_path is None
        assert len(memory.memory_queue) == 0
    
    def test_add_get(self):
        """Test adding and retrieving messages."""
        memory = ShortTermMemory(max_size=5)
        
        # Add a message
        msg = create_test_message(content="First message")
        memory.add(msg)
        
        # Verify retrieval
        items = memory.get_all()
        assert len(items) == 1
        assert items[0].content == "First message"
        
        # Add more messages
        memory.add(create_test_message(content="Second message"))
        memory.add(create_test_message(content="Third message"))
        
        # Verify all messages
        items = memory.get_all()
        assert len(items) == 3
        assert items[0].content == "First message"
        assert items[2].content == "Third message"
        
        # Test get_recent
        recent = memory.get_recent(count=2)
        assert len(recent) == 2
        assert recent[0].content == "Second message"
        assert recent[1].content == "Third message"
    
    def test_fifo_behavior(self):
        """Test FIFO queue behavior with max_size limit."""
        memory = ShortTermMemory(max_size=3)
        
        # Add more items than max_size
        for i in range(5):
            memory.add(create_test_message(content=f"Message {i+1}"))
        
        # Verify only the most recent messages are kept
        items = memory.get_all()
        assert len(items) == 3
        assert items[0].content == "Message 3"
        assert items[1].content == "Message 4"
        assert items[2].content == "Message 5"
    
    def test_session_filtering(self):
        """Test filtering by session ID."""
        memory = ShortTermMemory()
        
        # Add messages from different sessions
        memory.add(create_test_message(session_id="session-1", content="S1 Message 1"))
        memory.add(create_test_message(session_id="session-2", content="S2 Message 1"))
        memory.add(create_test_message(session_id="session-1", content="S1 Message 2"))
        
        # Get messages for session-1
        session1_items = memory.get_all(session_id="session-1")
        assert len(session1_items) == 2
        assert session1_items[0].content == "S1 Message 1"
        assert session1_items[1].content == "S1 Message 2"
        
        # Get messages for session-2
        session2_items = memory.get_all(session_id="session-2")
        assert len(session2_items) == 1
        assert session2_items[0].content == "S2 Message 1"
    
    def test_clear(self):
        """Test clearing memory."""
        memory = ShortTermMemory()
        
        # Add messages from different sessions
        memory.add(create_test_message(session_id="session-1"))
        memory.add(create_test_message(session_id="session-2"))
        memory.add(create_test_message(session_id="session-1"))
        
        # Clear session-1 only
        memory.clear(session_id="session-1")
        
        # Verify session-1 is cleared, session-2 remains
        all_items = memory.get_all()
        assert len(all_items) == 1
        assert all_items[0].session_id == "session-2"
        
        # Clear all sessions
        memory.clear()
        assert len(memory.get_all()) == 0
    
    def test_formatted_text(self):
        """Test formatted text output for prompt construction."""
        memory = ShortTermMemory()
        
        # Add a human message
        memory.add(create_test_message(
            content="Hello, how are you?",
            role="human"
        ))
        
        # Add an AI response
        memory.add(create_test_message(
            content="I'm doing well, thanks for asking!",
            role="ai"
        ))
        
        # Get formatted text
        formatted = memory.to_formatted_text()
        assert "User: Hello, how are you?" in formatted
        assert "Assistant: I'm doing well, thanks for asking!" in formatted
    
    def test_persistence(self):
        """Test persistence to disk."""
        # Create a temporary file for persistence
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            # Create memory with persistence
            memory1 = ShortTermMemory(persistence_path=temp_path)
            
            # Add some messages
            memory1.add(create_test_message(content="Persistent message 1"))
            memory1.add(create_test_message(content="Persistent message 2"))
            
            # Create a new memory instance that should load from the same file
            memory2 = ShortTermMemory(persistence_path=temp_path)
            
            # Verify messages were loaded
            items = memory2.get_all()
            assert len(items) == 2
            assert items[0].content == "Persistent message 1"
            assert items[1].content == "Persistent message 2"
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path) 