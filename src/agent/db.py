"""
Database utilities for the agent.
"""
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from supabase import Client

async def fetch_conversation_history(supabase: Client, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent conversation history for a session.
    
    Args:
        supabase (Client): The Supabase client.
        session_id (str): The session ID to fetch history for.
        limit (int, optional): Maximum number of messages to retrieve. Defaults to 10.
        
    Returns:
        List[Dict[str, Any]]: The conversation history messages in chronological order.
        
    Raises:
        HTTPException: If there's an error fetching the messages.
    """
    try:
        response = supabase.table("messages") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        # Convert to list and reverse to get chronological order
        messages = response.data[::-1]
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch conversation history: {str(e)}")

async def store_message(supabase: Client, session_id: str, message_type: str, content: str, data: Optional[Dict] = None):
    """Store a message in the Supabase messages table.
    
    Args:
        supabase (Client): The Supabase client.
        session_id (str): The session ID to associate with the message.
        message_type (str): The type of message (e.g., "human" or "ai").
        content (str): The message content.
        data (Optional[Dict], optional): Additional data to store with the message. Defaults to None.
        
    Raises:
        HTTPException: If there's an error storing the message.
    """
    message_obj = {
        "type": message_type,
        "content": content
    }
    if data:
        message_obj["data"] = data

    try:
        supabase.table("messages").insert({
            "session_id": session_id,
            "message": message_obj
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store message: {str(e)}")

async def format_conversation_history(conversation_history: List[Dict]) -> str:
    """Format the conversation history for the agent.
    
    Args:
        conversation_history (List[Dict]): The conversation history messages.
        
    Returns:
        str: Formatted conversation history as a string.
    """
    formatted_history = ""
    
    for msg in conversation_history:
        msg_data = msg["message"]
        role = "Assistant" if msg_data["type"] == "ai" else "User"
        content = msg_data["content"]
        formatted_history += f"{role}: {content}\n\n"
    
    return formatted_history 