"""
Pydantic models for memory objects.
"""
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class MemoryType(str, Enum):
    """Type of memory items."""
    MESSAGE = "message"         # Raw conversation message
    SUMMARY = "summary"         # Generated summary of conversation
    FACT = "fact"               # Extracted fact or entity
    METADATA = "metadata"       # System metadata


class MessageRole(str, Enum):
    """Role of a message sender."""
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"


class MemoryItem(BaseModel):
    """Base model for all memory items."""
    id: Optional[str] = Field(None, description="Unique identifier for the memory item")
    session_id: str = Field(..., description="Session ID this memory belongs to")
    user_id: str = Field(..., description="User ID this memory belongs to")
    type: MemoryType = Field(..., description="Type of memory")
    content: str = Field(..., description="Content of the memory item")
    importance: float = Field(0.5, description="Importance score between 0 and 1", ge=0, le=1)
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Updated to Pydantic V2 style configuration
    model_config = ConfigDict(
        json_schema_extra={
            "json_encoders": {
                datetime: lambda v: v.isoformat(),
            }
        }
    )


class MessageMemoryItem(MemoryItem):
    """Model for conversation message memories."""
    type: MemoryType = MemoryType.MESSAGE
    role: MessageRole = Field(..., description="Role of the message sender")

    # Updated to Pydantic V2 style validator
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Ensure type is MESSAGE."""
        if v != MemoryType.MESSAGE:
            raise ValueError(f"MessageMemoryItem type must be {MemoryType.MESSAGE}")
        return v


class SummaryMemoryItem(MemoryItem):
    """Model for conversation summary memories."""
    type: MemoryType = MemoryType.SUMMARY
    summary_type: str = Field("incremental", description="Type of summary (incremental, session, etc.)")
    source_message_ids: List[str] = Field(default_factory=list, description="IDs of messages this summary is based on")

    # Updated to Pydantic V2 style validator
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Ensure type is SUMMARY."""
        if v != MemoryType.SUMMARY:
            raise ValueError(f"SummaryMemoryItem type must be {MemoryType.SUMMARY}")
        return v


class FactMemoryItem(MemoryItem):
    """Model for extracted fact memories."""
    type: MemoryType = MemoryType.FACT
    entity: str = Field(..., description="The entity this fact relates to")
    attribute: str = Field(..., description="The attribute of the entity")
    value: Union[str, int, float, bool] = Field(..., description="The value of the attribute")
    source_message_id: Optional[str] = Field(None, description="ID of message this fact was extracted from")
    
    # Updated to Pydantic V2 style validator
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Ensure type is FACT."""
        if v != MemoryType.FACT:
            raise ValueError(f"FactMemoryItem type must be {MemoryType.FACT}")
        return v

    @property
    def content(self) -> str:
        """Generate content string from entity, attribute, and value."""
        return f"{self.entity} {self.attribute}: {self.value}"


class MemorySearchQuery(BaseModel):
    """Model for memory search queries."""
    query: str = Field(..., description="The search query text")
    session_id: Optional[str] = Field(None, description="Optional session ID to filter by")
    user_id: Optional[str] = Field(None, description="Optional user ID to filter by")
    memory_types: List[MemoryType] = Field(default_factory=list, description="Types of memories to search")
    limit: int = Field(10, description="Maximum number of results to return", ge=1)
    recency_weight: float = Field(0.5, description="Weight for recency in ranking (0-1)", ge=0, le=1)
    
    # Updated to Pydantic V2 style configuration
    model_config = ConfigDict(use_enum_values=True) 