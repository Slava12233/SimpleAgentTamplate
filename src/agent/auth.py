"""
Authentication utilities for the agent.
"""
import os
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify the bearer token against environment variable.
    
    Args:
        credentials (HTTPAuthorizationCredentials, optional): The credentials from the request.
            Provided by FastAPI dependency injection.
            
    Returns:
        bool: True if token is valid.
        
    Raises:
        HTTPException: If token is invalid or the environment variable is not set.
    """
    expected_token = os.getenv("API_BEARER_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="API_BEARER_TOKEN environment variable not set"
        )
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return True 