# Conversation Memory Implementation

This document explains how conversation memory is implemented in the AI Agent system.

## Overview

Conversation memory allows the agent to maintain context across multiple turns in a conversation. This enables more natural interactions as the agent can remember previous queries and its own responses, creating a cohesive conversation experience.

## Core Components

The conversation memory system consists of several components:

1. **Database Storage**: Messages are stored in Supabase
2. **Message Retrieval**: Previous messages are fetched for context
3. **Conversation Formatting**: History is formatted for the LLM
4. **System Prompt**: Instructions guide the LLM to use conversation history
5. **Testing**: Verification that memory works correctly

## Database Schema

Conversation memory is stored in the `messages` table with the following structure:

```sql
CREATE TABLE messages (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT NOT NULL,
    message JSONB NOT NULL
);

CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

The `message` JSONB field contains:
- `type`: Either "human" (user message) or "ai" (agent response)
- `content`: The actual message text
- `data`: Additional metadata for AI responses (confidence, sentiment, etc.)

## Message Flow

1. User sends a query with a `session_id`
2. System fetches previous messages for that session:
   ```python
   conversation_history = await fetch_conversation_history(supabase, request.session_id)
   ```
3. History is formatted into a prompt-friendly format:
   ```python
   formatted_history = await format_conversation_history(conversation_history)
   ```
4. User query is stored in the database:
   ```python
   await store_message(supabase, session_id, "human", content=request.query)
   ```
5. Full prompt (history + new query) is sent to the LLM:
   ```python
   prompt = f"{formatted_history}User: {request.query}"
   result = await agent.run(prompt)
   ```
6. Agent response is stored in the database:
   ```python
   await store_message(supabase, session_id, "ai", content=agent_response, data={...})
   ```

## Conversation History Retrieval

The `fetch_conversation_history` function retrieves messages for a session, sorted by creation time:

```python
async def fetch_conversation_history(supabase, session_id, limit=10):
    response = supabase.table("messages") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()
    
    # Convert to list and reverse to get chronological order
    messages = response.data[::-1]
    return messages
```

By default, this retrieves the 10 most recent messages in the conversation.

## Formatting History for the LLM

The `format_conversation_history` function converts raw database messages into a text format for the LLM:

```python
async def format_conversation_history(conversation_history):
    formatted_history = ""
    
    for msg in conversation_history:
        msg_data = msg["message"]
        role = "Assistant" if msg_data["type"] == "ai" else "User"
        content = msg_data["content"]
        formatted_history += f"{role}: {content}\n\n"
    
    return formatted_history
```

This creates a clean format like:
```
User: What's the weather in New York?
Assistant: The weather in New York today is sunny with a high of 75°F.

User: Will I need an umbrella tomorrow?
```

## System Prompt for Memory

The system prompt specifically instructs the LLM to utilize the conversation history:

```
You are a helpful, precise assistant with excellent conversation memory. 
Follow these guidelines:
1. Provide accurate, factual responses based on verified information.
2. Maintain context across the conversation and refer to previous exchanges when relevant.
3. When uncertain, clearly indicate your confidence level rather than guessing.
4. Present information in a structured, easy-to-understand format.
5. Handle summarization requests in two different ways:
   - When asked to LIST topics or for a "NUMBERED LIST": Provide a complete numbered list of ALL topics discussed.
   - When asked to SUMMARIZE or for a "NARRATIVE SUMMARY": Create a cohesive narrative summary that synthesizes the information and adds context, explaining connections between topics.
6. Provide sufficient detail and context in your responses while maintaining clarity.
7. Use formatting like paragraphs and line breaks to enhance readability in longer responses.
8. Do not reference your own limitations or nature as an AI.

Your goal is to be consistently helpful, informative, and engaging while maintaining natural conversation flow.
```

This prompt encourages the model to:
1. Pay attention to previous conversation context
2. Maintain coherence across multiple topics
3. Provide two distinct types of summaries when requested:
   - Numbered lists that comprehensively enumerate all topics
   - Narrative summaries that synthesize information with added context
4. Format responses for enhanced readability

## Testing Memory Functionality

The conversation memory functionality is tested in `tests/integration/test_conversation_memory.py`. This test:

1. Creates a unique conversation session
2. Asks about three different topics in sequence:
   - Weather forecast for New York
   - Recent sci-fi movie recommendations
   - A vegetarian pasta recipe
3. Requests a summary of the entire conversation
4. Verifies that the summary references all three previously discussed topics

Key testing steps include:

```python
# Send multiple queries in sequence with the same session_id
session_id = f"test-memory-{uuid.uuid4()}"

# Topic 1: Weather
send_query_to_agent(session_id, user_id, "What's the weather forecast for tomorrow in New York City?")

# Topic 2: Movies
send_query_to_agent(session_id, user_id, "What are some good sci-fi movies released in the last 5 years?")

# Topic 3: Cooking
send_query_to_agent(session_id, user_id, "Give me a simple pasta recipe that's vegetarian.")

# Request summary
send_query_to_agent(session_id, user_id, "Can you please summarize our entire conversation?")

# Verify topics in summary
summary_response = messages[-1]["message"]["content"].lower()
check_topics = [
    ("weather", "new york"),
    ("sci-fi", "movies"),
    ("pasta", "recipe", "vegetarian")
]
```

The test verifies that each topic is represented in the final summary, confirming that the memory system is correctly maintaining context across multiple conversation turns.

## Performance Considerations

When working with conversation memory, consider:

1. **Token Limits**: Most LLMs have context window limitations. The default limit of 10 messages helps stay within these limits.
2. **Database Performance**: Indexing on `session_id` and `created_at` optimizes query performance.
3. **Response Time**: Fetching conversation history adds a small overhead to each request.

## Future Enhancements

Potential improvements to the conversation memory system:

1. **Memory Summarization**: For very long conversations, implement summary compression to stay within token limits.
2. **Semantic Search**: Add vector embeddings to enable searching for relevant past conversations.
3. **User Profiles**: Maintain persistent facts about users across different sessions.
4. **Memory Controls**: Allow users to explicitly manage what the agent remembers or forgets.