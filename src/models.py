# src/models.py
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
import json

@dataclass
class Metric:
    """Represents a metric with validation and context"""
    value: str
    context: str
    verified: bool
    category: str
    timeframe: str
    impact_area: str

    def to_dict(self) -> Dict:
        """Convert metric to dictionary format"""
        return {
            "value": self.value,
            "context": self.context,
            "verified": self.verified,
            "category": self.category,
            "timeframe": self.timeframe,
            "impact_area": self.impact_area
        }

@dataclass
class TechnicalDetail:
    """Represents a technical detail with category and proficiency"""
    category: str
    detail: str
    proficiency: str

    def to_dict(self) -> Dict:
        """Convert technical detail to dictionary format"""
        return {
            "category": self.category,
            "detail": self.detail,
            "proficiency": self.proficiency
        }

@dataclass
class DateInfo:
    """Represents date information for entries"""
    start: str
    end: Optional[str] = None
    status: str = "completed"

    @property
    def start_date(self) -> datetime:
        return datetime.strptime(self.start, "%Y-%m")

    @property
    def end_date(self) -> Optional[datetime]:
        return datetime.strptime(self.end, "%Y-%m") if self.end else None

    def to_dict(self) -> Dict:
        """Convert date info to dictionary format"""
        return {
            "start": self.start,
            "end": self.end,
            "status": self.status
        }

class ResumeEntry:
    """Represents a single resume entry with full validation"""
    
    def __init__(self, entry_id: str, data: Dict):
        self.id = entry_id
        self.data = data
        self.dates = DateInfo(**data['dates'])
        self.core = data['core']
        self.category = data.get('category', '')
        self.company = data.get('company', '')
        self.skills = data.get('skills', [])
        self.metrics = [Metric(**m) for m in data.get('metrics', [])]
        self.technical_details = [
            TechnicalDetail(**t) for t in data.get('technical_details', [])
        ]
        self.validate()

    def validate(self) -> None:
        """Validate entry data completeness and correctness"""
        if not self.core:
            raise ValueError("Entry must have a core description")
        
        if not isinstance(self.skills, list):
            raise ValueError("Skills must be a list")
            
        if len(self.core) < 10:
            raise ValueError("Core description must be at least 10 characters")

    def to_dict(self) -> Dict:
        """Convert entry to dictionary format"""
        return {
            'id': self.id,
            'core': self.core,
            'dates': self.dates.to_dict(),
            'category': self.category,
            'company': self.company,
            'skills': self.skills,
            'metrics': [m.to_dict() for m in self.metrics],
            'technical_details': [t.to_dict() for t in self.technical_details],
            **{k: v for k, v in self.data.items() if k not in {
                'id', 'core', 'dates', 'category', 'company', 
                'skills', 'metrics', 'technical_details'
            }}
        }