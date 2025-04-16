# AI Agent with Pydantic AI and Supabase Integration

A production-ready conversational AI agent with memory, structured outputs, and database integration.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Setup and Installation](#setup-and-installation)
5. [Components](#components)
   - [Agent Module](#agent-module)
   - [Database Integration](#database-integration)
   - [Memory System](#memory-system)
   - [Extraction Utilities](#extraction-utilities)
   - [Authentication](#authentication)
   - [API Endpoints](#api-endpoints)
6. [Testing](#testing)
   - [Unit Tests](#unit-tests)
   - [Integration Tests](#integration-tests)
   - [Conversation Memory Test](#conversation-memory-test)
7. [Deployment](#deployment)
8. [API Reference](#api-reference)
9. [Environment Variables](#environment-variables)
10. [Contributing](#contributing)
11. [License](#license)

## Overview

This project provides a robust framework for building AI-powered conversational agents with memory capabilities. The agent uses large language models via Pydantic AI to generate structured outputs, stores conversation history in Supabase, and provides REST API endpoints for integration with various applications.

## Features

- 💬 **Conversational Memory**: Maintains context across multiple conversation turns
- 🧠 **Multi-Level Memory System**: Hierarchical memory with short-term, working, and long-term components
- 🔢 **Structured Outputs**: Uses Pydantic models for type-safe structured responses
- 📊 **Database Integration**: Stores conversation history in Supabase
- 🔒 **API Authentication**: Secures endpoints with API token verification
- 📚 **Comprehensive Testing**: Unit and integration tests with memory verification
- 📝 **Documentation**: API documentation with OpenAPI/Swagger
- 🐳 **Containerization**: Docker support for easy deployment

## Architecture

The system follows a layered architecture:

1. **API Layer**: FastAPI application that exposes endpoints and handles HTTP requests
2. **Agent Layer**: Core logic for processing user queries using Pydantic AI
3. **Memory Layer**: Hierarchical memory system for context management
4. **Database Layer**: Supabase integration for storing and retrieving conversation history
5. **Utilities Layer**: Helper functions for extraction and formatting

The conversation flow works as follows:

1. User sends a query to the `/api/agent` endpoint
2. The system retrieves previous conversation history for the session
3. The memory system combines short-term, working, and long-term memories 
4. The prompt is constructed with history + new query
5. The LLM generates a structured response
6. Response is extracted and stored in the database and memory system
7. Response is sent back to the user

For detailed documentation on specific components, see:
- [Conversation Memory System](docs/CONVERSATION_MEMORY.md)
- [Enhanced Memory Architecture](docs/ENHANCED_MEMORY.md)
- [Response Extraction System](docs/EXTRACTION.md)
- [Testing Framework](docs/TESTING.md)
- [Command Line Interface](docs/CLI.md)

## Setup and Installation

### Prerequisites

- Python 3.11 or higher
- Supabase account with a project
- OpenAI API key (or other LLM provider supported by Pydantic AI)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-agent
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:

```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Create the database tables in Supabase:

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

### Running the Agent

Start the agent with:

```bash
python src/main.py
```

The agent will be available at:
- API Endpoint: http://localhost:8001/api/agent
- API Documentation: http://localhost:8001/docs
- Memory Statistics: http://localhost:8001/memory-stats

### Using the CLI

You can interact with the agent directly from the command line:

```bash
# Interactive mode
python cli.py

# Single query mode
python cli.py --query "What's the weather like in New York?"

# Continue a previous session
python cli.py --session "your-session-id"

# Show memory statistics
python cli.py --session "your-session-id" --memory

# Clear session memory
python cli.py --session "your-session-id" --clear
```

The CLI provides:
- Interactive chat with the agent
- Conversation memory across messages
- Memory inspection and management
- Markdown formatting for responses
- Command history

## Components

### Agent Module

The agent module (`src/agent/`) is the core of the system and contains several key components:

#### app.py

The main FastAPI application that:
- Initializes the Pydantic AI agent with the system prompt
- Provides the `/api/agent` endpoint for processing queries
- Manages conversation history retrieval and storage
- Handles error cases and logging

**Key Functions:**
- `process_agent_request()`: Main endpoint handler for agent requests
- Detailed logging and error handling

#### models.py

Defines Pydantic models for request/response handling:

- `AgentOutput`: Structured output from the LLM with response, confidence, and sentiment
- `AgentRequest`: Request model with query, user_id, request_id, and session_id
- `AgentResponse`: Response model with success status
- `ExtractionTestRequest/Response`: Models for the extraction test endpoint

#### db.py

Database utilities for Supabase integration:

- `fetch_conversation_history()`: Retrieves previous messages for a session
- `store_message()`: Stores new messages in the database
- `format_conversation_history()`: Formats conversation history for the LLM prompt

#### auth.py

Authentication utilities:

- `verify_token()`: Verifies the API bearer token against environment variable

### Memory System

The memory system (`src/memory/`) implements a hierarchical approach to memory management:

#### manager.py

The main memory manager that coordinates between memory components:

- `store_message()`: Stores messages in memory
- `get_conversation_history()`: Retrieves messages from memory
- `get_formatted_history()`: Formats memory for prompt construction

#### models.py

Pydantic models for memory objects:

- `MemoryItem`: Base model for all memory items
- `MessageMemoryItem`: Model for conversation messages
- `SummaryMemoryItem`: Model for conversation summaries
- `FactMemoryItem`: Model for extracted facts

#### short_term.py

Short-term memory implementation:

- Uses a FIFO queue for recent messages
- Provides persistence between restarts
- Optimized for quick access to recent context

#### config.py

Configuration for the memory system:

- Memory size limits and thresholds
- Persistence settings
- Integration points with environment variables

### Extraction Utilities

The `src/utils/extraction.py` file contains utilities for parsing LLM responses:

- `extract_result_from_str()`: Uses multiple pattern matching strategies to extract structured data from model outputs
- Handles various output formats with graceful degradation

### Database Integration

The system uses Supabase as its database with a `messages` table structure:

- `id`: UUID primary key
- `created_at`: Timestamp
- `session_id`: Session identifier
- `message`: JSONB object containing message data
  - `type`: "human" or "ai"
  - `content`: Message text
  - `data`: Additional structured data (for AI responses)

### API Endpoints

- `POST /api/agent`: Main endpoint for processing agent requests
- `POST /api/test-extraction`: Test endpoint for extraction utilities
- `GET /memory-stats`: Get statistics about stored memories
- `POST /memory/clear/{session_id}`: Clear memory for a specific session
- `GET /`: Root endpoint with API information

## Testing

The project includes comprehensive test coverage:

### Unit Tests

Located in `tests/unit/`, these test individual components:

- `test_extraction.py`: Tests the extraction utility with various input formats
- `test_short_term_memory.py`: Tests the short-term memory component
- `test_memory_manager.py`: Tests the memory manager functionality

### Integration Tests

Located in `tests/integration/`, these test system components together:

- `test_agent_e2e.py`: End-to-end test for the agent API
- `test_extraction_endpoint.py`: Tests the extraction endpoint
- `test_conversation_memory.py`: Tests multi-turn conversation memory
- `test_quick_memory.py`: Rapid multi-topic conversation test with summary

### Conversation Memory Test

The conversation memory test (`test_conversation_memory.py`) verifies the agent's ability to maintain context across multiple turns:

1. Asks about weather in New York
2. Asks about sci-fi movies
3. Asks for a vegetarian pasta recipe
4. Requests a conversation summary
5. Verifies the summary includes all three topics

To run the tests:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit-only

# Run only integration tests
python run_tests.py --integration-only 

# Run a specific test
python tests/integration/test_conversation_memory.py
```

## Deployment

The project includes Docker support for containerized deployment:

```bash
# Build the Docker image
docker build -t ai-agent .

# Run the container
docker run -p 8001:8001 --env-file .env ai-agent
```

## API Reference

### POST /api/agent

Process a user query through the agent.

**Request:**

```json
{
  "query": "What's the weather like?",
  "user_id": "user-123",
  "request_id": "req-456",
  "session_id": "session-789"
}
```

**Response:**

```json
{
  "success": true
}
```

**Headers:**

- `Authorization: Bearer <API_TOKEN>`

### POST /api/test-extraction

Test the extraction functionality.

**Request:**

```json
{
  "text": "Raw result string with response data"
}
```

**Response:**

```json
{
  "response": "Extracted response text",
  "confidence": 0.9,
  "sentiment": "positive",
  "raw_output": "Original raw output"
}
```

### GET /memory-stats

Get memory statistics.

**Query Parameters:**
- `session_id` (optional): Filter by session ID

**Response:**
```json
{
  "total_messages": 15,
  "session_count": 3,
  "sessions": ["session-1", "session-2", "session-3"]
}
```

## Environment Variables

Required environment variables are documented in `.env.example`:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase service key
- `API_BEARER_TOKEN`: The token for API authorization
- `OPENAI_API_KEY`: Your OpenAI API key
- `PYDANTIC_AI_MODEL`: The model to use (default: 'openai:gpt-4o')
- `MEMORY_PERSISTENCE_DIR`: Directory to store memory persistence files
- `MEMORY_SHORT_TERM_SIZE`: Maximum number of items in short-term memory
- `MEMORY_PERSISTENCE_ENABLED`: Enable/disable memory persistence

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.