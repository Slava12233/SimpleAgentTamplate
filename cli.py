#!/usr/bin/env python
"""
CLI interface for interacting with the AI Agent.
"""
import os
import sys
import uuid
import argparse
import requests
import dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
dotenv.load_dotenv()

# Setup console for pretty printing
console = Console()

# Constants
API_URL = "http://localhost:8001/api/agent"
API_TOKEN = os.getenv("API_BEARER_TOKEN")
DEFAULT_USER_ID = "cli-user"

def send_query(query, session_id, user_id=DEFAULT_USER_ID):
    """Send a query to the agent API.
    
    Args:
        query (str): The query text
        session_id (str): Session identifier
        user_id (str, optional): User identifier. Defaults to DEFAULT_USER_ID.
        
    Returns:
        bool: Whether the request was successful
    """
    # Generate a unique request ID
    request_id = f"cli-request-{uuid.uuid4()}"
    
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
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return True
        else:
            console.print(f"[bold red]Error: {response.status_code}[/]")
            console.print(response.text)
            return False
    except requests.RequestException as e:
        console.print(f"[bold red]Connection error: {str(e)}[/]")
        return False

def get_agent_response(session_id):
    """Get the latest agent response for a session.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        str: The agent's response, or None if not found
    """
    try:
        # Access Supabase directly using environment variables
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            console.print("[bold red]Error: Missing Supabase credentials in .env file[/]")
            return None
        
        # Using the REST API directly for simplicity
        url = f"{supabase_url}/rest/v1/messages"
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        params = {
            "session_id": f"eq.{session_id}",
            "order": "created_at.desc",
            "limit": "1"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            messages = response.json()
            if messages and len(messages) > 0:
                message = messages[0]
                if message["message"]["type"] == "ai":
                    return message["message"]["content"]
        
        return None
    except Exception as e:
        console.print(f"[bold red]Error retrieving response: {str(e)}[/]")
        return None

def check_agent_running():
    """Check if the agent API is running."""
    try:
        response = requests.get("http://localhost:8001/docs")
        return response.status_code == 200
    except:
        return False

def interactive_session():
    """Start an interactive session with the agent."""
    # Check if agent is running
    if not check_agent_running():
        console.print("[bold red]Error: Agent is not running.[/]")
        console.print("Please start the agent with: python src/main.py")
        return
    
    # Generate a session ID for this conversation
    session_id = f"cli-session-{uuid.uuid4()}"
    
    console.print(Panel.fit(
        "[bold blue]AI Agent CLI[/]\n"
        "Type your messages to chat with the agent.\n"
        "Type [bold]'exit'[/] or [bold]'quit'[/] to end the session.\n"
        f"Session ID: {session_id}"
    ))
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = console.input("[bold green]You:[/] ")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'q']:
            console.print("[bold blue]Exiting session. Goodbye![/]")
            break
        
        # Send the query
        console.print("[bold yellow]Sending query...[/]")
        if send_query(user_input, session_id):
            # Wait for response
            console.print("[bold yellow]Waiting for response...[/]")
            
            # Get the agent's response
            response = get_agent_response(session_id)
            
            if response:
                # Display the response
                console.print("[bold blue]Agent:[/]")
                # Convert escaped newlines to actual newlines
                formatted_response = response.replace('\\n', '\n')
                console.print(Markdown(formatted_response))
            else:
                console.print("[bold red]No response received from agent.[/]")
        else:
            console.print("[bold red]Failed to send query.[/]")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="CLI for interacting with the AI Agent")
    parser.add_argument("--session", "-s", help="Use a specific session ID")
    parser.add_argument("--query", "-q", help="Single query mode (non-interactive)")
    args = parser.parse_args()
    
    if args.query:
        # Single query mode
        session_id = args.session or f"cli-session-{uuid.uuid4()}"
        console.print(f"[bold blue]Session ID:[/] {session_id}")
        console.print(f"[bold green]Query:[/] {args.query}")
        
        if send_query(args.query, session_id):
            response = get_agent_response(session_id)
            if response:
                console.print("[bold blue]Agent:[/]")
                console.print(Markdown(response))
            else:
                console.print("[bold red]No response received.[/]")
    else:
        # Interactive mode
        interactive_session()

if __name__ == "__main__":
    main() 