# src/database.py

from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from datetime import datetime
import json
import logging
from collections import defaultdict
from .models import ResumeEntry
from .query_builder import ResumeQueryBuilder

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeDatabase:
    """Database system for managing resume entries stored as individual JSON files"""
    
    def __init__(self, data_dir: Path):
        """Initialize database with directory for entry files"""
        self.data_dir = Path(data_dir)
        self.entries: Dict[str, Dict] = {}
        self.indices = self._initialize_indices()
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load all entries
        self.load_entries()

    def _initialize_indices(self) -> Dict:
        """Initialize the indexing system"""
        return {
            'skills': defaultdict(set),
            'companies': defaultdict(set),
            'categories': defaultdict(set),
            'tags': defaultdict(set),
            'proficiency': defaultdict(lambda: defaultdict(set)),
            'dates': []  # Will store (datetime, entry_id) tuples
        }

    def load_entries(self) -> None:
        """Load all JSON files from the data directory"""
        logger.info(f"Loading entries from {self.data_dir}")
        for file_path in self.data_dir.glob("*.json"):
            try:
                entry_id = file_path.stem
                with open(file_path, 'r') as f:
                    entry_data = json.load(f)
                    self.entries[entry_id] = entry_data
                    self._index_entry(entry_id, entry_data)
            except Exception as e:
                logger.error(f"Error loading entry from {file_path}: {e}")

    def _index_entry(self, entry_id: str, entry_data: Dict) -> None:
        """Index an entry for efficient querying"""
        # Index skills
        for skill in entry_data.get('skills', []):
            self.indices['skills'][skill].add(entry_id)
        
        # Index company
        if 'company' in entry_data:
            self.indices['companies'][entry_data['company']].add(entry_id)
        
        # Index category
        if 'category' in entry_data:
            self.indices['categories'][entry_data['category']].add(entry_id)
            
        # Index tags
        for tag in entry_data.get('tags', []):
            self.indices['tags'][tag].add(entry_id)
            
        # Index technical details by proficiency
        for detail in entry_data.get('technical_details', []):
            self.indices['proficiency'][detail['proficiency']][detail['category']].add(entry_id)
        
        # Index dates for range queries
        start_date = datetime.strptime(entry_data['dates']['start'], '%Y-%m')
        self.indices['dates'].append((start_date, entry_id))
        self.indices['dates'].sort(key=lambda x: x[0])

    def add_entry(self, entry_id: str, entry_data: Dict) -> None:
        """Add a new entry or update existing entry"""
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

    def _get_entry_path(self, entry_id: str) -> Path:
        """Get the file path for an entry"""
        return self.data_dir / f"{entry_id}.json"

    def query(self) -> ResumeQueryBuilder:
        """Create a new query builder"""
        return ResumeQueryBuilder(self)

    def _execute_query(self, query: ResumeQueryBuilder) -> List[Dict]:
        """Execute a query built with QueryBuilder"""
        results: Optional[Set[str]] = None

        # Apply skill filters
        for skills, match_all in query.skill_filters:
            skill_matches = self._filter_by_skills(skills, match_all)
            results = self._combine_results(results, skill_matches)

        # Apply date filters
        for start, end in query.date_filters:
            date_matches = self._filter_by_date_range(start, end)
            results = self._combine_results(results, date_matches)

        # If no filters applied, use all entries
        if results is None:
            results = set(self.entries.keys())

        # Convert results to list of entries
        entries = [self.entries[entry_id] for entry_id in results]

        # Apply sorting
        for field, ascending in query.sort_options:
            entries = self._sort_entries(entries, field, ascending)

        # Apply offset and limit
        if query.offset_value:
            entries = entries[query.offset_value:]
        if query.limit_value:
            entries = entries[:query.limit_value]

        return entries

    def _filter_by_skills(self, skills: List[str], match_all: bool) -> Set[str]:
        """Filter entries by skills"""
        if not skills:
            return set(self.entries.keys())
        
        skill_sets = [self.indices['skills'][skill] for skill in skills]
        if match_all:
            return set.intersection(*skill_sets) if skill_sets else set()
        return set.union(*skill_sets) if skill_sets else set()

    def _filter_by_date_range(self, start: Optional[str], end: Optional[str]) -> Set[str]:
        """Filter entries by date range"""
        if not start and not end:
            return set(self.entries.keys())
            
        start_date = datetime.strptime(start, '%Y-%m') if start else None
        end_date = datetime.strptime(end, '%Y-%m') if end else None
        
        matching_entries = set()
        for entry_id, entry in self.entries.items():
            if self._is_in_date_range(entry['dates'], start_date, end_date):
                matching_entries.add(entry_id)
                
        return matching_entries

    def _is_in_date_range(self, dates: Dict, start_date: Optional[datetime], 
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

    @staticmethod
    def _combine_results(current: Optional[Set[str]], new_results: Set[str]) -> Set[str]:
        """Combine query results"""
        if current is None:
            return new_results
        return current & new_results

    def _sort_entries(self, entries: List[Dict], field: str, ascending: bool = True) -> List[Dict]:
        """Sort entries by specified field"""
        if field == 'date':
            return sorted(entries, 
                        key=lambda x: datetime.strptime(x['dates']['start'], '%Y-%m'),
                        reverse=not ascending)
        return entries

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

    # Keep the original query_entries method for backward compatibility
    def query_entries(self, 
                     skills: Optional[List[str]] = None,
                     companies: Optional[List[str]] = None,
                     categories: Optional[List[str]] = None,
                     tags: Optional[List[str]] = None,
                     date_range: Optional[tuple] = None) -> List[Dict]:
        """Legacy method for querying entries - uses new query builder internally"""
        query = self.query()
        
        if skills:
            query.with_skills(skills)
        if companies:
            query.at_companies(companies)
        if categories:
            query.in_categories(categories)
        if tags:
            query.with_tags(tags)
        if date_range:
            query.in_date_range(*date_range)
            
        return query.execute()