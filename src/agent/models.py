"""
Data models for the agent.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class AgentOutput(BaseModel):
    """The structured output from our agent."""
    response: str = Field(description="The response to the user's query")
    confidence: float = Field(description="Confidence level in the response", ge=0, le=1)
    sentiment: Literal["positive", "neutral", "negative"] = Field(description="The sentiment of the response")

class AgentRequest(BaseModel):
    """Request model for agent API."""
    query: str = Field(description="The user's input text")
    user_id: str = Field(description="Unique identifier for the user")
    request_id: str = Field(description="Unique identifier for this request")
    session_id: str = Field(description="Current conversation session ID")

class AgentResponse(BaseModel):
    """Response model for agent API."""
    success: bool = Field(description="Indicates if the request was processed successfully")

class ExtractionTestRequest(BaseModel):
    """Request model for testing extraction functionality."""
    text: str = Field(description="Text to extract information from")

class ExtractionTestResponse(BaseModel):
    """Response model for extraction test endpoint."""
    response: str = Field(description="Extracted response text")
    confidence: float = Field(description="Extracted confidence level")
    sentiment: str = Field(description="Extracted sentiment")
    raw_output: str = Field(description="Original raw output for debugging") 