# test_usage.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.database import ResumeDatabase
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_data(db: ResumeDatabase):
    """Set up some test entries in the database"""
    # Test entry 1: Recent Python ML project
    entry1 = {
        "id": "TST001",
        "core": "Developed machine learning pipeline",
        "dates": {
            "start": "2024-01",
            "end": "2024-03",
            "status": "completed"
        },
        "company": "Tech Corp",
        "category": "technical_projects",
        "skills": ["Python", "Machine Learning", "Data Science"],
        "tags": ["AI/ML", "Backend"],
        "technical_details": [
            {
                "category": "ml",
                "detail": "Pipeline development",
                "proficiency": "expert"
            }
        ]
    }

    # Test entry 2: Older data analysis project
    entry2 = {
        "id": "TST002",
        "core": "Data analysis for customer insights",
        "dates": {
            "start": "2023-06",
            "end": "2023-12",
            "status": "completed"
        },
        "company": "Data Corp",
        "category": "data_analysis",
        "skills": ["Python", "SQL", "Data Analysis"],
        "tags": ["Data", "Analytics"],
        "technical_details": [
            {
                "category": "data",
                "detail": "Data analysis",
                "proficiency": "intermediate"
            }
        ]
    }

    # Add entries to database
    db.add_entry("TST001", entry1)
    db.add_entry("TST002", entry2)
    
    return [entry1, entry2]

def test_queries(db: ResumeDatabase, test_entries: list):
    """Test both old and new query methods"""
    
    print("\n=== Testing Query Methods ===\n")

    # Test 1: Basic skill query
    print("Test 1: Entries with Python skill")
    print("\nOld query method:")
    old_results = db.query_entries(skills=["Python"])
    print(f"Found {len(old_results)} entries")
    for entry in old_results:
        print(f"- {entry['core']}")

    print("\nNew query method:")
    new_results = db.query().with_skills(["Python"]).execute()
    print(f"Found {len(new_results)} entries")
    for entry in new_results:
        print(f"- {entry['core']}")

    # Test 2: Date range query
    print("\nTest 2: Entries from 2024")
    print("\nOld query method:")
    old_results = db.query_entries(date_range=("2024-01", "2024-12"))
    print(f"Found {len(old_results)} entries")
    for entry in old_results:
        print(f"- {entry['core']} ({entry['dates']['start']})")

    print("\nNew query method:")
    new_results = (db.query()
                  .in_date_range("2024-01", "2024-12")
                  .execute())
    print(f"Found {len(new_results)} entries")
    for entry in new_results:
        print(f"- {entry['core']} ({entry['dates']['start']})")

    # Test 3: Complex query
    print("\nTest 3: Complex query - Python entries with ML/AI tags, sorted by date")
    print("\nOld query method:")
    old_results = db.query_entries(
        skills=["Python"],
        tags=["AI/ML"]
    )
    # Sort manually since old method doesn't support sorting
    old_results = sorted(
        old_results,
        key=lambda x: x['dates']['start'],
        reverse=True
    )
    print(f"Found {len(old_results)} entries")
    for entry in old_results:
        print(f"- {entry['core']} ({entry['dates']['start']})")

    print("\nNew query method:")
    new_results = (db.query()
                  .with_skills(["Python"])
                  .with_tags(["AI/ML"])
                  .sort_by("date", ascending=False)
                  .execute())
    print(f"Found {len(new_results)} entries")
    for entry in new_results:
        print(f"- {entry['core']} ({entry['dates']['start']})")

    # Test 4: Testing new query features
    print("\nTest 4: Demonstrating new query features")
    advanced_results = (db.query()
                       .with_skills(["Python", "Machine Learning"], match_all=True)
                       .in_date_range("2024-01", None)
                       .sort_by("date", ascending=False)
                       .limit(5)
                       .execute())
    print(f"Found {len(advanced_results)} entries matching complex criteria:")
    for entry in advanced_results:
        print(f"- {entry['core']}")
        print(f"  Skills: {', '.join(entry['skills'])}")
        print(f"  Date: {entry['dates']['start']}")

def main():
    """Main test function"""
    # Initialize database with test directory
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    db = ResumeDatabase(test_dir)
    
    # Set up test data
    test_entries = setup_test_data(db)
    
    # Run tests
    test_queries(db, test_entries)

if __name__ == "__main__":
    main()