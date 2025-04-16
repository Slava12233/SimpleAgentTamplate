"""
Unit tests for the extraction utilities.
"""
import pytest
from src.utils.extraction import extract_result_from_str

def test_extract_agent_run_result():
    """Test extraction from AgentRunResult format."""
    test_string = "Raw result string: AgentRunResult(data=AgentOutput(response='The capital of France is Paris.', confidence=0.9, sentiment='positive'))"
    
    response, confidence, sentiment = extract_result_from_str(test_string)
    
    assert response == "The capital of France is Paris."
    assert confidence == 0.9
    assert sentiment == "positive"

def test_extract_result_from_json():
    """Test the extraction of results from the JSON format string."""
    # Test case based on actual output format
    test_string = '''
    Span
    took
    1.02s
    at
    Apr 16 01:04:53 AM
    Generation
    Details
    Raw Data
    Pretty
    JSON
    user
    User: Hello agent, what is the capital of France?

    A:

    assistant
    Tool calls
    final_result
    {
    3 items
    "response"
    : 
    "The capital of France is Paris."
    ,
    "confidence"
    : 
    0.9
    ,
    "sentiment"
    : 
    "positive"
    ,
    }
    tool
    final_result
    Final result processed.
    '''
    
    response, confidence, sentiment = extract_result_from_str(test_string)
    
    assert response == "The capital of France is Paris."
    assert confidence == 0.9
    assert sentiment == "positive"

def test_extract_result_from_str_incomplete():
    """Test the extraction with incomplete data."""
    test_string = """
    final_result
    {
    "response"
    : 
    "This is a test response."
    }
    """
    
    response, confidence, sentiment = extract_result_from_str(test_string)
    
    assert response == "This is a test response."
    assert confidence == 0.5  # Default value
    assert sentiment == "neutral"  # Default value

def test_extract_result_from_str_malformed():
    """Test the extraction with malformed data."""
    test_string = "This doesn't contain any valid data structure"
    
    response, confidence, sentiment = extract_result_from_str(test_string)
    
    # Should use default values
    assert response == "I apologize, but I'm having trouble providing a response at the moment."
    assert confidence == 0.5
    assert sentiment == "neutral"

def test_extract_from_text_with_paris_mention():
    """Test extracting from text that mentions Paris as capital."""
    test_string = "Hello! The capital of France is Paris. It's a beautiful city."
    
    response, confidence, sentiment = extract_result_from_str(test_string)
    
    assert "capital of France is Paris" in response
    assert confidence == 0.9
    assert sentiment == "positive" 