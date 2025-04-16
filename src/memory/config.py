"""
Configuration settings for the memory system.
"""
import os
from typing import Dict, Any

# Memory system configuration
MEMORY_CONFIG = {
    # Short-term memory settings
    "short_term": {
        "max_size": int(os.getenv("MEMORY_SHORT_TERM_SIZE", "10")),
        "include_in_prompt": True
    },
    
    # Working memory settings (for future implementation)
    "working": {
        "enabled": False,
        "max_facts": 100,
        "importance_threshold": 0.7
    },
    
    # Long-term memory settings (for future implementation)
    "long_term": {
        "enabled": False,
        "similarity_threshold": 0.75,
        "max_results": 5
    },
    
    # General memory settings
    "general": {
        "persistence_enabled": True,
        "persistence_dir": os.getenv(
            "MEMORY_PERSISTENCE_DIR", 
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory_data")
        ),
        "token_limit": 4000
    }
}

def get_memory_config() -> Dict[str, Any]:
    """
    Get the current memory configuration.
    
    Returns:
        Dict[str, Any]: The memory configuration dictionary
    """
    return MEMORY_CONFIG

def update_memory_config(section: str, key: str, value: Any) -> None:
    """
    Update a specific memory configuration setting.
    
    Args:
        section (str): The configuration section (short_term, working, long_term, general)
        key (str): The configuration key to update
        value (Any): The new value
    
    Raises:
        KeyError: If the section or key doesn't exist
    """
    if section not in MEMORY_CONFIG:
        raise KeyError(f"Configuration section '{section}' not found")
    
    if key not in MEMORY_CONFIG[section]:
        raise KeyError(f"Configuration key '{key}' not found in section '{section}'")
    
    MEMORY_CONFIG[section][key] = value 