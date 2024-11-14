# src/database.py

from pathlib import Path
from typing import Dict, List, Optional, Iterator
import json
import logging
from datetime import datetime
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeDatabase:
    """Database system for managing resume entries stored as individual JSON files"""
    
    def __init__(self, data_dir: Path):
        """
        Initialize database with directory for entry files
        
        Args:
            data_dir: Path to directory containing JSON entry files
        """
        self.data_dir = Path(data_dir)
        self.entries: Dict[str, Dict] = {}
        self.index: Dict[str, Dict] = {
            'skills': {},
            'companies': {},
            'categories': {},
            'tags': {}
        }
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load all entries
        self.load_entries()

    def _get_entry_path(self, entry_id: str) -> Path:
        """Get the file path for an entry"""
        return self.data_dir / f"{entry_id}.json"

    def load_entries(self) -> None:
        """Load all JSON files from the data directory"""
        logger.info(f"Loading entries from {self.data_dir}")
        for file_path in self.data_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    entry_data = json.load(f)
                    entry_id = file_path.stem  # filename without extension
                    self.entries[entry_id] = entry_data
                    self._index_entry(entry_id, entry_data)
            except Exception as e:
                logger.error(f"Error loading entry from {file_path}: {e}")

    def _index_entry(self, entry_id: str, entry_data: Dict) -> None:
        """Index an entry for efficient querying"""
        # Index skills
        for skill in entry_data.get('skills', []):
            self.index['skills'].setdefault(skill, []).append(entry_id)
        
        # Index company
        if 'company' in entry_data:
            self.index['companies'].setdefault(
                entry_data['company'], []).append(entry_id)
        
        # Index category
        if 'category' in entry_data:
            self.index['categories'].setdefault(
                entry_data['category'], []).append(entry_id)
            
        # Index tags
        for tag in entry_data.get('tags', []):
            self.index['tags'].setdefault(tag, []).append(entry_id)

    def add_entry(self, entry_id: str, entry_data: Dict) -> None:
        """
        Add a new entry or update existing entry
        
        Args:
            entry_id: Unique identifier for the entry
            entry_data: Dictionary containing entry data
        """
        # Validate entry data
        self._validate_entry(entry_data)
        
        # Save to file
        entry_path = self._get_entry_path(entry_id)
        try:
            with open(entry_path, 'w') as f:
                json.dump(entry_data, f, indent=2)
            
            # Update memory storage
            self.entries[entry_id] = entry_data
            self._index_entry(entry_id, entry_data)
            logger.info(f"Successfully saved entry {entry_id}")
            
        except Exception as e:
            logger.error(f"Error saving entry {entry_id}: {e}")
            raise

    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """Retrieve an entry by ID"""
        return self.entries.get(entry_id)

    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry by ID"""
        entry_path = self._get_entry_path(entry_id)
        if entry_path.exists():
            try:
                entry_path.unlink()  # Delete file
                del self.entries[entry_id]
                # Remove from indices
                self._remove_from_indices(entry_id)
                logger.info(f"Successfully deleted entry {entry_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting entry {entry_id}: {e}")
                raise
        return False

    def _remove_from_indices(self, entry_id: str) -> None:
        """Remove an entry from all indices"""
        for index_type in self.index:
            for key in list(self.index[index_type].keys()):
                if entry_id in self.index[index_type][key]:
                    self.index[index_type][key].remove(entry_id)
                if not self.index[index_type][key]:
                    del self.index[index_type][key]

    def backup_entries(self, backup_dir: Path) -> None:
        """Create a backup of all entry files"""
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy all JSON files to backup directory
            for file_path in self.data_dir.glob("*.json"):
                shutil.copy2(file_path, backup_dir / file_path.name)
            logger.info(f"Successfully backed up entries to {backup_dir}")
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    def query_entries(self, 
                     skills: Optional[List[str]] = None,
                     companies: Optional[List[str]] = None,
                     categories: Optional[List[str]] = None,
                     tags: Optional[List[str]] = None,
                     date_range: Optional[tuple] = None) -> List[Dict]:
        """
        Query entries based on multiple criteria
        
        Args:
            skills: List of required skills
            companies: List of companies
            categories: List of categories
            tags: List of tags
            date_range: Tuple of (start_date, end_date) in 'YYYY-MM' format
            
        Returns:
            List of matching entries
        """
        result_sets = []
        
        if skills:
            skill_entries = set.intersection(
                *[set(self.index['skills'].get(skill, [])) for skill in skills]
            )
            result_sets.append(skill_entries)
            
        if companies:
            company_entries = set.union(
                *[set(self.index['companies'].get(company, [])) 
                  for company in companies]
            )
            result_sets.append(company_entries)
            
        if categories:
            category_entries = set.union(
                *[set(self.index['categories'].get(category, [])) 
                  for category in categories]
            )
            result_sets.append(category_entries)
            
        if tags:
            tag_entries = set.intersection(
                *[set(self.index['tags'].get(tag, [])) for tag in tags]
            )
            result_sets.append(tag_entries)
            
        if date_range:
            start_date, end_date = [
                datetime.strptime(d, '%Y-%m') if d else None 
                for d in date_range
            ]
            date_filtered = {
                entry_id for entry_id, entry in self.entries.items()
                if self._is_in_date_range(entry['dates'], start_date, end_date)
            }
            result_sets.append(date_filtered)
        
        if not result_sets:
            return list(self.entries.values())
            
        # Intersect all result sets
        final_ids = set.intersection(*result_sets)
        return [self.entries[entry_id] for entry_id in final_ids]

    @staticmethod
    def _is_in_date_range(dates: Dict, start_date: Optional[datetime], 
                         end_date: Optional[datetime]) -> bool:
        """Check if entry dates fall within specified range"""
        entry_start = datetime.strptime(dates['start'], '%Y-%m')
        entry_end = (datetime.strptime(dates['end'], '%Y-%m') 
                    if dates.get('end') else datetime.now())
        
        if start_date and entry_end < start_date:
            return False
        if end_date and entry_start > end_date:
            return False
        return True

    def _validate_entry(self, entry_data: Dict) -> None:
        """Validate entry data structure"""
        required_fields = ['core', 'dates']
        missing = [f for f in required_fields if f not in entry_data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        if 'dates' in entry_data:
            if 'start' not in entry_data['dates']:
                raise ValueError("Missing start date")
            
            # Validate date format
            try:
                datetime.strptime(entry_data['dates']['start'], '%Y-%m')
                if entry_data['dates'].get('end'):
                    datetime.strptime(entry_data['dates']['end'], '%Y-%m')
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM")

# Example usage:
if __name__ == "__main__":
    # Initialize database
    db = ResumeDatabase(Path("data/entries"))
    
    # Example query
    results = db.query_entries(
        skills=["Python", "Machine Learning"],
        categories=["experience"],
        date_range=("2020-01", "2024-03")
    )
    
    for result in results:
        print(f"\nEntry: {result['core']}")
        print(f"Company: {result.get('company', 'N/A')}")
        print(f"Skills: {', '.join(result.get('skills', []))}")