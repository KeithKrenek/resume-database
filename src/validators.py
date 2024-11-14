# src/validators.py
from typing import Dict, Any
from jsonschema import validate
import logging

logger = logging.getLogger(__name__)

# JSON Schema for resume entries
ENTRY_SCHEMA = {
    "type": "object",
    "required": ["core", "dates"],
    "properties": {
        "id": {"type": "string"},
        "core": {"type": "string", "minLength": 10},
        "dates": {
            "type": "object",
            "required": ["start"],
            "properties": {
                "start": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
                "end": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
                "status": {"type": "string", "enum": ["completed", "ongoing"]}
            }
        },
        "category": {"type": "string"},
        "company": {"type": "string"},
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "metrics": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["value", "context", "category", "timeframe", "impact_area"],
                "properties": {
                    "value": {"type": "string"},
                    "context": {"type": "string"},
                    "verified": {"type": "boolean"},
                    "category": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "impact_area": {"type": "string"}
                }
            }
        },
        "technical_details": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "detail", "proficiency"],
                "properties": {
                    "category": {"type": "string"},
                    "detail": {"type": "string"},
                    "proficiency": {"type": "string"}
                }
            }
        }
    }
}

def validate_entry(entry_data: Dict[str, Any]) -> bool:
    """
    Validate entry data against schema
    
    Args:
        entry_data: Dictionary containing entry data
        
    Returns:
        bool: True if valid, raises ValidationError if invalid
    """
    try:
        validate(instance=entry_data, schema=ENTRY_SCHEMA)
        return True
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise