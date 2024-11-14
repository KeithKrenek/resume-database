# src/utils.py
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_json_file(file_path: Path) -> Dict:
    """Load and parse JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        raise

def save_json_file(data: Dict, file_path: Path) -> None:
    """Save data to JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        raise

def format_date(date_str: str) -> str:
    """Format date string to YYYY-MM format"""
    try:
        date = datetime.strptime(date_str, "%Y-%m")
        return date.strftime("%Y-%m")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM")

def filter_entries_by_date_range(
    entries: List[Dict],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """Filter entries by date range"""
    if not (start_date or end_date):
        return entries
        
    filtered = []
    start = datetime.strptime(start_date, "%Y-%m") if start_date else None
    end = datetime.strptime(end_date, "%Y-%m") if end_date else None
    
    for entry in entries:
        entry_start = datetime.strptime(entry['dates']['start'], "%Y-%m")
        entry_end = (
            datetime.strptime(entry['dates']['end'], "%Y-%m")
            if entry['dates'].get('end')
            else datetime.now()
        )
        
        if start and entry_end < start:
            continue
        if end and entry_start > end:
            continue
        filtered.append(entry)
    
    return filtered