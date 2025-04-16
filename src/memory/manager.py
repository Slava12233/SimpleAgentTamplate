"""
Memory Manager for coordinating different memory components.

This module provides a unified interface for interacting with the 
hierarchical memory system (short-term, working, and long-term memory).
"""
import os
from typing import List, Dict, Any, Optional, Union

from src.memory.models import (
    MemoryItem, MessageMemoryItem, SummaryMemoryItem, 
    FactMemoryItem, MemoryType, MessageRole
)
from src.memory.short_term import ShortTermMemory
from src.memory.config import get_memory_config, update_memory_config


class MemoryManager:
    """
    Memory Manager that coordinates between different memory components.
    
    This class provides a unified interface to store and retrieve memories
    across the hierarchical memory system.
    """
    
    def __init__(
        self, 
        short_term_size: Optional[int] = None,
        persistence_dir: Optional[str] = None
    ):
        """
        Initialize the memory manager.
        
        Args:
            short_term_size: Maximum number of items in short-term memory
            persistence_dir: Optional directory for persisting memory state
        """
        # Get memory configuration
        self.config = get_memory_config()
        
        # Set up persistence paths if provided
        self.persistence_dir = persistence_dir or self.config["general"]["persistence_dir"]
        self.short_term_path = None
        
        if self.persistence_dir and self.config["general"]["persistence_enabled"]:
            os.makedirs(self.persistence_dir, exist_ok=True)
            self.short_term_path = os.path.join(self.persistence_dir, 'short_term.pkl')
        
        # Initialize memory components
        self.short_term = ShortTermMemory(
            max_size=short_term_size or self.config["short_term"]["max_size"],
            persistence_path=self.short_term_path
        )
        
        # Placeholders for future memory components
        # These will be implemented in later phases
        self.working_memory = None
        self.long_term_memory = None

    def store_message(
        self, 
        session_id: str,
        user_id: str,
        content: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MessageMemoryItem:
        """
        Store a conversation message in memory.
        
        Args:
            session_id: The session identifier
            user_id: The user identifier
            content: The message content
            role: The role of the message sender (human/ai/system)
            metadata: Optional metadata for the message
            
        Returns:
            The stored message memory item
        """
        message_item = MessageMemoryItem(
            session_id=session_id,
            user_id=user_id,
            content=content,
            role=role,
            metadata=metadata or {}
        )
        
        # Store in short-term memory
        self.short_term.add(message_item)
        
        # In future phases, we'll also store in other memory components
        # and potentially trigger summarization
        
        return message_item

    def get_conversation_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[MessageMemoryItem]:
        """
        Get recent conversation history for a session.
        
        Args:
            session_id: The session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message memory items in chronological order
        """
        # Use provided limit or default from config
        limit = limit or self.config["short_term"]["max_size"]
        
        # For now, just retrieve from short-term memory
        # In future phases, this will combine retrieval from multiple sources
        all_items = self.short_term.get_all(session_id=session_id)
        message_items = [
            item for item in all_items 
            if isinstance(item, MessageMemoryItem)
        ]
        
        # Return the most recent 'limit' items
        return message_items[-limit:] if message_items else []

    def get_formatted_history(self, session_id: str, limit: Optional[int] = None) -> str:
        """
        Get formatted conversation history for prompt construction.
        
        Args:
            session_id: The session identifier
            limit: Maximum number of messages to include
            
        Returns:
            Formatted conversation history as a string
        """
        # In Phase 1, this just returns the short-term memory formatted
        # In later phases, this will include relevant context from all memory types
        return self.short_term.to_formatted_text(session_id=session_id)

    def clear_session(self, session_id: str) -> None:
        """
        Clear all memory for a specific session.
        
        Args:
            session_id: The session identifier to clear
        """
        self.short_term.clear(session_id=session_id)
        
        # In future phases, we'll also clear from other memory components

    def clear_all(self) -> None:
        """Clear all memory across all sessions."""
        self.short_term.clear()
        
        # In future phases, we'll also clear other memory components
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """
        Update memory configuration setting.
        
        Args:
            section: The configuration section
            key: The configuration key
            value: The new value
        """
        update_memory_config(section, key, value)
        self.config = get_memory_config()
        
        # If updating short-term size, update the memory component
        if section == "short_term" and key == "max_size":
            self.short_term = ShortTermMemory(
                max_size=value,
                persistence_path=self.short_term_path
            ) 