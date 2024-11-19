# src/utils.py
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import json
from pathlib import Path
import logging
import hashlib
import shutil
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class FileOperationError(Exception):
    """Custom exception for file operations"""
    pass

@contextmanager
def safe_file_operation(operation: str):
    """Context manager for safe file operations"""
    try:
        yield
    except Exception as e:
        logger.error(f"Error during {operation}: {str(e)}")
        raise FileOperationError(f"Failed to {operation}: {str(e)}")

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse JSON file with error handling"""
    with safe_file_operation("read JSON file"):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_json_file(data: Dict[str, Any], file_path: Path, backup: bool = True) -> None:
    """Save data to JSON file with backup option"""
    with safe_file_operation("write JSON file"):
        # Create backup if requested
        if backup and file_path.exists():
            backup_path = file_path.with_suffix('.bak')
            shutil.copy2(file_path, backup_path)
        
        # Write new file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def format_date(date_str: str) -> str:
    """Format date string to YYYY-MM format with validation"""
    try:
        date = datetime.strptime(date_str, "%Y-%m")
        return date.strftime("%Y-%m")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM")

def filter_entries_by_date_range(
    entries: List[Dict[str, Any]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filter entries by date range with validation"""
    if not (start_date or end_date):
        return entries
    
    try:
        start = datetime.strptime(start_date, "%Y-%m") if start_date else None
        end = datetime.strptime(end_date, "%Y-%m") if end_date else None
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")
    
    filtered = []
    for entry in entries:
        try:
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
        except (KeyError, ValueError) as e:
            logger.warning(f"Skipping entry with invalid dates: {e}")
            continue
    
    return filtered

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file"""
    with safe_file_operation("calculate file hash"):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

def ensure_directory(directory: Path) -> None:
    """Ensure directory exists and is writable"""
    with safe_file_operation("create directory"):
        directory.mkdir(parents=True, exist_ok=True)
        if not os.access(directory, os.W_OK):
            raise PermissionError(f"Directory not writable: {directory}")