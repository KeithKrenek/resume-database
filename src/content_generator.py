# src/content_generator.py

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RoleContent:
    """Represents role-specific content with multiple detail levels"""
    entry_id: str
    company: str
    dates: Dict
    short: str
    medium: str
    detailed: str
    skills: List[str]
    metrics: List[Dict]
    tech_details: List[Dict]

    @classmethod
    def from_entry(cls, entry_id: str, entry: Dict, role: str) -> Optional['RoleContent']:
        """Create RoleContent from entry data for specific role"""
        if 'variations' not in entry or role not in entry['variations']:
            return None
            
        variations = entry['variations'][role]
        return cls(
            entry_id=entry_id,
            company=entry.get('company', ''),
            dates=entry['dates'],
            short=variations.get('short', entry['core']),
            medium=variations.get('medium', entry['core']),
            detailed=variations.get('detailed', entry['core']),
            skills=entry.get('skills', []),
            metrics=entry.get('metrics', []),
            tech_details=entry.get('technical_details', [])
        )

class ContentGenerator:
    """Generates role-specific content from resume entries"""
    
    def __init__(self, database):
        self.db = database
        self.role_cache = defaultdict(list)
        self._build_role_index()

    def _build_role_index(self) -> None:
        """Index entries by roles for faster access"""
        for entry_id, entry in self.db.entries.items():
            if 'variations' in entry:
                for role in entry['variations'].keys():
                    role_content = RoleContent.from_entry(entry_id, entry, role)
                    if role_content:
                        self.role_cache[role].append(role_content)
        
        # Sort each role's entries by date (most recent first)
        for role in self.role_cache:
            self.role_cache[role].sort(
                key=lambda x: datetime.strptime(x.dates['start'], '%Y-%m'),
                reverse=True
            )

    def get_roles(self) -> List[str]:
        """Get list of all available roles"""
        return list(self.role_cache.keys())

    def generate_role_content(self, 
                            role: str,
                            limit: Optional[int] = None,
                            detail_level: str = 'detailed',
                            skills_filter: Optional[List[str]] = None,
                            date_range: Optional[tuple] = None) -> List[Dict]:
        """
        Generate role-specific content with various options
        
        Args:
            role: Target role
            limit: Maximum number of entries to return
            detail_level: 'short', 'medium', or 'detailed'
            skills_filter: Optional list of required skills
            date_range: Optional tuple of (start_date, end_date) in YYYY-MM format
            
        Returns:
            List of formatted entries for the role
        """
        if role not in self.role_cache:
            logger.warning(f"No entries found for role: {role}")
            return []

        entries = self.role_cache[role]

        # Apply skills filter
        if skills_filter:
            entries = [
                e for e in entries
                if all(skill in e.skills for skill in skills_filter)
            ]

        # Apply date filter
        if date_range:
            start_date = (datetime.strptime(date_range[0], '%Y-%m') 
                         if date_range[0] else None)
            end_date = (datetime.strptime(date_range[1], '%Y-%m')
                       if date_range[1] else None)
            
            entries = [
                e for e in entries
                if self._is_in_date_range(e.dates, start_date, end_date)
            ]

        # Format entries according to detail level
        formatted_entries = []
        for entry in entries[:limit]:
            formatted = {
                'id': entry.entry_id,
                'company': entry.company,
                'dates': entry.dates,
                'description': getattr(entry, detail_level),
                'skills': entry.skills
            }
            
            # Add metrics if using detailed view
            if detail_level == 'detailed':
                formatted['metrics'] = entry.metrics
                formatted['technical_details'] = entry.tech_details
                
            formatted_entries.append(formatted)

        return formatted_entries

    def generate_role_summary(self, role: str) -> Dict:
        """Generate a summary of entries for a role"""
        if role not in self.role_cache:
            return {'role': role, 'count': 0}

        entries = self.role_cache[role]
        
        # Collect unique skills and companies
        skills = set()
        companies = set()
        date_range = [None, None]  # [earliest, latest]
        
        for entry in entries:
            skills.update(entry.skills)
            if entry.company:
                companies.add(entry.company)
            
            entry_date = datetime.strptime(entry.dates['start'], '%Y-%m')
            if not date_range[0] or entry_date < date_range[0]:
                date_range[0] = entry_date
            
            end_date = (datetime.strptime(entry.dates['end'], '%Y-%m')
                       if entry.dates.get('end') else datetime.now())
            if not date_range[1] or end_date > date_range[1]:
                date_range[1] = end_date

        return {
            'role': role,
            'count': len(entries),
            'skills': sorted(skills),
            'companies': sorted(companies),
            'date_range': {
                'start': date_range[0].strftime('%Y-%m'),
                'end': date_range[1].strftime('%Y-%m')
            }
        }

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