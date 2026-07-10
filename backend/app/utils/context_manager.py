from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

def is_new_interaction_trigger(user_input: str) -> bool:
    """Detects if user input starts a fresh interaction (e.g. 'Met Dr...', 'Called...')."""
    clean = user_input.lower().strip()
    
    # Matching prefixes
    prefixes = [
        "met dr", "met with dr", "visited dr", "visited with dr",
        "called dr", "had a call with dr", "spoke to dr", "had a meeting with dr"
    ]
    return any(clean.startswith(p) for p in prefixes)

def resolve_interaction_context(state: Dict[str, Any]) -> Tuple[Dict[str, Any], str | None]:
    """
    Evaluates the input text and active state context.
    If the user input is a trigger for a new interaction, returns empty extracted_data and None interaction_id.
    Otherwise, preserves the existing context.
    """
    user_input = state.get("user_input", "")
    extracted_data = state.get("extracted_data", {})
    interaction_id = state.get("interaction_id")
    
    if is_new_interaction_trigger(user_input):
        logger.info("[DEBUG LOG] ContextManager: New interaction trigger detected. Clearing active context.")
        return {}, None
        
    return extracted_data, interaction_id
