"""
Unit tests for the memory manager.
"""
import os
import tempfile
import pytest
from typing import Dict, Any, Optional

from src.memory.manager import MemoryManager
from src.memory.models import MemoryType, MessageRole


class TestMemoryManager:
    """Test suite for MemoryManager class."""
    
    def test_init(self):
        """Test initialization with default values."""
        manager = MemoryManager()
        assert manager.short_term is not None
        assert manager.short_term.max_size == 20
        assert manager.persistence_dir is not None
        assert manager.working_memory is None
        assert manager.long_term_memory is None
    
    def test_persistence_dir(self):
        """Test initialization with persistence directory."""
        # Create a temporary directory for persistence
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create memory manager with persistence
            manager = MemoryManager(persistence_dir=temp_dir)
            assert manager.persistence_dir == temp_dir
            assert manager.short_term.persistence_path is not None
            assert os.path.exists(os.path.dirname(manager.short_term.persistence_path))
    
    def test_store_message(self):
        """Test storing a message in memory."""
        manager = MemoryManager()
        
        # Store a message
        message = manager.store_message(
            session_id="test-session",
            user_id="test-user",
            content="Hello, world!",
            role="human"
        )
        
        # Verify message properties
        assert message.session_id == "test-session"
        assert message.user_id == "test-user"
        assert message.content == "Hello, world!"
        assert message.role == "human"
        assert message.type == MemoryType.MESSAGE
    
    def test_get_conversation_history(self):
        """Test retrieving conversation history."""
        # Create a fresh manager for this test to avoid interference
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = MemoryManager(persistence_dir=temp_dir)
            
            # Store a few messages
            manager.store_message(
                session_id="test-session",
                user_id="test-user",
                content="Hello, AI!",
                role="human"
            )
            
            manager.store_message(
                session_id="test-session",
                user_id="test-user",
                content="Hello, human! How can I help you today?",
                role="ai"
            )
            
            manager.store_message(
                session_id="test-session",
                user_id="test-user",
                content="Tell me about memory systems.",
                role="human"
            )
            
            # Store a message in a different session
            manager.store_message(
                session_id="other-session",
                user_id="other-user",
                content="This is from another session.",
                role="human"
            )
            
            # Retrieve conversation history for test-session
            history = manager.get_conversation_history(session_id="test-session")
            
            # Verify correct messages are retrieved
            assert len(history) == 3
            assert history[0].content == "Hello, AI!"
            assert history[1].content == "Hello, human! How can I help you today?"
            assert history[2].content == "Tell me about memory systems."
            
            # Verify limit parameter works
            limited_history = manager.get_conversation_history(
                session_id="test-session", 
                limit=2
            )
            assert len(limited_history) == 2
            assert limited_history[0].content == "Hello, human! How can I help you today?"
            assert limited_history[1].content == "Tell me about memory systems."
    
    def test_get_formatted_history(self):
        """Test retrieving formatted conversation history."""
        manager = MemoryManager()
        
        # Store a few messages
        manager.store_message(
            session_id="test-session",
            user_id="test-user",
            content="Hello, AI!",
            role="human"
        )
        
        manager.store_message(
            session_id="test-session",
            user_id="test-user",
            content="Hello, human! How can I help you today?",
            role="ai"
        )
        
        # Get formatted history
        formatted = manager.get_formatted_history(session_id="test-session")
        
        # Verify format
        assert "User: Hello, AI!" in formatted
        assert "Assistant: Hello, human! How can I help you today?" in formatted
    
    def test_clear_session(self):
        """Test clearing a specific session."""
        manager = MemoryManager()
        
        # Store messages in different sessions
        manager.store_message(
            session_id="session-1",
            user_id="user-1",
            content="Session 1 message",
            role="human"
        )
        
        manager.store_message(
            session_id="session-2",
            user_id="user-2",
            content="Session 2 message",
            role="human"
        )
        
        # Clear session-1
        manager.clear_session(session_id="session-1")
        
        # Verify session-1 is cleared but session-2 remains
        session1_history = manager.get_conversation_history(session_id="session-1")
        session2_history = manager.get_conversation_history(session_id="session-2")
        
        assert len(session1_history) == 0
        assert len(session2_history) == 1
        assert session2_history[0].content == "Session 2 message"
    
    def test_clear_all(self):
        """Test clearing all sessions."""
        manager = MemoryManager()
        
        # Store messages in different sessions
        manager.store_message(
            session_id="session-1",
            user_id="user-1",
            content="Session 1 message",
            role="human"
        )
        
        manager.store_message(
            session_id="session-2",
            user_id="user-2",
            content="Session 2 message",
            role="human"
        )
        
        # Clear all sessions
        manager.clear_all()
        
        # Verify all sessions are cleared
        session1_history = manager.get_conversation_history(session_id="session-1")
        session2_history = manager.get_conversation_history(session_id="session-2")
        
        assert len(session1_history) == 0
        assert len(session2_history) == 0 