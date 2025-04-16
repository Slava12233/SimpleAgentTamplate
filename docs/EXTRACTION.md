# Response Extraction System

This document explains the response extraction system used in the AI agent to parse structured data from LLM outputs.

## Overview

The extraction system is responsible for reliably extracting structured data (response text, confidence, and sentiment) from the raw text output of language models. It uses multiple fallback mechanisms to ensure the most robust parsing possible, even when facing inconsistent output formats.

## Core Functionality

The main extraction function `extract_result_from_str()` in `src/utils/extraction.py` takes a raw text output from the LLM and returns three key pieces of information:

1. **Response Text**: The main content to return to the user
2. **Confidence Score**: A number between 0.0 and 1.0 indicating confidence
3. **Sentiment**: One of "positive", "neutral", or "negative"

## Multi-Level Pattern Matching

The extraction system uses a series of pattern-matching approaches in order of reliability:

### Pattern 1: AgentRunResult Format

Tries to match the standard Pydantic AI AgentRunResult format:

```python
agent_result_match = re.search(r"AgentRunResult\(data=AgentOutput\(response='([^']*)', confidence=([0-9.]+), sentiment='([^']*)'\)\)", result_str)
```

Example input:
```
AgentRunResult(data=AgentOutput(response='The capital of France is Paris.', confidence=0.9, sentiment='positive'))
```

### Pattern 2: Alternative AgentOutput Format

Looks for a more flexible format of response, confidence, and sentiment:

```python
alt_match = re.search(r"response='([^']*)',.*confidence=([0-9.]+),.*sentiment='([^']*)'", result_str)
```

### Pattern 3: JSON-like Structure

Searches for JSON-like key-value pairs:

```python
match = re.search(r'"response"\s*:\s*"([^"]*)"', result_str)
# Also looks for confidence and sentiment in similar formats
```

Example input:
```
{
    "response": "The capital of France is Paris.",
    "confidence": 0.9,
    "sentiment": "positive"
}
```

### Pattern 4: Flexible AgentOutput

Handles variations in AgentOutput format with more flexible pattern matching:

```python
flexible_match = re.search(r"AgentOutput\((.*?)\)", result_str, re.DOTALL)
# Then parses individual attributes from the match
```

### Pattern 5: JSON Object Extraction

Attempts to find and parse any JSON object in the string:

```python
json_match = re.search(r'{.*}', result_str, re.DOTALL)
if json_match:
    data = json.loads(json_match.group(0))
```

### Pattern 6: Sentence Extraction

As a fallback, tries to extract a properly formatted sentence:

```python
sentence_match = re.search(r'([A-Z][^.!?]*[.!?])', result_str)
```

### Raw Text Fallback

If all else fails but there's substantial content, uses cleaned raw text:

```python
cleaned = re.sub(r'final_result|Raw result string:|AgentRunResult|AgentOutput|\(|\)|data=', '', result_str)
```

## Graceful Degradation

If no patterns match, the system provides reasonable defaults:

```python
# Default values if extraction fails
response = "I apologize, but I'm having trouble providing a response at the moment."
confidence = 0.5
sentiment = "neutral"
```

## Testing

The extraction system is thoroughly tested in:

1. **Unit Tests**: `tests/unit/test_extraction.py` tests various input formats
2. **Integration Test**: `tests/integration/test_extraction_endpoint.py` tests the extraction endpoint

Test cases include:
- Standard AgentRunResult format
- JSON format outputs
- Incomplete outputs with partial data
- Malformed outputs
- Plain text outputs

## Endpoint for Testing

The API includes a dedicated endpoint for testing extraction:

```
POST /api/test-extraction
```

With payload:
```json
{
  "text": "Raw model output to extract from"
}
```

This endpoint returns:
```json
{
  "response": "Extracted response text",
  "confidence": 0.9,
  "sentiment": "positive",
  "raw_output": "Original raw output"
}
```

## Future Improvements

Potential enhancements to the extraction system:

1. **LLM-specific Formats**: Add specialized patterns for different LLM providers
2. **Structured JSON Output**: Request JSON output format directly from LLMs
3. **Error Classification**: More detailed error categorization for failed extractions
4. **Dynamic Pattern Learning**: Track which patterns succeed most often and prioritize them 