# src/analytics.py

from typing import Dict, List, Optional, Set, Counter
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
import logging
from pathlib import Path
import json
import calendar
import re

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a search result with relevance score"""
    entry_id: str
    score: float
    highlights: Dict[str, List[str]]
    entry_data: Dict

    def __str__(self) -> str:
        return f"Entry {self.entry_id} (Score: {self.score:.2f})"

class SearchAnalytics:
    """Advanced search and analytics for resume entries"""
    
    def __init__(self, database):
        self.db = database
        self._build_search_index()

    def _build_search_index(self) -> None:
        """Build search indices for efficient querying"""
        self.text_index = defaultdict(list)  # word -> [(entry_id, field, position)]
        self.skill_index = defaultdict(set)  # skill -> {entry_id}
        self.date_index = []  # sorted list of (date, entry_id) tuples
        self.company_index = defaultdict(list)  # company -> [(entry_id, start_date)]
        
        for entry_id, entry in self.db.entries.items():
            # Index text content
            self._index_text(entry_id, 'core', entry['core'])
            for field in ['methodology', 'impact']:
                if field in entry:
                    for item in entry[field]:
                        self._index_text(entry_id, field, item)
            
            # Index skills
            for skill in entry.get('skills', []):
                self.skill_index[skill.lower()].add(entry_id)
            
            # Index dates
            start_date = datetime.strptime(entry['dates']['start'], '%Y-%m')
            self.date_index.append((start_date, entry_id))
            
            # Index company
            if 'company' in entry:
                self.company_index[entry['company']].append((entry_id, start_date))
        
        # Sort date index
        self.date_index.sort(key=lambda x: x[0])

    def _index_text(self, entry_id: str, field: str, text: str) -> None:
        """Index words in text content"""
        words = re.findall(r'\b\w+\b', text.lower())
        for pos, word in enumerate(words):
            self.text_index[word].append((entry_id, field, pos))

    def search(self, 
              query: str, 
              filters: Optional[Dict] = None,
              sort_by: str = 'relevance') -> List[SearchResult]:
        """
        Search entries with advanced text matching and filtering
        
        Args:
            query: Search query
            filters: Optional filters (skills, date_range, companies)
            sort_by: How to sort results ('relevance', 'date', 'company')
        """
        # Get initial matches
        matches = self._text_search(query)
        
        # Apply filters
        if filters:
            matches = self._apply_filters(matches, filters)
        
        # Sort results
        if sort_by == 'date':
            matches.sort(key=lambda x: datetime.strptime(
                self.db.entries[x.entry_id]['dates']['start'], '%Y-%m'
            ), reverse=True)
        elif sort_by == 'company':
            matches.sort(key=lambda x: self.db.entries[x.entry_id].get('company', ''))
            
        return matches

    def _text_search(self, query: str) -> List[SearchResult]:
        """Perform text-based search"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        scores = defaultdict(float)
        highlights = defaultdict(lambda: defaultdict(list))
        
        for word in query_words:
            for entry_id, field, pos in self.text_index[word]:
                # Score based on field importance
                field_weight = {
                    'core': 1.0,
                    'methodology': 0.7,
                    'impact': 0.8
                }.get(field, 0.5)
                
                scores[entry_id] += field_weight
                
                # Get context for highlighting
                entry_text = self.db.entries[entry_id].get(field, '')
                if isinstance(entry_text, str):
                    context = self._get_context(entry_text, word)
                    if context:
                        highlights[entry_id][field].append(context)
        
        # Create search results
        results = []
        for entry_id, score in scores.items():
            results.append(SearchResult(
                entry_id=entry_id,
                score=score,
                highlights=dict(highlights[entry_id]),
                entry_data=self.db.entries[entry_id]
            ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def _get_context(self, text: str, word: str, context_words: int = 5) -> Optional[str]:
        """Get context around a matched word"""
        word_pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        match = word_pattern.search(text)
        if match:
            words = text.split()
            word_pos = None
            for i, w in enumerate(words):
                if word_pattern.search(w):
                    word_pos = i
                    break
                    
            if word_pos is not None:
                start = max(0, word_pos - context_words)
                end = min(len(words), word_pos + context_words + 1)
                context = ' '.join(words[start:end])
                return f"...{context}..."
        return None

    def _apply_filters(self, results: List[SearchResult], 
                      filters: Dict) -> List[SearchResult]:
        """Apply filters to search results"""
        filtered = []
        
        for result in results:
            entry = result.entry_data
            
            # Skills filter
            if 'skills' in filters:
                required_skills = set(s.lower() for s in filters['skills'])
                entry_skills = set(s.lower() for s in entry.get('skills', []))
                if not required_skills.issubset(entry_skills):
                    continue
            
            # Date range filter
            if 'date_range' in filters:
                start, end = filters['date_range']
                entry_start = datetime.strptime(entry['dates']['start'], '%Y-%m')
                if start and entry_start < datetime.strptime(start, '%Y-%m'):
                    continue
                if end and entry_start > datetime.strptime(end, '%Y-%m'):
                    continue
            
            # Company filter
            if 'companies' in filters and entry.get('company') not in filters['companies']:
                continue
                
            filtered.append(result)
            
        return filtered

    def analyze_experience(self) -> Dict:
        """Generate comprehensive experience analytics"""
        analytics = {
            'timeline': self._analyze_timeline(),
            'skills': self._analyze_skills(),
            'companies': self._analyze_companies(),
            'growth': self._analyze_growth(),
            'impact': self._analyze_impact()
        }
        return analytics

    def _analyze_timeline(self) -> Dict:
        """Analyze experience timeline"""
        timeline = defaultdict(int)
        skill_timeline = defaultdict(lambda: defaultdict(int))
        
        for entry_id, entry in self.db.entries.items():
            start = datetime.strptime(entry['dates']['start'], '%Y-%m')
            end = (datetime.strptime(entry['dates']['end'], '%Y-%m')
                  if entry['dates'].get('end')
                  else datetime.now())
            
            # Count months of experience
            current = start
            while current <= end:
                key = current.strftime('%Y-%m')
                timeline[key] += 1
                
                # Track skills over time
                for skill in entry.get('skills', []):
                    skill_timeline[skill][key] += 1
                    
                current = datetime(
                    current.year + (current.month == 12),
                    (current.month % 12) + 1,
                    1
                )
        
        return {
            'monthly_activity': dict(timeline),
            'skill_progression': {
                skill: dict(months)
                for skill, months in skill_timeline.items()
            }
        }

    def _analyze_skills(self) -> Dict:
        """Analyze skills usage and relationships"""
        skill_freq = Counter()
        skill_pairs = Counter()
        skill_growth = defaultdict(list)
        
        for entry_id, entry in self.db.entries.items():
            skills = entry.get('skills', [])
            start_date = datetime.strptime(entry['dates']['start'], '%Y-%m')
            
            # Count individual skills
            skill_freq.update(skills)
            
            # Track skill pairs
            for i, skill1 in enumerate(skills):
                for skill2 in skills[i+1:]:
                    pair = tuple(sorted([skill1, skill2]))
                    skill_pairs[pair] += 1
            
            # Track skill growth
            for skill in skills:
                skill_growth[skill].append(start_date)
        
        # Calculate skill growth trends
        growth_trends = {}
        for skill, dates in skill_growth.items():
            dates.sort()
            growth_trends[skill] = {
                'first_use': dates[0].strftime('%Y-%m'),
                'frequency': len(dates),
                'recent_uses': len([d for d in dates if 
                    (datetime.now() - d).days <= 365])
            }
        
        return {
            'frequency': dict(skill_freq),
            'common_pairs': {f"{s1}, {s2}": count 
                           for (s1, s2), count in skill_pairs.most_common()},
            'growth_trends': growth_trends
        }

    def _analyze_companies(self) -> Dict:
        """Analyze company experience"""
        company_stats = defaultdict(lambda: {
            'duration': 0,
            'roles': set(),
            'skills': set(),
            'projects': 0
        })
        
        for entry_id, entry in self.db.entries.items():
            company = entry.get('company')
            if not company:
                continue
                
            # Calculate duration
            start = datetime.strptime(entry['dates']['start'], '%Y-%m')
            end = (datetime.strptime(entry['dates']['end'], '%Y-%m')
                  if entry['dates'].get('end')
                  else datetime.now())
            duration = (end.year - start.year) * 12 + end.month - start.month
            
            stats = company_stats[company]
            stats['duration'] += duration
            stats['skills'].update(entry.get('skills', []))
            stats['projects'] += 1
            
            if 'variations' in entry:
                stats['roles'].update(entry['variations'].keys())
        
        # Convert sets to lists for JSON serialization
        return {
            company: {
                'duration': stats['duration'],
                'roles': list(stats['roles']),
                'skills': list(stats['skills']),
                'projects': stats['projects']
            }
            for company, stats in company_stats.items()
        }

    def _analyze_growth(self) -> Dict:
        """Analyze professional growth and progression"""
        skill_progression = defaultdict(list)
        role_progression = []
        proficiency_growth = defaultdict(list)
        
        for entry_id, entry in self.db.entries.items():
            date = datetime.strptime(entry['dates']['start'], '%Y-%m')
            
            # Track skill acquisition
            for skill in entry.get('skills', []):
                skill_progression[skill].append(date)
            
            # Track role changes
            if 'variations' in entry:
                for role in entry['variations'].keys():
                    role_progression.append((date, role))
            
            # Track proficiency development
            for detail in entry.get('technical_details', []):
                proficiency_growth[detail['category']].append({
                    'date': date.strftime('%Y-%m'),
                    'proficiency': detail['proficiency']
                })
        
        # Sort and format progressions
        skill_timeline = {
            skill: [d.strftime('%Y-%m') for d in sorted(dates)]
            for skill, dates in skill_progression.items()
        }
        
        role_timeline = [
            {'date': date.strftime('%Y-%m'), 'role': role}
            for date, role in sorted(role_progression)
        ]
        
        return {
            'skill_timeline': skill_timeline,
            'role_timeline': role_timeline,
            'proficiency_growth': dict(proficiency_growth)
        }

    def _analyze_impact(self) -> Dict:
        """Analyze impact and achievements"""
        impact_metrics = defaultdict(list)
        achievement_types = Counter()
        impact_areas = defaultdict(list)
        
        for entry_id, entry in self.db.entries.items():
            # Analyze metrics
            for metric in entry.get('metrics', []):
                impact_metrics[metric['category']].append({
                    'value': metric['value'],
                    'context': metric['context'],
                    'date': entry['dates']['start']
                })
                impact_areas[metric['impact_area']].append(metric['value'])
            
            # Analyze impact statements
            for impact in entry.get('impact', []):
                # Categorize impact statements
                if any(word in impact.lower() 
                      for word in ['increased', 'improved', 'enhanced']):
                    achievement_types['improvement'] += 1
                elif any(word in impact.lower() 
                        for word in ['created', 'developed', 'built']):
                    achievement_types['creation'] += 1
                elif any(word in impact.lower() 
                        for word in ['led', 'managed', 'coordinated']):
                    achievement_types['leadership'] += 1
        
        return {
            'metrics_by_category': dict(impact_metrics),
            'achievement_types': dict(achievement_types),
            'impact_areas': dict(impact_areas)
        }