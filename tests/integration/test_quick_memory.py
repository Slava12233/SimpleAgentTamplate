"""
Test for quick memory retention across multiple rapid exchanges.
"""
import requests
import json
import uuid
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

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

# Setup rich console
console = Console()

def send_query_and_get_response(query, session_id, user_id="test-user"):
    """Send a query and get the agent's response.
    
    Args:
        query (str): The query text
        session_id (str): Session identifier
        user_id (str, optional): User identifier. Defaults to "test-user".
        
    Returns:
        str: The agent's response text or None if error
    """
    # Generate a unique request ID
    request_id = f"quick-test-{uuid.uuid4()}"
    
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
    
    try:
        # Send the query
        console.print(f"[bold green]User:[/] {query}")
        response = requests.post(AGENT_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            console.print(f"[bold red]Error: {response.status_code}[/]")
            console.print(response.text)
            return None
        
        # Wait a moment for the response to be stored
        time.sleep(1)
        
        # Get the latest agent response from the database
        db_response = supabase.table("messages") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        
        messages = db_response.data
        if messages and len(messages) > 0:
            message = messages[0]
            if message["message"]["type"] == "ai":
                agent_response = message["message"]["content"]
                # Convert escaped newlines to actual newlines
                agent_response = agent_response.replace('\\n', '\n')
                console.print(f"[bold blue]Agent:[/] {agent_response}")
                return agent_response
        
        return None
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/]")
        return None

def check_agent_running():
    """Check if the agent API is running."""
    try:
        response = requests.get("http://localhost:8001/docs")
        return response.status_code == 200
    except:
        return False

def run_quick_memory_test():
    """Run a test with 5 quick exchanges and final summary."""
    # Check if agent is running
    if not check_agent_running():
        console.print("[bold red]Error: Agent is not running.[/]")
        console.print("Please start the agent with: python src/main.py")
        return False
    
    # Generate a session ID for this test
    session_id = f"quick-test-{uuid.uuid4()}"
    
    console.print(Panel.fit(
        "[bold blue]Quick Memory Test[/]\n"
        "Testing 5 rapid exchanges followed by a summary request\n"
        f"Session ID: {session_id}"
    ))
    
    # Define the test questions - each about a different topic
    test_questions = [
        "What is the tallest mountain in the world?",
        "Who wrote the novel '1984'?",
        "What is the capital of Brazil?",
        "What planet is known as the Red Planet?",
        "Who painted the Mona Lisa?"
    ]
    
    # Wait longer before asking for summary to ensure all messages are processed
    time.sleep(2)
    
    # Summary request
    summary_request = "Please provide a complete numbered list of ALL topics we have discussed in this conversation. Include every single question and answer."
    
    # Send each question in sequence
    responses = []
    for question in test_questions:
        response = send_query_and_get_response(question, session_id)
        if response:
            responses.append(response)
            # Longer pause between questions
            time.sleep(2)
        else:
            console.print("[bold red]Failed to get response. Aborting test.[/]")
            return False
    
    # Request a summary
    console.print("\n[bold yellow]Requesting conversation summary...[/]")
    summary = send_query_and_get_response(summary_request, session_id)
    
    if not summary:
        console.print("[bold red]Failed to get summary. Test incomplete.[/]")
        return False
    
    # Analyze the summary for topic inclusion
    console.print("\n[bold yellow]Analyzing summary for topic inclusion...[/]")
    
    # Keywords to check for each topic
    topic_keywords = [
        ["mountain", "Everest", "tallest", "highest"],
        ["1984", "Orwell", "novel", "wrote", "author"],
        ["Brazil", "Brasília", "capital"],
        ["Mars", "planet", "Red Planet"],
        ["Mona Lisa", "painting", "Leonardo", "da Vinci"]
    ]
    
    # Check if each topic is mentioned in the summary
    summary_lower = summary.lower()
    topic_included = [False] * len(topic_keywords)
    
    for i, keywords in enumerate(topic_keywords):
        topic_included[i] = any(keyword.lower() in summary_lower for keyword in keywords)
    
    # Display results
    console.print("\n[bold yellow]Test Results:[/]")
    all_topics_included = all(topic_included)
    
    for i, (included, question) in enumerate(zip(topic_included, test_questions)):
        status = "[green]✓" if included else "[red]✗"
        console.print(f"{status} Topic {i+1}: {question}[/]")
    
    if all_topics_included:
        console.print("\n[bold green]✅ SUCCESS: All topics were included in the summary![/]")
    else:
        console.print("\n[bold yellow]⚠️ PARTIAL: Some topics were missing from the summary[/]")
        missing_count = topic_included.count(False)
        console.print(f"   {missing_count} out of {len(topic_included)} topics were missing")
    
    return all_topics_included

if __name__ == "__main__":
    print("🔷 Starting Quick Memory Test")
    
    # Run the test
    result = run_quick_memory_test()
    
    if result:
        print("🎉 Quick Memory Test completed successfully!")
    else:
        print("❌ Quick Memory Test did not meet all success criteria") 