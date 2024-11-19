# tests/test_database.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from src.database import ResumeDatabase
from datetime import datetime

@pytest.fixture
def test_db(tmp_path):
    """Create a test database instance"""
    return ResumeDatabase(tmp_path / "test_entries")

def test_add_entry(test_db):
    """Test adding an entry"""
    entry_data = {
        "core": "Test entry description",
        "dates": {
            "start": "2024-01",
            "end": "2024-03",
            "status": "completed"
        },
        "category": "test",
        "skills": ["Python", "Testing"]
    }
    
    test_db.add_entry("TEST001", entry_data)
    assert "TEST001" in test_db.entries
    assert test_db.entries["TEST001"] == entry_data

def test_query_entries(test_db):
    """Test querying entries"""
    # Add test entries
    entry1 = {
        "core": "Python development",
        "dates": {"start": "2024-01", "end": "2024-03"},
        "skills": ["Python", "Testing"],
        "category": "development"
    }
    entry2 = {
        "core": "Data analysis",
        "dates": {"start": "2023-01", "end": "2023-12"},
        "skills": ["Python", "Data Analysis"],
        "category": "analysis"
    }
    
    test_db.add_entry("TEST001", entry1)
    test_db.add_entry("TEST002", entry2)
    
    # Test queries
    python_entries = test_db.query_entries(skills=["Python"])
    assert len(python_entries) == 2
    
    recent_entries = test_db.query_entries(
        date_range=("2024-01", "2024-12")
    )
    assert len(recent_entries) == 1