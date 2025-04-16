"""
Main FastAPI application for the agent.
"""
import os
import logfire
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic_ai import Agent

from src.agent.models import (
    AgentOutput, 
    AgentRequest, 
    AgentResponse, 
    ExtractionTestRequest, 
    ExtractionTestResponse
)
from src.agent.auth import verify_token, security
from src.agent.db import fetch_conversation_history, store_message, format_conversation_history
from src.utils.extraction import extract_result_from_str

# Load environment variables using dotenv
from dotenv import load_dotenv
load_dotenv()

# Initialize Logfire for monitoring
logfire.configure(send_to_logfire='if-token-present')

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent API",
    description="API for AI-powered conversational agent",
    version="1.0.0"
)

# Supabase setup
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Pydantic AI agent
model_name = os.getenv('PYDANTIC_AI_MODEL', 'openai:gpt-3.5-turbo')
print(f'Using model: {model_name}')

# Define the system prompt once
SYSTEM_PROMPT = (
    'You are a helpful, precise assistant with excellent conversation memory. '
    'Follow these guidelines:\n'
    '1. Provide accurate, factual responses based on verified information.\n'
    '2. Maintain context across the conversation and refer to previous exchanges when relevant.\n'
    '3. When uncertain, clearly indicate your confidence level rather than guessing.\n'
    '4. Present information in a structured, easy-to-understand format.\n'
    '5. Handle summarization requests in two different ways:\n'
    '   - When asked to LIST topics or for a "NUMBERED LIST": Provide a complete numbered list of ALL topics discussed.\n'
    '   - When asked to SUMMARIZE or for a "NARRATIVE SUMMARY": Create a cohesive narrative summary that synthesizes the information and adds context, explaining connections between topics.\n'
    '6. Provide sufficient detail and context in your responses while maintaining clarity.\n'
    '7. Use formatting like paragraphs and line breaks to enhance readability in longer responses.\n'
    '8. Do not reference your own limitations or nature as an AI.\n\n'
    'Your goal is to be consistently helpful, informative, and engaging while maintaining natural conversation flow.'
)

# Check Pydantic AI version and use appropriate parameter
import pkg_resources
import re

try:
    pydantic_ai_version = pkg_resources.get_distribution("pydantic-ai").version
    print(f"Detected Pydantic AI version: {pydantic_ai_version}")
    
    # Extract major.minor version numbers
    version_match = re.match(r"(\d+)\.(\d+)", pydantic_ai_version)
    if version_match:
        major, minor = map(int, version_match.groups())
        
        # Determine which parameter to use based on version
        if major == 0 and minor < 2:
            # Older versions used result_type
            agent = Agent(
                model_name,
                result_type=AgentOutput,
                system_prompt=SYSTEM_PROMPT,
                instrument=True,
            )
            print("Initialized agent with result_type")
        else:
            # Newer versions use output_type
            agent = Agent(
                model_name,
                output_type=AgentOutput,
                system_prompt=SYSTEM_PROMPT,
                instrument=True,
            )
            print("Initialized agent with output_type")
    else:
        # If version parsing fails, try result_type first
        try:
            agent = Agent(
                model_name,
                result_type=AgentOutput,
                system_prompt=SYSTEM_PROMPT,
                instrument=True,
            )
            print("Initialized agent with result_type")
        except TypeError:
            agent = Agent(
                model_name,
                output_type=AgentOutput,
                system_prompt=SYSTEM_PROMPT,
                instrument=True,
            )
            print("Initialized agent with output_type")
except (pkg_resources.DistributionNotFound, Exception) as e:
    print(f"Error determining Pydantic AI version: {str(e)}")
    # Fallback to try-except approach
    try:
        agent = Agent(
            model_name,
            result_type=AgentOutput,
            system_prompt=SYSTEM_PROMPT,
            instrument=True,
        )
        print("Initialized agent with result_type")
    except TypeError as e:
        if "unexpected keyword argument 'result_type'" in str(e):
            agent = Agent(
                model_name,
                output_type=AgentOutput,
                system_prompt=SYSTEM_PROMPT,
                instrument=True,
            )
            print("Initialized agent with output_type")
        else:
            raise e

