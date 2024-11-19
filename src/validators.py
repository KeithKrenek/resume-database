# src/validators.py

from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
import re
from dataclasses import dataclass
import logging
from enum import Enum
from jsonschema import validate

logger = logging.getLogger(__name__)

# Original JSON Schema (keep this for backward compatibility)
ENTRY_SCHEMA = {
    "type": "object",
    "required": ["core", "dates"],
    "properties": {
        "id": {"type": "string"},
        "core": {"type": "string", "minLength": 10},
        "dates": {
            "type": "object",
            "required": ["start"],
            "properties": {
                "start": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
                "end": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
                "status": {"type": "string", "enum": ["completed", "ongoing"]}
            }
        },
        "category": {"type": "string"},
        "company": {"type": "string"},
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "metrics": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["value", "context", "category", "timeframe", "impact_area"],
                "properties": {
                    "value": {"type": "string"},
                    "context": {"type": "string"},
                    "verified": {"type": "boolean"},
                    "category": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "impact_area": {"type": "string"}
                }
            }
        },
        "technical_details": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "detail", "proficiency"],
                "properties": {
                    "category": {"type": "string"},
                    "detail": {"type": "string"},
                    "proficiency": {"type": "string"}
                }
            }
        }
    }
}

# Original validation function (keep this for backward compatibility)
def validate_entry_schema(entry_data: Dict[str, Any]) -> bool:
    """
    Validate entry data against schema
    
    Args:
        entry_data: Dictionary containing entry data
        
    Returns:
        bool: True if valid, raises ValidationError if invalid
    """
    try:
        validate(instance=entry_data, schema=ENTRY_SCHEMA)
        return True
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise

# New validation system
class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"

@dataclass
class ValidationResult:
    """Represents a single validation finding"""
    level: ValidationLevel
    field: str
    message: str
    context: Optional[str] = None

    def __str__(self) -> str:
        ctx = f" ({self.context})" if self.context else ""
        return f"{self.level.value.upper()}: {self.field} - {self.message}{ctx}"

