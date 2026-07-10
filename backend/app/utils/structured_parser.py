import json
import re
import logging
from typing import Dict, Any, Tuple, List
from app.ai.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

def extract_json_block(text: str) -> str:
    """
    Stage 2: Removes markdown code fences and isolates the first complete JSON object.
    """
    clean_text = text.strip()
    
    # Remove markdown code fences if present
    json_block = re.search(r'```(?:json)?\s*(.*?)\s*```', clean_text, re.DOTALL | re.IGNORECASE)
    if json_block:
        clean_text = json_block.group(1).strip()
    else:
        # Extract first complete JSON object from text between '{' and '}'
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            clean_text = clean_text[start_idx:end_idx+1].strip()
            
    return clean_text

def clean_json_string(text: str) -> str:
    """
    Stage 3: Cleans a JSON string to recover common syntax errors:
    - Trailing commas in arrays or objects.
    - Single quotes used for keys or values.
    - Escaped newlines inside string literals.
    """
    # Recover single quotes on keys and values
    text = re.sub(r"'([^']*?)'\s*:", r'"\1":', text)
    text = re.sub(r":\s*'([^']*?)'", r': "\1"', text)
    text = re.sub(r"\[\s*'([^']*?)'", r'["\1"', text)
    text = re.sub(r"'\s*\]", r'"]', text)
    text = re.sub(r",\s*'([^']*?)'", r', "\1"', text)
    text = re.sub(r"'([^']*?)'\s*,", r'"\1",', text)
    
    # Recover trailing commas in objects and arrays
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*\]', ']', text)
    
    # Handle newline escaping
    text = text.replace('\n', '\\n').replace('\r', '\\r')
    return text

def parse_llm_json(raw_text: str) -> Dict[str, Any]:
    """
    Attempts to parse LLM raw text using a layered recovery parser:
    Stage 1: Attempt standard json.loads()
    Stage 2: Extract JSON block and retry json.loads()
    Stage 3: Apply lightweight cleanups and retry json.loads()
    """
    # --- Stage 1 ---
    try:
        return json.loads(raw_text.strip())
    except Exception:
        pass
        
    # --- Stage 2 ---
    extracted = extract_json_block(raw_text)
    try:
        return json.loads(extracted)
    except Exception:
        pass
        
    # --- Stage 3 ---
    cleaned = clean_json_string(extracted)
    try:
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"JSON parsing failed across all stages: {e}")

def normalize_dict(
    data: Any,
    string_fields: List[str],
    list_fields: List[str]
) -> Tuple[Dict[str, Any], bool]:
    """
    Normalizes a dictionary representing structured output keys.
    Returns the normalized dictionary and a boolean flag indicating if any normalization was performed.
    """
    if not isinstance(data, dict):
        data = {}
        
    normalized = {}
    performed_normalization = False
    
    # 1. Normalize string fields
    for field in string_fields:
        val = data.get(field)
        if val is None:
            normalized[field] = None
        elif isinstance(val, list):
            performed_normalization = True
            if len(val) > 0 and val[0] is not None:
                s = str(val[0]).strip()
                normalized[field] = s if s else None
            else:
                normalized[field] = None
        else:
            s = str(val).strip()
            if s != val:
                performed_normalization = True
            normalized[field] = s if s else None
            
    # 2. Normalize list fields
    for field in list_fields:
        val = data.get(field)
        if val is None:
            if field in data:
                performed_normalization = True
            normalized[field] = []
        elif isinstance(val, str):
            performed_normalization = True
            s = val.strip()
            normalized[field] = [s] if s else []
        elif isinstance(val, list):
            normalized_list = []
            for item in val:
                if item is not None:
                    s = str(item).strip()
                    if s:
                        normalized_list.append(s)
            if normalized_list != val:
                performed_normalization = True
            normalized[field] = normalized_list
        else:
            performed_normalization = True
            normalized[field] = []
            
    # Check if any fields were missing entirely from input
    for field in string_fields + list_fields:
        if field not in data:
            performed_normalization = True
            
    return normalized, performed_normalization

def safe_interaction_parse(
    raw_text: str,
    fallback_data: Dict[str, Any],
    string_fields: List[str],
    list_fields: List[str]
) -> Tuple[Dict[str, Any], str]:
    """
    Single point of responsibility for:
    - JSON parsing (layered)
    - Normalization
    - Fallback handling
    - Logging (INFO, WARNING, ERROR)
    
    Always returns (normalized_dict, warning_message). Never throws an exception.
    """
    # 1. Attempt JSON Parsing (Stages 1-3)
    try:
        parsed_dict = parse_llm_json(raw_text)
        
        # 2. Run Normalization
        normalized, performed_normalization = normalize_dict(parsed_dict, string_fields, list_fields)
        
        # 3. Structured Logging
        if performed_normalization:
            logger.warning("Normalization performed on extracted JSON data.")
            warning_msg = "Warning: normalization performed on LLM output."
        else:
            logger.info("Successfully parsed and validated LLM JSON.")
            warning_msg = ""
            
        return normalized, warning_msg
        
    except Exception as e:
        # --- Stage 4: Fallback Handling ---
        logger.error(f"Fallback used. Failed to parse LLM JSON: {e}")
        
        # Normalize fallback data to ensure compliance
        normalized_fallback, _ = normalize_dict(fallback_data, string_fields, list_fields)
        warning_msg = f"Failed to parse LLM JSON: {str(e)}"
        return normalized_fallback, warning_msg

def safe_llm_call(
    prompt_template: str,
    prompt_variables: Dict[str, Any],
    fallback_data: Dict[str, Any],
    string_fields: List[str],
    list_fields: List[str]
) -> Tuple[Dict[str, Any], str]:
    """
    Executes the LLM with retry logic, timeout handling, raw response parsing, 
    normalization, fallback handling, and structured logging.
    """
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    raw_response = ""
    attempts = 2
    last_error = None
    for attempt in range(attempts):
        try:
            response = chain.invoke(prompt_variables)
            raw_response = response.content
            break
        except Exception as e:
            last_error = e
            logger.warning(f"LLM call failed on attempt {attempt + 1}: {e}")
            if attempt == attempts - 1:
                logger.error(f"LLM call failed after {attempts} attempts. Using fallback.")
                normalized_fallback, _ = normalize_dict(fallback_data, string_fields, list_fields)
                return normalized_fallback, f"LLM error: {str(last_error)}"
                
    # Parse and normalize
    normalized_dict, warning_msg = safe_interaction_parse(raw_response, fallback_data, string_fields, list_fields)
    return normalized_dict, warning_msg
