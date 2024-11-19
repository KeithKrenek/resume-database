# src/__init__.py

from .database import ResumeDatabase
from .validators import EnhancedValidator, ValidationLevel, ValidationResult
from typing import Dict, Any

# For backward compatibility
def validate_entry(entry_data: Dict[str, Any]) -> bool:
    """
    Legacy validation function that wraps the new validation system
    
    Returns True if no errors (warnings and suggestions are allowed)
    """
    validator = EnhancedValidator()
    results = validator.validate_entry(entry_data)
    
    # Check for any error-level validations
    return not any(r.level == ValidationLevel.ERROR for r in results)

# Export new validation system
__all__ = [
    'ResumeDatabase',
    'validate_entry',
    'EnhancedValidator',
    'ValidationLevel',
    'ValidationResult'
]