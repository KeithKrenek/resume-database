# test_validation.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.validators import EnhancedValidator, ValidationLevel
import json
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test the enhanced validation functionality"""
    validator = EnhancedValidator()
    
    print("\n=== Testing Enhanced Validation System ===\n")
    
    # Test Case 1: Good entry with minor suggestions
    print("Test Case 1: Good entry with minor suggestions")
    good_entry = {
        "core": "Led development of machine learning pipeline for manufacturing optimization, resulting in significant efficiency improvements",
        "dates": {
            "start": "2024-01",
            "end": "2024-03",
            "status": "completed"
        },
        "skills": ["Python", "Machine Learning", "TensorFlow 2.0", "AWS"],
        "metrics": [
            {
                "value": "25%",
                "context": "improvement in production efficiency",
                "category": "performance",
                "timeframe": "3 months",
                "impact_area": "manufacturing"
            }
        ]
    }
    
    results = validator.validate_entry(good_entry)
    print("\nValidation results:")
    for result in results:
        print(f"- {result}")
    
    # Test Case 2: Entry with issues
    print("\nTest Case 2: Entry with issues")
    problematic_entry = {
        "core": "Did stuff",  # Too short
        "dates": {
            "start": "2024-01",
            "end": "2023-12"  # End before start
        },
        "skills": ["python", "ML", "custom_framework"],  # Non-standard skills
        "metrics": [
            {
                "value": "lots",  # Non-standard metric
                "context": "imp",  # Too brief
                "category": "performance"
            }
        ]
    }
    
    results = validator.validate_entry(problematic_entry)
    
    print("\nValidation results:")
    for level in ValidationLevel:
        level_results = [r for r in results if r.level == level]
        if level_results:
            print(f"\n{level.value.upper()}S:")
            for result in level_results:
                print(f"- {result}")

if __name__ == "__main__":
    main()