class EnhancedValidator:
    """Advanced validation system for resume entries"""
    
    def __init__(self):
        self.common_skills = self._load_common_skills()
        self.skill_patterns = self._compile_skill_patterns()
        self.metric_patterns = self._compile_metric_patterns()

    def _load_common_skills(self) -> Set[str]:
        """Load common skill names (could be expanded to load from a file)"""
        return {
            "Python", "JavaScript", "Java", "C++", "SQL",
            "Machine Learning", "Data Science", "Deep Learning",
            "Project Management", "Leadership", "Communication",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "React", "Angular", "Vue.js", "Node.js", "Django",
            "TensorFlow", "PyTorch", "Scikit-learn", "Pandas",
            "Git", "CI/CD", "Agile", "Scrum"
        }

    def _compile_skill_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for skill validation"""
        return {
            'version_number': re.compile(r'\d+(\.\d+)*'),
            'framework_version': re.compile(r'[A-Za-z]+\s*\d+(\.\d+)*'),
            'abbreviation': re.compile(r'^[A-Z]{2,}(\.[A-Z]{2,})*$')
        }

    def _compile_metric_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for metric validation"""
        return {
            'percentage': re.compile(r'^[+-]?\d+(\.\d+)?%$'),
            'money': re.compile(r'^\$\d{1,3}(,\d{3})*(\.\d{2})?[KMB]?$'),
            'number': re.compile(r'^\d{1,3}(,\d{3})*(\.\d+)?[KMB]?$')
        }

    def validate_entry(self, entry_data: Dict) -> List[ValidationResult]:
        """Perform comprehensive validation of an entry"""
        results = []
        
        # Basic structure validation
        results.extend(self._validate_structure(entry_data))
        
        # Content validation
        results.extend(self._validate_core_content(entry_data))
        results.extend(self._validate_dates(entry_data))
        results.extend(self._validate_skills(entry_data))
        results.extend(self._validate_metrics(entry_data))
        results.extend(self._validate_variations(entry_data))
        
        # Quality checks
        results.extend(self._check_quality(entry_data))
        
        return results

    def _validate_structure(self, data: Dict) -> List[ValidationResult]:
        """Validate basic structure requirements"""
        results = []
        
        required_fields = {'core', 'dates', 'skills'}
        missing = required_fields - set(data.keys())
        if missing:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="structure",
                message=f"Missing required fields: {', '.join(missing)}"
            ))
        
        return results

    def _validate_core_content(self, data: Dict) -> List[ValidationResult]:
        """Validate core description content"""
        results = []
        core = data.get('core', '')
        
        # Length checks
        if len(core) < 20:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="core",
                message="Core description too short (minimum 20 characters)"
            ))
        elif len(core) > 500:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                field="core",
                message="Core description might be too long"
            ))
        
        # Content quality checks
        if core.count(',') == 0:
            results.append(ValidationResult(
                level=ValidationLevel.SUGGESTION,
                field="core",
                message="Consider using commas to break up complex achievements"
            ))
        
        if not any(word in core.lower() for word in ['led', 'developed', 'created', 'implemented', 'managed']):
            results.append(ValidationResult(
                level=ValidationLevel.SUGGESTION,
                field="core",
                message="Consider starting with strong action verbs"
            ))
        
        return results

    def _validate_dates(self, data: Dict) -> List[ValidationResult]:
        """Validate date information"""
        results = []
        dates = data.get('dates', {})
        
        if not dates.get('start'):
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="dates.start",
                message="Start date is required"
            ))
        
        try:
            start_date = datetime.strptime(dates.get('start', ''), '%Y-%m')
            if dates.get('end'):
                end_date = datetime.strptime(dates['end'], '%Y-%m')
                if end_date < start_date:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        field="dates",
                        message="End date cannot be before start date"
                    ))
        except ValueError:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="dates",
                message="Invalid date format (use YYYY-MM)"
            ))
        
        return results

    def _validate_skills(self, data: Dict) -> List[ValidationResult]:
        """Validate skills content"""
        results = []
        skills = data.get('skills', [])
        
        if not skills:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="skills",
                message="At least one skill is required"
            ))
        
        # Check for unknown skills
        unknown_skills = set(skills) - self.common_skills
        if unknown_skills:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                field="skills",
                message=f"Uncommon skills found: {', '.join(unknown_skills)}",
                context="Consider standardizing or verifying spelling"
            ))
        
        # Check for skill name patterns
        for skill in skills:
            for pattern_name, pattern in self.skill_patterns.items():
                if pattern.match(skill):
                    results.append(ValidationResult(
                        level=ValidationLevel.SUGGESTION,
                        field="skills",
                        message=f"Consider standardizing format for {skill}",
                        context=f"Matches {pattern_name} pattern"
                    ))
        
        return results

    def _validate_metrics(self, data: Dict) -> List[ValidationResult]:
        """Validate metrics content"""
        results = []
        metrics = data.get('metrics', [])
        
        if not metrics:
            results.append(ValidationResult(
                level=ValidationLevel.SUGGESTION,
                field="metrics",
                message="Consider adding quantifiable metrics"
            ))
        
        for i, metric in enumerate(metrics):
            # Validate value format
            value = metric.get('value', '')
            if not any(pattern.match(value) for pattern in self.metric_patterns.values()):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field=f"metrics[{i}].value",
                    message=f"Unclear metric value format: {value}",
                    context="Consider using standard formats (%, $, or numbers)"
                ))
            
            # Validate context
            context = metric.get('context', '')
            if len(context) < 5:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field=f"metrics[{i}].context",
                    message="Metric context too brief",
                    context="Provide more detailed context"
                ))
        
        return results

    def _validate_variations(self, data: Dict) -> List[ValidationResult]:
        """Validate role variations"""
        results = []
        variations = data.get('variations', {})
        
        if not variations:
            results.append(ValidationResult(
                level=ValidationLevel.SUGGESTION,
                field="variations",
                message="Consider adding role-specific variations"
            ))
        
        for role, content in variations.items():
            if not all(k in content for k in ['short', 'medium', 'detailed']):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field=f"variations.{role}",
                    message="Missing one or more detail levels",
                    context="Should have short, medium, and detailed"
                ))
        
        return results

    def _check_quality(self, data: Dict) -> List[ValidationResult]:
        """Perform overall quality checks"""
        results = []
        
        # Check technical details
        if not data.get('technical_details'):
            results.append(ValidationResult(
                level=ValidationLevel.SUGGESTION,
                field="technical_details",
                message="Consider adding technical implementation details"
            ))
        
        # Check methodology
        if not data.get('methodology'):
            results.append(ValidationResult(
                level=ValidationLevel.SUGGESTION,
                field="methodology",
                message="Consider documenting methodologies used"
            ))
        
        # Check impact
        if not data.get('impact'):
            results.append(ValidationResult(
                level=ValidationLevel.SUGGESTION,
                field="impact",
                message="Consider documenting specific impacts and outcomes"
            ))
        
        return results