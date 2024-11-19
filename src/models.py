# src/models.py
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from enum import Enum

class EntryStatus(Enum):
    """Status options for entries"""
    COMPLETED = "completed"
    ONGOING = "ongoing"
    PLANNED = "planned"

class Proficiency(Enum):
    """Proficiency levels for technical details"""
    EXPERT = "expert"
    ADVANCED = "advanced"
    INTERMEDIATE = "intermediate"
    BEGINNER = "beginner"

@dataclass
class Metric:
    """Represents a metric with validation and context"""
    value: str
    context: str
    verified: bool
    category: str
    timeframe: str
    impact_area: str

    def __post_init__(self) -> None:
        """Validate metric data after initialization"""
        if not self.value or not self.context:
            raise ValueError("Metric must have both value and context")
        if len(self.context) < 5:
            raise ValueError("Metric context must be descriptive (min 5 chars)")

    def to_dict(self) -> Dict[str, Any]:
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

    def __post_init__(self) -> None:
        """Validate technical detail data"""
        if not self.category or not self.detail:
            raise ValueError("Technical detail must have category and detail")
        if self.proficiency not in [p.value for p in Proficiency]:
            raise ValueError(f"Invalid proficiency level: {self.proficiency}")

    def to_dict(self) -> Dict[str, str]:
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
    status: str = EntryStatus.COMPLETED.value

    def __post_init__(self) -> None:
        """Validate date information"""
        try:
            start_date = datetime.strptime(self.start, "%Y-%m")
            if self.end:
                end_date = datetime.strptime(self.end, "%Y-%m")
                if end_date < start_date:
                    raise ValueError("End date cannot be before start date")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {e}")

        if self.status not in [s.value for s in EntryStatus]:
            raise ValueError(f"Invalid status: {self.status}")

    @property
    def start_date(self) -> datetime:
        return datetime.strptime(self.start, "%Y-%m")

    @property
    def end_date(self) -> Optional[datetime]:
        return datetime.strptime(self.end, "%Y-%m") if self.end else None

    @property
    def duration_months(self) -> int:
        """Calculate duration in months"""
        end = self.end_date or datetime.now()
        return ((end.year - self.start_date.year) * 12 + 
                end.month - self.start_date.month)

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert date info to dictionary format"""
        return {
            "start": self.start,
            "end": self.end,
            "status": self.status
        }

class ResumeEntry:
    """Represents a single resume entry with full validation"""
    
    def __init__(self, entry_id: str, data: Dict[str, Any]):
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
        self.tags = data.get('tags', [])
        self.validate()

    def validate(self) -> None:
        """Validate entry data completeness and correctness"""
        if not self.core:
            raise ValueError("Entry must have a core description")
        
        if not isinstance(self.skills, list):
            raise ValueError("Skills must be a list")
            
        if len(self.core) < 10:
            raise ValueError("Core description must be at least 10 characters")

        # Validate skills format
        for skill in self.skills:
            if not isinstance(skill, str) or len(skill) < 2:
                raise ValueError(f"Invalid skill format: {skill}")

        # Validate tags format
        for tag in self.tags:
            if not isinstance(tag, str) or len(tag) < 2:
                raise ValueError(f"Invalid tag format: {tag}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary format"""
        base_dict = {
            'id': self.id,
            'core': self.core,
            'dates': self.dates.to_dict(),
            'category': self.category,
            'company': self.company,
            'skills': self.skills,
            'metrics': [m.to_dict() for m in self.metrics],
            'technical_details': [t.to_dict() for t in self.technical_details],
            'tags': self.tags
        }
        
        # Add any additional fields from original data
        extra_fields = {
            k: v for k, v in self.data.items() 
            if k not in base_dict
        }
        
        return {**base_dict, **extra_fields}

    def __str__(self) -> str:
        """String representation of the entry"""
        return f"{self.company} - {self.core} ({self.dates.start})"