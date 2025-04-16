"""
Short-term memory implementation for the agent.

This module provides a simple in-memory cache for recent messages
using a FIFO queue with configurable size.
"""
from typing import List, Dict, Any, Optional, Deque
from collections import deque
import json
import pickle
import os
from datetime import datetime

from src.memory.models import MemoryItem, MessageMemoryItem, MemoryType
from src.memory.config import get_memory_config


class ShortTermMemory:
    """
    Short-term memory implementation using an in-memory FIFO queue.
    
    Stores the most recent conversations turns for immediate context.
    """
    
    def __init__(self, max_size: Optional[int] = None, persistence_path: Optional[str] = None):
        """
        Initialize the short-term memory.
        
        Args:
            max_size: Maximum number of items to store in memory
            persistence_path: Optional path to persist memory between restarts
        """
        # Get memory configuration
        config = get_memory_config()
        
        # Use provided values or defaults from config
        self.max_size = max_size or config["short_term"]["max_size"]
        self.persistence_path = persistence_path
        self.memory_queue: Deque[MemoryItem] = deque(maxlen=self.max_size)
        self._load_from_disk()
    
    def add(self, memory_item: MemoryItem) -> None:
        """
        Add a memory item to short-term memory.
        
        Args:
            memory_item: The memory item to add
        """
        self.memory_queue.append(memory_item)
        if self.persistence_path:
            self._save_to_disk()
    
    def get_all(self, session_id: Optional[str] = None) -> List[MemoryItem]:
        """
        Get all memory items, optionally filtered by session ID.
        
        Args:
            session_id: Optional session ID to filter by
            
        Returns:
            List of memory items
        """
        if session_id:
            return [item for item in self.memory_queue if item.session_id == session_id]
        return list(self.memory_queue)
    
    def get_recent(self, count: int = 5, session_id: Optional[str] = None) -> List[MemoryItem]:
        """
        Get the most recent memory items.
        
        Args:
            count: Number of recent items to retrieve
            session_id: Optional session ID to filter by
            
        Returns:
            List of the most recent memory items
        """
        items = self.get_all(session_id)
        return items[-count:] if items else []
    
    def clear(self, session_id: Optional[str] = None) -> None:
        """
        Clear memory items, optionally only for a specific session.
        
        Args:
            session_id: Optional session ID to clear items for
        """
        if session_id:
            self.memory_queue = deque(
                [item for item in self.memory_queue if item.session_id != session_id],
                maxlen=self.max_size
            )
        else:
            self.memory_queue.clear()
        
        if self.persistence_path:
            self._save_to_disk()
    
    def to_formatted_text(self, session_id: Optional[str] = None) -> str:
        """
        Convert memory items to formatted text for prompt construction.
        
        Args:
            session_id: Optional session ID to filter by
            
        Returns:
            Formatted conversation history as a string
        """
        items = self.get_all(session_id)
        formatted_text = ""
        
        message_items = [item for item in items if item.type == MemoryType.MESSAGE]
        for item in message_items:
            if isinstance(item, MessageMemoryItem):
                role = "User" if item.role == "human" else "Assistant"
                formatted_text += f"{role}: {item.content}\n\n"
        
        return formatted_text
    
    def _save_to_disk(self) -> None:
        """Save memory state to disk if persistence is enabled."""
        if not self.persistence_path:
            return
        
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, 'wb') as f:
                pickle.dump(list(self.memory_queue), f)
        except Exception as e:
            print(f"Error saving short-term memory to disk: {str(e)}")
    
    def _load_from_disk(self) -> None:
        """Load memory state from disk if persistence is enabled."""
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        
        try:
            with open(self.persistence_path, 'rb') as f:
                items = pickle.load(f)
                self.memory_queue = deque(items, maxlen=self.max_size)
        except Exception as e:
            print(f"Error loading short-term memory from disk: {str(e)}")
            # Initialize empty queue if loading fails
            self.memory_queue = deque(maxlen=self.max_size) 