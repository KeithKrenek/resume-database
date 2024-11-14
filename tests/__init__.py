"""
Test initialization and shared utilities for resume database tests.
"""

import json
from pathlib import Path
from typing import Dict, Optional


def create_test_entry(
    entry_id: str,
    core: str = "Test entry description",
    start_date: str = "2024-01",
    end_date: Optional[str] = "2024-03",
    category: str = "test_category",
    company: str = "Test Company",
    skills: Optional[list] = None
) -> Dict:
    """
    Create a test entry with default values for testing.
    
    Args:
        entry_id: Unique identifier for the entry
        core: Core description of the entry
        start_date: Start date in YYYY-MM format
        end_date: End date in YYYY-MM format (optional)
        category: Entry category
        company: Company name
        skills: List of skills (optional)
        
    Returns:
        Dict containing the test entry data
    """
    return {
        "id": entry_id,
        "core": core,
        "dates": {
            "start": start_date,
            "end": end_date,
            "status": "completed" if end_date else "ongoing"
        },
        "category": category,
        "company": company,
        "skills": skills or ["Python", "Testing"],
        "metrics": [
            {
                "value": "100%",
                "context": "test coverage",
                "verified": True,
                "category": "testing",
                "timeframe": "continuous",
                "impact_area": "quality"
            }
        ],
        "technical_details": [
            {
                "category": "testing",
                "detail": "Unit testing",
                "proficiency": "expert"
            }
        ],
        "tags": ["Testing", "Quality"]
    }


def create_sample_entries() -> Dict[str, Dict]:
    """
    Create a set of sample entries for testing.
    
    Returns:
        Dict mapping entry IDs to entry data
    """
    return {
        "TEST001": create_test_entry(
            "TEST001",
            core="Python development project",
            skills=["Python", "Django", "Testing"],
            category="development"
        ),
        "TEST002": create_test_entry(
            "TEST002",
            core="Data analysis project",
            skills=["Python", "Pandas", "Data Analysis"],
            category="analysis",
            start_date="2023-01",
            end_date="2023-12"
        ),
        "TEST003": create_test_entry(
            "TEST003",
            core="Ongoing research project",
            skills=["Research", "Machine Learning"],
            category="research",
            start_date="2024-01",
            end_date=None
        )
    }


def save_test_entries(entries: Dict[str, Dict], base_path: Path) -> None:
    """
    Save test entries to individual JSON files.
    
    Args:
        entries: Dictionary mapping entry IDs to entry data
        base_path: Base directory for saving entry files
    """
    base_path.mkdir(parents=True, exist_ok=True)
    
    for entry_id, entry_data in entries.items():
        file_path = base_path / f"{entry_id}.json"
        with open(file_path, 'w') as f:
            json.dump(entry_data, f, indent=2)


def setup_test_database(tmp_path: Path) -> Path:
    """
    Set up a test database with sample entries.
    
    Args:
        tmp_path: Temporary directory path (provided by pytest)
        
    Returns:
        Path to the test database directory
    """
    test_db_path = tmp_path / "test_entries"
    entries = create_sample_entries()
    save_test_entries(entries, test_db_path)
    return test_db_path


# Common test data
VALID_DATES = {
    "start": "2024-01",
    "end": "2024-03",
    "status": "completed"
}

VALID_METRICS = [
    {
        "value": "50%",
        "context": "improvement in efficiency",
        "verified": True,
        "category": "performance",
        "timeframe": "3 months",
        "impact_area": "productivity"
    }
]

VALID_TECHNICAL_DETAILS = [
    {
        "category": "backend",
        "detail": "Python development",
        "proficiency": "expert"
    }
]

# Test fixtures and utilities can be imported by test files
__all__ = [
    'create_test_entry',
    'create_sample_entries',
    'save_test_entries',
    'setup_test_database',
    'VALID_DATES',
    'VALID_METRICS',
    'VALID_TECHNICAL_DETAILS'
]