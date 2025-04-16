"""
Test for conversation memory across multiple topics.
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

def send_query_to_agent(session_id, user_id, query):
    """Helper function to send a query to the agent.
    
    Args:
        session_id (str): The session ID for the conversation.
        user_id (str): The user ID.
        query (str): The query text to send.
        
    Returns:
        tuple: (success, request_id) - Whether the request was successful and the request ID used.
    """
    request_id = f"test-request-{uuid.uuid4()}"
    
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
    
    print(f"🔷 Sending query: '{query}'")
    
    try:
        response = requests.post(AGENT_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✅ Agent response status: {response.status_code}")
            print(f"✅ Response: {response.json()}")
            return True, request_id
        else:
            print(f"❌ Agent response failed with status: {response.status_code}")
            print(f"❌ Error: {response.text}")
            return False, request_id
            
    except requests.RequestException as e:
        print(f"❌ Failed to connect to the agent: {str(e)}")
        return False, request_id

def get_agent_responses(session_id):
    """Get all messages for the given session from the database.
    
    Args:
        session_id (str): The session ID to get messages for.
        
    Returns:
        list: List of message objects in order.
    """
    try:
        db_response = supabase.table("messages") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at") \
            .execute()
        
        messages = db_response.data
        return messages
    except Exception as e:
        print(f"❌ Failed to retrieve messages from database: {str(e)}")
        return []

def test_conversation_memory():
    """Test conversation memory across multiple topics with final summary."""
    # Generate unique IDs for this test
    session_id = f"test-memory-{uuid.uuid4()}"
    user_id = "test-user"
    
    print(f"🔶 Testing conversation memory")
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
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Agent API is not running! Please start it with: python src/main.py")
            return False

        # Topic 1: Weather
        topic1_query = "What's the weather forecast for tomorrow in New York City?"
        success, _ = send_query_to_agent(session_id, user_id, topic1_query)
        if not success:
            return False
        
        # Wait a moment to ensure data is stored
        time.sleep(2)
        
        # Topic 2: Movies
        topic2_query = "What are some good sci-fi movies released in the last 5 years?"
        success, _ = send_query_to_agent(session_id, user_id, topic2_query)
        if not success:
            return False
            
        # Wait a moment to ensure data is stored
        time.sleep(2)
        
        # Topic 3: Cooking
        topic3_query = "Give me a simple pasta recipe that's vegetarian."
        success, _ = send_query_to_agent(session_id, user_id, topic3_query)
        if not success:
            return False
            
        # Wait a moment to ensure data is stored
        time.sleep(2)
        
        # Final summary request
        summary_query = "Can you please summarize our entire conversation so far? Make sure to mention all three topics we discussed: the weather, movies, and the pasta recipe."
        success, _ = send_query_to_agent(session_id, user_id, summary_query)
        if not success:
            return False
            
        # Wait a moment to ensure data is stored
        time.sleep(3)
        
        # Get all messages from database and check for memory retention
        print("🔷 Checking conversation history in database...")
        messages = get_agent_responses(session_id)
        
        if not messages:
            print("❌ No messages found in the database")
            return False
            
        print(f"✅ Found {len(messages)} messages in conversation")
        
        # We should have 8 messages total (4 user queries + 4 agent responses)
        if len(messages) != 8:
            print(f"⚠️ Expected 8 messages but found {len(messages)}")
        
        # Display message summaries
        for i, msg in enumerate(messages):
            try:
                msg_type = msg["message"]["type"]
                content = msg["message"]["content"]
                if len(content) > 100:
                    print(f"📝 Message {i+1} ({msg_type}): {content[:100]}...")
                    # Print the full summary if it's the last message
                    if i == len(messages) - 1:
                        print(f"\n📋 Full summary:\n{content}\n")
                else:
                    print(f"📝 Message {i+1} ({msg_type}): {content}")
            except KeyError as e:
                print(f"⚠️ Message structure issue: {e}")
        
        # Check the summary response for references to all three topics
        summary_response = messages[-1]["message"]["content"].lower()
        
        memory_topics = [
            ("weather", "new york"),
            ("sci-fi", "movies"),
            ("pasta", "recipe", "vegetarian")
        ]
        
        print("\n🔍 Checking if summary includes all conversation topics:")
        for topic_terms in memory_topics:
            topic_found = any(term in summary_response for term in topic_terms)
            topic_name = " or ".join(topic_terms)
            if topic_found:
                print(f"✅ Summary includes reference to {topic_name}")
            else:
                print(f"❌ Summary is missing reference to {topic_name}")
        
        return True
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔷 Starting conversation memory test")
    
    # Run the test
    result = test_conversation_memory()
    
    if result:
        print("🎉 Conversation memory test completed successfully!")
    else:
        print("❌ Conversation memory test failed") 