# Enhanced Memory Management System - Project Planning

## 1. Project Overview

This document outlines the architecture, design decisions, and implementation plan for enhancing the AI Agent's memory management system. We're developing a hierarchical memory system with short-term, working, and long-term memory components, along with vector database integration for semantic search and automatic summarization capabilities.

## 2. Goals and Objectives

- **Primary Goal**: Create a robust memory management system that enables the agent to maintain context over extended conversations while optimizing for token efficiency and relevance.

- **Key Objectives**:
  - Implement a three-tier memory architecture (short-term, working, long-term)
  - Integrate vector database capabilities for semantic search
  - Develop automatic summarization to prevent context window limitations
  - Ensure memory persistence across sessions
  - Provide a clean API for memory operations

## 3. System Architecture

### 3.1 Memory Hierarchy

#### Short-Term Memory
- **Purpose**: Store recent conversation turns (last 5-10 messages)
- **Implementation**: In-memory cache with complete message content
- **Lifespan**: Maintained during active conversation
- **Usage**: Primary context for immediate responses

#### Working Memory
- **Purpose**: Store important information from the current session
- **Implementation**: Structured key-value store with entity extraction
- **Lifespan**: Maintained during session lifetime
- **Usage**: Contextual information referenced frequently

#### Long-Term Memory
- **Purpose**: Store summarized historical conversations and key facts
- **Implementation**: Vector database with embeddings for semantic search
- **Lifespan**: Persistent across sessions
- **Usage**: Retrieved selectively based on relevance to current query

### 3.2 Vector Database Integration

- **Technology**: Supabase with pgvector extension
- **Schema Design**:
  - `memory_embeddings` table with vector embeddings
  - `memory_metadata` table with associated metadata
  - Indices for efficient similarity search
- **Operations**:
  - Embedding generation for incoming messages
  - Similarity search for relevant context
  - Periodic reindexing for optimization

### 3.3 Summarization System

- **Approach**: Two-level summarization strategy
  - Real-time incremental summarization during conversation
  - Batch summarization for completed conversations
- **Implementation**: 
  - Use LLM to generate concise summaries
  - Extract key entities and facts
  - Store both summaries and structured data

### 3.4 Memory Manager API

- **Core Operations**:
  - `store(message, metadata)`: Store new message in memory
  - `retrieve(query, limit)`: Retrieve relevant context
  - `summarize(messages)`: Generate summary from messages
  - `forget(criteria)`: Selectively remove memories
  - `prioritize(message_id)`: Increase importance of specific memory

## 4. Technical Specifications

### 4.1 Database Schema Extensions

```sql
-- Vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Memory embeddings table
CREATE TABLE memory_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    embedding VECTOR(1536),  -- For OpenAI embeddings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Memory content table
CREATE TABLE memory_content (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    embedding_id UUID REFERENCES memory_embeddings(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL,  -- 'message', 'summary', 'fact'
    metadata JSONB,
    importance FLOAT DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indices
CREATE INDEX idx_memory_embeddings_session ON memory_embeddings(session_id);
CREATE INDEX idx_memory_embeddings_user ON memory_embeddings(user_id);
CREATE INDEX idx_memory_content_type ON memory_content(content_type);
```

### 4.2 Module Structure

```
src/
├── memory/
│   ├── __init__.py
│   ├── manager.py           # Main memory manager interface
│   ├── short_term.py        # Short-term memory implementation
│   ├── working.py           # Working memory implementation
│   ├── long_term.py         # Long-term memory with vector DB
│   ├── summarization.py     # Summarization utilities
│   ├── embedding.py         # Embedding generation utilities
│   └── models.py            # Pydantic models for memory data
├── agent/
│   └── ... (existing files)
└── utils/
    └── ... (existing files)
```

## 5. Implementation Approach

### 5.1 Phase 1: Core Memory System

1. Create database schema extensions
2. Implement memory manager interface
3. Build short-term memory component
4. Integrate with existing agent conversation flow

### 5.2 Phase 2: Vector Search Integration

1. Set up vector database with Supabase pgvector
2. Implement embedding generation for messages
3. Create similarity search functionality
4. Add relevance scoring for retrieved memories

### 5.3 Phase 3: Summarization System

1. Implement incremental summarization
2. Build batch summarization for sessions
3. Create entity extraction for key facts
4. Develop importance scoring for memories

### 5.4 Phase 4: Integration and Optimization

1. Connect memory system to agent's prompt construction
2. Implement memory retrieval strategies
3. Optimize token usage and relevance scoring
4. Add memory cleanup and maintenance utilities

## 6. Testing Strategy

- **Unit Tests**: Test each memory component in isolation
- **Integration Tests**: Test memory system with agent
- **Performance Tests**: Benchmark memory operations
- **Memory Retention Tests**: Verify correct recall over time
- **Token Efficiency Tests**: Measure token usage improvements

## 7. Deployment Considerations

- **Database Migration**: Ensure smooth migration for existing conversations
- **Scaling**: Plan for high-volume memory operations
- **Backup**: Implement memory backup and recovery
- **Privacy**: Add mechanisms for memory expiration and deletion

## 8. Success Metrics

- **Context Quality**: Improvement in contextual relevance of responses
- **Token Efficiency**: Reduction in context tokens used per conversation
- **Conversation Length**: Ability to maintain context over more turns
- **Response Accuracy**: Improvement in factual consistency across a session

## 9. Style Guidelines

- Follow existing project code style (PEP8, type hints)
- Use clear docstrings for all memory components
- Add comments explaining memory retrieval strategies
- Create comprehensive tests for memory operations 