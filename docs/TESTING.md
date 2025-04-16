# Testing Framework

This document explains the testing setup and methodology used in the AI Agent project.

## Overview

The project uses a comprehensive testing strategy with both unit tests and integration tests to verify functionality across all system components. The testing framework is built using pytest and focuses on ensuring that each component works correctly in isolation and together as a system.

## Test Structure

Tests are organized into three main categories:

1. **Unit Tests**: Test individual functions and components in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test the entire system from user request to response

## Test Directory Structure

```
tests/
├── unit/                 # Unit tests
│   ├── __init__.py
│   └── test_extraction.py
├── integration/          # Integration tests
│   ├── __init__.py
│   ├── test_agent_e2e.py
│   ├── test_conversation_memory.py
│   └── test_extraction_endpoint.py
└── __init__.py
```

## Unit Tests

Unit tests verify that individual components function correctly in isolation. Current unit tests include:

### test_extraction.py

Tests the extraction utility with various input formats:

- `test_extract_agent_run_result()`: Tests extraction from the standard AgentRunResult format
- `test_extract_result_from_json()`: Tests extraction from JSON format strings
- `test_extract_result_from_str_incomplete()`: Tests extraction with incomplete data
- `test_extract_result_from_str_malformed()`: Tests extraction with malformed data
- `test_extract_from_text_with_paris_mention()`: Tests extraction from plain text responses

## Integration Tests

Integration tests verify that components work together correctly. Current integration tests include:

### test_agent_e2e.py

Tests the end-to-end flow of the agent API:

1. Generates a unique session and request ID
2. Sends a query to the agent API
3. Verifies successful response from the API
4. Checks that messages are stored correctly in the database
5. Verifies the response content is relevant to the query

### test_extraction_endpoint.py

Tests the extraction test endpoint:

1. Sends various test input formats to the extraction endpoint
2. Verifies that the endpoint correctly extracts structured data
3. Checks that different patterns are correctly matched

### test_conversation_memory.py

Tests the conversation memory across multiple turns:

1. Creates a unique conversation session
2. Sends multiple queries about different topics
3. Requests a conversation summary
4. Verifies that the summary includes references to all topics
5. Checks the complete conversation history in the database

## Running Tests

The project includes a centralized test runner script (`run_tests.py`) that provides several options for executing tests:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit-only

# Run only integration tests
python run_tests.py --integration-only

# Run a specific test file
python tests/integration/test_conversation_memory.py
```

## Test Requirements

Integration tests require:

1. A running instance of the agent API
2. Valid Supabase credentials in the `.env` file
3. Valid API bearer token

## Mock vs. Real Dependencies

- **Unit Tests**: Use mocked dependencies for isolation
- **Integration Tests**: Use real Supabase instance and actual API calls

## Testing Best Practices

When adding new features, follow these testing guidelines:

1. **Test Coverage**: Add unit tests for all new functions
2. **Edge Cases**: Test both happy paths and failure cases
3. **Independence**: Tests should not depend on the results of other tests
4. **Cleanup**: Tests should clean up after themselves (especially in the database)
5. **Documentation**: Clearly document the purpose of each test function

## Continuous Improvement

Areas for test improvement:

1. **Mocking**: Add more mocked dependencies to speed up tests
2. **Coverage**: Increase test coverage for edge cases
3. **Performance**: Add performance benchmarks for critical paths
4. **Load Testing**: Add tests for high concurrency scenarios 