@app.post("/api/agent", response_model=AgentResponse, tags=["Agent"])
async def process_agent_request(
    request: AgentRequest,
    authenticated: bool = Depends(verify_token)
):
    """Process an agent request.
    
    Args:
        request (AgentRequest): The request data.
        authenticated (bool): Authentication check (handled by dependency).
        
    Returns:
        AgentResponse: Success status of the request.
    """
    try:
        # Fetch conversation history from the DB
        conversation_history = await fetch_conversation_history(supabase, request.session_id)
        
        # Format conversation history for the agent
        formatted_history = await format_conversation_history(conversation_history)
        
        # Store user's query
        await store_message(
            supabase,
            session_id=request.session_id,
            message_type="human",
            content=request.query
        )            

        # Create prompt with history and user query
        prompt = f"{formatted_history}User: {request.query}"
        
        # Get response from Pydantic AI agent
        try:
            print(f"Sending prompt to agent: {prompt}")
            result = await agent.run(prompt)
            
            # Print the result as a string for debugging
            result_str = str(result)
            print(f"Raw result string: {result_str}")
            
            # For debugging, print the type and representation
            print(f"Result type: {type(result)}")
            print(f"Result repr: {repr(result)}")
            
            if hasattr(result, 'data'):
                print(f"Result has data attribute: {result.data}")
            
            # Direct access attempt
            try:
                direct_response = getattr(result, 'response', None) or getattr(result, 'data.response', None)
                if direct_response:
                    print(f"Direct response access: {direct_response}")
            except Exception as direct_err:
                print(f"Direct access error: {str(direct_err)}")
            
            # Extract response data using direct string manipulation as a fallback
            agent_response, confidence, sentiment = extract_result_from_str(result_str)
            
            print(f"Extracted response: {agent_response}")
            print(f"Extracted confidence: {confidence}")
            print(f"Extracted sentiment: {sentiment}")
            
        except Exception as e:
            print(f"Error running agent: {str(e)}")
            # Use a fallback response
            agent_response = "I apologize, but I encountered an error processing your request."
            confidence = 0.5
            sentiment = "neutral"

        # Store agent's response with additional structured data
        await store_message(
            supabase,
            session_id=request.session_id,
            message_type="ai",
            content=agent_response,
            data={
                "request_id": request.request_id,
                "confidence": confidence,
                "sentiment": sentiment
            }
        )

        return AgentResponse(success=True)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        # Store error message in conversation
        await store_message(
            supabase,
            session_id=request.session_id,
            message_type="ai",
            content="I apologize, but I encountered an error processing your request.",
            data={"error": str(e), "request_id": request.request_id}
        )
        return AgentResponse(success=False)

@app.post("/api/test-extraction", response_model=ExtractionTestResponse, tags=["Testing"])
async def test_extraction(request: ExtractionTestRequest):
    """Test endpoint to check extraction functions.
    
    Args:
        request (ExtractionTestRequest): Test input.
        
    Returns:
        ExtractionTestResponse: Extraction results.
    """
    try:
        response, confidence, sentiment = extract_result_from_str(request.text)
        return ExtractionTestResponse(
            response=response,
            confidence=confidence,
            sentiment=sentiment,
            raw_output=request.text
        )
    except Exception as e:
        print(f"Error in extraction test: {str(e)}")
        return ExtractionTestResponse(
            response="Error during extraction",
            confidence=0.0,
            sentiment="neutral",
            raw_output=str(e)
        )

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information.
    
    Returns:
        dict: API information.
    """
    return {
        "message": "AI Agent API is running!",
        "endpoints": [
            "/api/agent",
            "/api/test-extraction",
            "/docs"
        ],
        "documentation": "Visit /docs for interactive API documentation"
    } 