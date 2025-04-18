"""
Helper functions for GAIA D&D Campaign Assistant.
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Get the logger
logger = logging.getLogger("GAIA")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for all file systems.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        A sanitized filename
    """
    # Replace spaces with underscores
    s = filename.replace(' ', '_')
    
    # Remove any non-alphanumeric, non-underscore, non-dash, non-dot characters
    s = re.sub(r'[^\w\-\.]', '', s)
    
    # Ensure lowercase for consistency
    s = s.lower()
    
    return s

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in a human-readable way.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable file size
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            if unit == 'B':
                return f"{size_bytes} {unit}"
            return f"{size_bytes / 1024:.2f} {unit}"
        size_bytes /= 1024
    
    return f"{size_bytes:.2f} GB"

def get_file_extension(filename: str) -> str:
    """
    Get file extension from a filename.
    
    Args:
        filename: The filename to extract extension from
        
    Returns:
        The file extension (lowercase) or empty string if no extension
    """
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip('.')

def timestamp_filename(base_filename: str) -> str:
    """
    Add a timestamp to a filename.
    
    Args:
        base_filename: The base filename
        
    Returns:
        Filename with timestamp added
    """
    base_name, ext = os.path.splitext(base_filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{timestamp}{ext}"

def clean_response(response: str) -> str:
    """
    Clean AI response text to remove common formatting issues.
    
    Args:
        response: Raw response from the AI
        
    Returns:
        Cleaned response text
    """
    if not response:
        return ""
    
    # First trim whitespace
    response = response.strip()
    
    # Remove common prefixes
    prefixes_to_remove = [
        "GAIA:", 
        "Answer:", 
        "Response:", 
        "AI:", 
        "Assistant:", 
        "Here's the answer:"
    ]
    
    for prefix in prefixes_to_remove:
        if response.startswith(prefix):
            response = response[len(prefix):].strip()
    
    # Remove any synthetic conversation markers
    if "Human:" in response or "GAIA:" in response or "User:" in response:
        parts = re.split(r'(?:Human:|GAIA:|User:)', response)
        response = parts[0].strip()
        
    # Remove any fictional dialogue patterns
    dialogue_patterns = [
        r"Rupert(?:'s)? (?:response|says|asks|replied|questioned|stated):",
        r"GAIA(?:'s)? (?:response|says|replies|answered|stated):",
        r"User(?:'s)? (?:response|says|asks|replied|questioned|stated):",
        r"Human(?:'s)? (?:response|says|asks|replied|questioned|stated):"
    ]
    
    for pattern in dialogue_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            # Take only the first part before any dialogue markers
            parts = re.split(pattern, response, flags=re.IGNORECASE)
            response = parts[0].strip()
            break
    
    # Also check for numbered list format that might be part of fabricated dialogue
    if re.search(r'\d+\.\s+\*\*[^*]+\*\*:', response):
        # This looks like a numbered list with dialogue - take just the beginning
        parts = re.split(r'\d+\.\s+\*\*[^*]+\*\*:', response)
        response = parts[0].strip()
        
    # Check if response appears to be cut off mid-sentence
    last_char = response[-1] if response else ""
    if last_char and last_char not in ".!?":
        # Find the last complete sentence if possible
        last_period = max(response.rfind('.'), response.rfind('!'), response.rfind('?'))
        if last_period > len(response) * 0.7:  # Only truncate if we've got most of the content
            response = response[:last_period+1]
    
    return response

def ensure_directories_exist(paths: List[str]) -> bool:
    """
    Ensure that all directories in the list exist.
    
    Args:
        paths: List of directory paths
        
    Returns:
        True if all directories exist (or were created), False otherwise
    """
    try:
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)
                logger.info(f"Created directory: {path}")
        return True
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        return False