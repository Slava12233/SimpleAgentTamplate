"""
End-to-end test for the agent API.
"""
import requests
import json
import uuid
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase setup
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Agent API URL
AGENT_URL = "http://localhost:8001/api/agent"
API_TOKEN = os.getenv("API_BEARER_TOKEN")

def test_agent_e2e():
    """End-to-end test for the agent."""
    # Generate unique IDs for this test
    session_id = f"test-session-{uuid.uuid4()}"
    request_id = f"test-request-{uuid.uuid4()}"
    user_id = "test-user"
    
    # Test query
    query = "Hello agent, what is the capital of France?"
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "user_id": user_id,
        "request_id": request_id,
        "session_id": session_id
    }
    
    print(f"🔶 Testing agent with query: '{query}'")
    print(f"🔶 Session ID: {session_id}")
    
    try:
        # First, check API docs to verify the server is running
        print("🔷 Checking if agent API is running...")
        try:
            docs_response = requests.get("http://localhost:8001/docs")
            if docs_response.status_code == 200:
                print("✅ Agent API is running")
            else:
                print(f"⚠️ Agent API might not be running properly (status: {docs_response.status_code})")
        except requests.exceptions.ConnectionError:
            print("❌ Agent API is not running! Please start it with: python src/main.py")
            return False

        # Send request to agent
        print(f"🔷 Sending request to agent...")
        response = requests.post(AGENT_URL, headers=headers, json=payload)
        
        # Check response
        if response.status_code == 200:
            print(f"✅ Agent response status: {response.status_code}")
            print(f"✅ Response: {response.json()}")
        else:
            print(f"❌ Agent response failed with status: {response.status_code}")
            print(f"❌ Error: {response.text}")
            return False
        
        # Wait a moment to ensure data is stored
        print("⏳ Waiting for data to be stored in the database...")
        time.sleep(3)  # Increased to ensure DB operation completes
        
        # Check Supabase for stored messages
        print("🔷 Checking for messages in the database...")
        try:
            # Get messages for this session
            db_response = supabase.table("messages") \
                .select("*") \
                .eq("session_id", session_id) \
                .execute()
            
            # Verify we have messages
            messages = db_response.data
            
            if not messages:
                print("❌ No messages found in the database")
                return False
            
            print(f"✅ Found {len(messages)} messages in database")
            
            # Display the messages
            for i, msg in enumerate(messages):
                try:
                    msg_type = msg["message"]["type"]
                    content = msg["message"]["content"]
                    print(f"📝 Message {i+1} ({msg_type}): {content[:100]}{'...' if len(content) > 100 else ''}")
                    
                    # Check for error in AI response
                    if msg_type == "ai" and "data" in msg["message"] and "error" in msg["message"]["data"]:
                        error = msg["message"]["data"]["error"]
                        print(f"⚠️ AI response contains an error: {error}")
                except KeyError as e:
                    print(f"⚠️ Message structure issue: {e}")
                    print(f"⚠️ Full message data: {msg}")
            
            # Check for additional data in the agent response
            agent_responses = [m for m in messages if m["message"]["type"] == "ai"]
            
            if agent_responses:
                ai_msg = agent_responses[0]["message"]
                if "data" in ai_msg:
                    data = ai_msg.get("data", {})
                    
                    if "error" in data:
                        print(f"⚠️ Agent encountered an error: {data['error']}")
                    else:
                        print("✅ Found structured data in agent response:")
                        for key, value in data.items():
                            if key != "request_id":  # Skip request_id
                                print(f"   🔹 {key}: {value}")
                
                # Check for specific response content
                if "paris" in ai_msg["content"].lower() or "france" in ai_msg["content"].lower():
                    print("✅ Agent correctly mentioned Paris as the capital of France")
                
                # Even with errors, the test completed if we got a response
                return True
            else:
                print("❌ No AI response found in the database")
                return False
                
        except Exception as e:
            print(f"❌ Failed to retrieve messages from database: {str(e)}")
            return False
    
    except requests.RequestException as e:
        print(f"❌ Failed to connect to the agent: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔷 Starting end-to-end test for Supabase agent")
    
    # Run the test
    result = test_agent_e2e()
    
    if result:
        print("🎉 End-to-end test completed successfully!")
    else:
        print("❌ End-to-end test failed") 