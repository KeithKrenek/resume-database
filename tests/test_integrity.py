# test_integrity.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import shutil
from src.database import ResumeDatabase
from src.integrity import DataIntegrityChecker
from test_data_helper import setup_test_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_problematic_entries(db: ResumeDatabase):
    """Add entries with intentional issues for testing"""
    
    # Entry with date issues
    entry1 = {
        "id": "TST003",
        "core": "did some work",  # Too brief, no action verbs
        "dates": {
            "start": "2024-01",
            "end": "2025-12",  # Future date
        },
        "company": "Tech corp",  # Inconsistent naming with "Tech Corp"
        "skills": ["python", "ML"],  # Inconsistent skill naming
        "metrics": [
            {
                "value": "many",  # Non-quantitative
                "context": "improvements",  # Too brief
                "category": "impact",
                "timeframe": "ongoing",
                "impact_area": "general"
            }
        ]
    }
    
    # Entry with overlapping dates
    entry2 = {
        "id": "TST004",
        "core": "Worked on some projects and did various tasks",  # Vague
        "dates": {
            "start": "2024-02",  # Overlaps with TST001
            "end": "2024-04"
        },
        "company": "Tech Corp",
        "skills": ["Python 3.9", "Machine learning"],  # Inconsistent with other entries
        "technical_details": []  # Missing technical details
    }
    
    db.add_entry("TST003", entry1)
    db.add_entry("TST004", entry2)

def main():
    """Test the data integrity checking functionality"""
    # Initialize test directory
    test_dir = Path("test_data")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Initialize database and load test data
    db = ResumeDatabase(test_dir)
    test_entries = setup_test_data(db)
    add_problematic_entries(db)
    
    # Initialize integrity checker
    checker = DataIntegrityChecker(db)
    
    print("\n=== Testing Data Integrity Checker ===\n")
    
    # Check for issues
    print("Checking for integrity issues...")
    issues = checker.check_integrity()
    
    # Group issues by severity
    issues_by_severity = {
        'critical': [],
        'warning': [],
        'info': []
    }
    
    for issue in issues:
        issues_by_severity[issue.severity].append(issue)
    
    # Display results
    for severity in ['critical', 'warning', 'info']:
        severity_issues = issues_by_severity[severity]
        if severity_issues:
            print(f"\n{severity.upper()} Issues ({len(severity_issues)}):")
            for issue in severity_issues:
                print(f"\n{issue}")
    
    print("\n=== Testing Auto-Fix Functionality ===\n")
    
    # Attempt to fix common issues
    fixed, failed = checker.fix_common_issues()
    
    if fixed:
        print("\nSuccessfully fixed:")
        for fix in fixed:
            print(f"- {fix}")
    
    if failed:
        print("\nFailed to fix:")
        for failure in failed:
            print(f"- {failure}")
    
    # Check remaining issues after fixes
    print("\nChecking for remaining issues...")
    remaining_issues = checker.check_integrity()
    print(f"\nRemaining issues: {len(remaining_issues)}")

if __name__ == "__main__":
    main()