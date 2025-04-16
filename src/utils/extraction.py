"""
Extraction utilities for parsing model responses.
"""
import re
import json

def extract_result_from_str(result_str):
    """Extract the result data from a string representation.
    
    Args:
        result_str (str): The raw string output from the model.
        
    Returns:
        tuple: A tuple containing (response, confidence, sentiment).
    """
    # Default values if extraction fails
    response = "I apologize, but I'm having trouble providing a response at the moment."
    confidence = 0.5
    sentiment = "neutral"
    
    try:
        # Print for debugging
        print(f"Attempting to extract from: {result_str[:200]}...")
        
        # Pattern 1: Check for AgentRunResult format with single quotes
        agent_result_match = re.search(r"AgentRunResult\(data=AgentOutput\(response='([^']*)(?<!\\)', confidence=([0-9.]+), sentiment='([^']*)'\)\)", result_str)
        if agent_result_match:
            response = agent_result_match.group(1)
            confidence = float(agent_result_match.group(2))
            sentiment = agent_result_match.group(3)
            return response, confidence, sentiment
        
        # Pattern 2: Check for AgentRunResult format with double quotes
        agent_result_match_double = re.search(r'AgentRunResult\(data=AgentOutput\(response="(.*?)(?<!\\)", confidence=([0-9.]+), sentiment=\'([^\']*)\'\)\)', result_str, re.DOTALL)
        if agent_result_match_double:
            response = agent_result_match_double.group(1)
            confidence = float(agent_result_match_double.group(2))
            sentiment = agent_result_match_double.group(3)
            return response, confidence, sentiment
        
        # Pattern 3: Extract between response= and confidence=
        response_pattern = re.search(r'response=(?:\'|")(.*?)(?:\'|")(?=,\s*confidence)', result_str, re.DOTALL)
        if response_pattern:
            response = response_pattern.group(1)
            
            # Now get confidence and sentiment
            conf_match = re.search(r'confidence=([0-9.]+)', result_str)
            if conf_match:
                confidence = float(conf_match.group(1))
                
            sentiment_match = re.search(r'sentiment=(?:\'|")(.*?)(?:\'|")', result_str)
            if sentiment_match:
                sentiment = sentiment_match.group(1)
                
            return response, confidence, sentiment
        
        # Pattern 4: Try to find a JSON-like structure in the string as fallback
        match = re.search(r'"response"\s*:\s*"([^"]*)"', result_str)
        if match:
            response = match.group(1)
            
            # Now that we have a response, look for confidence and sentiment in the same format
            conf_match = re.search(r'"confidence"\s*:\s*([\d.]+)', result_str)
            if conf_match:
                confidence = float(conf_match.group(1))
            
            sent_match = re.search(r'"sentiment"\s*:\s*"([^"]*)"', result_str)
            if sent_match:
                sentiment = sent_match.group(1)
                
            # Return early since we have all the data
            return response, confidence, sentiment
        
        # Pattern 5: Try to extract from a more flexible pattern that looks like AgentOutput
        flexible_match = re.search(r"AgentOutput\((.*?)\)", result_str, re.DOTALL)
        if flexible_match:
            output_str = flexible_match.group(1)
            
            # Extract from output string with regex
            response_match = re.search(r'response=[\'"](.+?)["\'](?=\s*\w+=|$)', output_str, re.DOTALL)
            if response_match:
                response = response_match.group(1)
                
            conf_match = re.search(r"confidence=([0-9.]+)", output_str)
            if conf_match:
                confidence = float(conf_match.group(1))
                
            sentiment_match = re.search(r"sentiment=['\"]([^'\"]+)['\"]", output_str)
            if sentiment_match:
                sentiment = sentiment_match.group(1)
                
            if response_match:  # Only return if we at least got a response
                return response, confidence, sentiment
        
        # Pattern 6: Try to extract JSON from the string
        try:
            # Find anything that looks like a JSON object
            json_match = re.search(r'{.*}', result_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    data = json.loads(json_str)
                    if 'response' in data:
                        response = data['response']
                        confidence = data.get('confidence', 0.5)
                        sentiment = data.get('sentiment', 'neutral')
                        return response, confidence, sentiment
                except json.JSONDecodeError:
                    pass  # Continue to other patterns if JSON parsing fails
        except Exception as json_err:
            print(f"Error parsing JSON: {str(json_err)}")
        
        # Pattern 7: If nothing else matched, try to extract the full response from data field
        full_response_match = re.search(r'data=AgentOutput\((.*?)\)', result_str, re.DOTALL)
        if full_response_match:
            data_content = full_response_match.group(1)
            # Extract just the response content
            clean_response = re.sub(r'response=(?:"|\')', '', data_content)
            clean_response = re.sub(r'(?:"|\')\s*confidence.*', '', clean_response)
            if clean_response and len(clean_response) > 10:
                return clean_response, confidence, sentiment
                
        # Pattern 8: If everything else fails, just extract anything between quotes
        quote_match = re.search(r'(?:"|\')([^"\']{20,})(?:"|\')', result_str)
        if quote_match:
            return quote_match.group(1), confidence, sentiment
                
        # If nothing matched but there's some text, use the raw content as a last resort
        if len(result_str) > 10 and "error" not in result_str.lower():
            # Clean up the string - remove common artifacts
            cleaned = re.sub(r'final_result|Raw result string:|AgentRunResult|AgentOutput|\(|\)|data=', '', result_str)
            cleaned = cleaned.strip()
            if len(cleaned) > 10:  # Make sure we have something substantial
                return cleaned[:1000], confidence, sentiment  # Allow longer responses
            
    except Exception as e:
        print(f"Error in extraction: {str(e)}")
    
    return response, confidence, sentiment 