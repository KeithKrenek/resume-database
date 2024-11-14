# tests/test_models.py
import pytest
from src.models import ResumeEntry, DateInfo

def test_resume_entry_validation():
    """Test resume entry validation"""
    # Valid entry
    entry_data = {
        "core": "Valid test entry",
        "dates": {
            "start": "2024-01",
            "end": "2024-03"
        },
        "skills": ["Testing"]
    }
    entry = ResumeEntry("TEST001", entry_data)
    assert entry.core == "Valid test entry"
    
    # Invalid entry (missing core)
    with pytest.raises(ValueError):
        ResumeEntry("TEST002", {"dates": {"start": "2024-01"}})

def test_date_info():
    """Test date info handling"""
    date_info = DateInfo(start="2024-01", end="2024-03")
    assert date_info.start_date.year == 2024
    assert date_info.start_date.month == 1
    assert date_info.end_date.month == 3