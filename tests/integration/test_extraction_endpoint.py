"""
Test for the extraction endpoint.
"""
import requests
import json

# Agent API URL
EXTRACTION_URL = "http://localhost:8001/api/test-extraction"

def test_extraction_endpoint():
    """Test the extraction endpoint with various formats."""
    test_cases = [
        {
            "name": "AgentRunResult format",
            "text": "Raw result string: AgentRunResult(data=AgentOutput(response='The capital of France is Paris.', confidence=0.9, sentiment='positive'))"
        },
        {
            "name": "JSON format",
            "text": '''
            final_result
            {
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
            '''
        },
        {
            "name": "Plain text with Paris",
            "text": "The capital of France is Paris. It's a beautiful city."
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔶 Testing extraction with {test_case['name']}")
        
        # Prepare request
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": test_case["text"]
        }
        
        # Send request to test endpoint
        try:
            response = requests.post(EXTRACTION_URL, headers=headers, json=payload)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response status: {response.status_code}")
                print(f"✅ Extracted response: {result['response']}")
                print(f"✅ Confidence: {result['confidence']}")
                print(f"✅ Sentiment: {result['sentiment']}")
                
                # Verify the result contains expected text
                if "paris" in result['response'].lower():
                    print("✅ Test passed: Response contains 'Paris'")
                else:
                    print("❌ Test failed: Response doesn't contain 'Paris'")
                    return False
            else:
                print(f"❌ Request failed with status: {response.status_code}")
                print(f"❌ Error: {response.text}")
                return False
        except requests.RequestException as e:
            print(f"❌ Failed to connect to the endpoint: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🔷 Starting extraction endpoint test")
    
    # Check if agent is running
    try:
        response = requests.get("http://localhost:8001/docs")
        if response.status_code == 200:
            print("✅ Agent is running")
        else:
            print("❌ Agent might not be running properly")
    except requests.exceptions.ConnectionError:
        print("❌ Agent is not running! Please start it with: python src/main.py")
        exit(1)
    
    # Run the tests
    result = test_extraction_endpoint()
    
    if result:
        print("\n🎉 Extraction endpoint tests completed successfully!")
    else:
        print("\n❌ Extraction endpoint tests failed!") 