# test_data_helper.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.database import ResumeDatabase
import json

def setup_test_data(db: ResumeDatabase):
    """Set up test entries for analytics testing"""
    
    # ML Project Entry
    entry1 = {
        "id": "TST001",
        "core": "Led development of machine learning system for manufacturing optimization",
        "dates": {
            "start": "2024-01",
            "end": "2024-03",
            "status": "completed"
        },
        "company": "Tech Corp",
        "category": "technical_projects",
        "variations": {
            "ml_engineer": {
                "short": "Built ML pipeline for manufacturing",
                "medium": "Developed ML system for process optimization",
                "detailed": "Led development of machine learning pipeline for manufacturing optimization, resulting in 25% efficiency improvement"
            }
        },
        "skills": ["Python", "Machine Learning", "TensorFlow", "Data Science"],
        "tags": ["AI/ML", "Manufacturing"],
        "impact": [
            "Improved manufacturing efficiency by 25%",
            "Reduced process variance by 40%",
            "Implemented automated decision system"
        ],
        "metrics": [
            {
                "value": "25%",
                "context": "efficiency improvement",
                "category": "performance",
                "timeframe": "3 months",
                "impact_area": "manufacturing"
            }
        ],
        "technical_details": [
            {
                "category": "ml",
                "detail": "Machine learning pipeline development",
                "proficiency": "expert"
            }
        ]
    }

    # Data Analysis Entry
    entry2 = {
        "id": "TST002",
        "core": "Developed data analytics platform for customer insights",
        "dates": {
            "start": "2023-06",
            "end": "2023-12",
            "status": "completed"
        },
        "company": "Data Corp",
        "category": "data_analysis",
        "variations": {
            "data_scientist": {
                "short": "Built customer analytics platform",
                "medium": "Developed comprehensive customer insights system",
                "detailed": "Created end-to-end analytics platform for customer behavior analysis, driving 40% increase in engagement"
            }
        },
        "skills": ["Python", "SQL", "Data Analysis", "Visualization"],
        "tags": ["Data", "Analytics"],
        "impact": [
            "Increased customer engagement by 40%",
            "Developed automated reporting system",
            "Created predictive models for customer behavior"
        ],
        "metrics": [
            {
                "value": "40%",
                "context": "increase in customer engagement",
                "category": "impact",
                "timeframe": "6 months",
                "impact_area": "business"
            }
        ],
        "technical_details": [
            {
                "category": "data",
                "detail": "Data pipeline development",
                "proficiency": "expert"
            }
        ]
    }

    # Add entries to database
    db.add_entry("TST001", entry1)
    db.add_entry("TST002", entry2)
    
    return [entry1, entry2]