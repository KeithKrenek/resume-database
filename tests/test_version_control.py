# test_version_control.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.database import ResumeDatabase
from src.version_control import VersionControl
import json
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test the version control functionality"""
    # Initialize database with test directory
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Initialize version control
    vc = VersionControl(test_dir)
    
    print("\n=== Testing Version Control System ===\n")
    
    # Test entry creation and updates
    entry_id = "TST001"
    
    # Initial version
    print("Creating initial version...")
    initial_data = {
        "core": "Led development of ML system",
        "dates": {
            "start": "2024-01",
            "end": "2024-03",
            "status": "completed"
        },
        "skills": ["Python", "Machine Learning"]
    }
    
    change = vc.record_change(
        entry_id=entry_id,
        new_data=initial_data,
        change_type='create',
        comment="Initial creation"
    )
    print(f"Created initial version with hash: {change.new_hash[:8]}")
    
    # First update
    print("\nMaking first update...")
    updated_data = initial_data.copy()
    updated_data["skills"].append("Deep Learning")
    updated_data["metrics"] = [{
        "value": "25%",
        "context": "improvement in accuracy"
    }]
    
    change = vc.record_change(
        entry_id=entry_id,
        new_data=updated_data,
        change_type='update',
        comment="Added metrics and deep learning skill"
    )
    print(f"Created updated version with hash: {change.new_hash[:8]}")
    
    # View history
    print("\nEntry history:")
    history = vc.get_history(entry_id)
    for record in history:
        print(f"\nChange at {record.timestamp}")
        print(f"Type: {record.change_type}")
        print(f"Fields changed: {', '.join(record.fields_changed)}")
        if record.comment:
            print(f"Comment: {record.comment}")
    
    # View diff between versions
    if len(history) >= 2:
        print("\nDiff between versions:")
        diff = vc.get_diff(
            entry_id,
            history[0].new_hash,
            history[1].new_hash
        )
        print('\n'.join(diff))
    
    # Test rollback
    print("\nTesting rollback...")
    original_version = vc.rollback(entry_id, history[0].new_hash)
    print("Rolled back to original version:")
    pprint(original_version)
    
    # View final history
    print("\nFinal history after rollback:")
    final_history = vc.get_history(entry_id)
    for record in final_history:
        print(f"\nChange at {record.timestamp}")
        print(f"Type: {record.change_type}")
        print(f"Fields changed: {', '.join(record.fields_changed)}")

if __name__ == "__main__":
    main()