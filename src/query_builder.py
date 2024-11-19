# src/query_builder.py

from typing import List, Optional
from datetime import datetime

class ResumeQueryBuilder:
    """Builder pattern for constructing complex queries"""
    
    def __init__(self, database):
        self.database = database
        self.skill_filters = []
        self.date_filters = []
        self.category_filters = []
        self.company_filters = []
        self.tag_filters = []
        self.proficiency_filters = []
        self.sort_options = []
        self.limit_value = None
        self.offset_value = None

    def with_skills(self, skills: List[str], match_all: bool = True) -> 'ResumeQueryBuilder':
        """Filter entries by required skills"""
        self.skill_filters.append((skills, match_all))
        return self

    def in_date_range(self, start: Optional[str] = None, end: Optional[str] = None) -> 'ResumeQueryBuilder':
        """Filter entries by date range"""
        self.date_filters.append((start, end))
        return self

    def in_categories(self, categories: List[str]) -> 'ResumeQueryBuilder':
        """Filter entries by categories"""
        self.category_filters.append(categories)
        return self

    def at_companies(self, companies: List[str]) -> 'ResumeQueryBuilder':
        """Filter entries by companies"""
        self.company_filters.append(companies)
        return self

    def with_tags(self, tags: List[str], match_all: bool = True) -> 'ResumeQueryBuilder':
        """Filter entries by tags"""
        self.tag_filters.append((tags, match_all))
        return self

    def sort_by(self, field: str, ascending: bool = True) -> 'ResumeQueryBuilder':
        """Add sorting criteria"""
        self.sort_options.append((field, ascending))
        return self

    def limit(self, count: int) -> 'ResumeQueryBuilder':
        """Limit number of results"""
        self.limit_value = count
        return self

    def offset(self, count: int) -> 'ResumeQueryBuilder':
        """Skip first n results"""
        self.offset_value = count
        return self

    def execute(self) -> List[dict]:
        """Execute the query and return results"""
        return self.database._execute_query(self)