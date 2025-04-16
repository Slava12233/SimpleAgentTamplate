"""
Main entry point for the AI Agent.
"""
import os
import sys

# Add the parent directory to Python path to fix import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
from src.agent.app import app

if __name__ == "__main__":
    """Run the application with uvicorn when executed directly."""
    print("Starting AI Agent on http://localhost:8001")
    print("Visit http://localhost:8001/docs for API documentation")
    uvicorn.run(app, host="0.0.0.0", port=8001) 