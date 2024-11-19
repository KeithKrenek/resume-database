# test_content_generator.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.database import ResumeDatabase
from src.content_generator import ContentGenerator
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_data(db: ResumeDatabase):
    """Set up test entries with role variations"""
    
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
            },
            "data_scientist": {
                "short": "Analyzed manufacturing data using ML",
                "medium": "Applied ML to manufacturing optimization",
                "detailed": "Conducted in-depth analysis of manufacturing data using machine learning techniques, identifying key optimization opportunities"
            }
        },
        "skills": ["Python", "Machine Learning", "Data Science"],
        "tags": ["AI/ML", "Manufacturing"],
        "metrics": [
            {
                "value": "25%",
                "context": "efficiency improvement",
                "verified": True,
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
            },
            "data_engineer": {
                "short": "Engineered data pipeline for analytics",
                "medium": "Built scalable data processing system",
                "detailed": "Designed and implemented scalable data pipeline processing 1M+ daily customer interactions"
            }
        },
        "skills": ["Python", "SQL", "Data Analysis"],
        "tags": ["Data", "Analytics"],
        "metrics": [
            {
                "value": "40%",
                "context": "increase in customer engagement",
                "verified": True,
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

def main():
    """Test the content generator functionality"""
    # Initialize database with test directory
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Initialize database and load test data
    db = ResumeDatabase(test_dir)
    test_entries = setup_test_data(db)
    
    # Initialize content generator
    generator = ContentGenerator(db)
    
    print("\n=== Testing Role-Specific Content Generation ===\n")
    
    # Get available roles
    roles = generator.get_roles()
    print(f"Available roles: {', '.join(roles)}\n")
    
    # For each role, generate different views
    for role in roles:
        print(f"\nGenerating content for role: {role}")
        
        # Get role summary
        summary = generator.generate_role_summary(role)
        print("\nRole Summary:")
        print(f"- Number of entries: {summary['count']}")
        print(f"- Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
        print(f"- Companies: {', '.join(summary['companies'])}")
        print(f"- Skills: {', '.join(summary['skills'])}")
        
        # Generate different detail levels
        for level in ['short', 'medium', 'detailed']:
            print(f"\n{level.capitalize()} descriptions:")
            entries = generator.generate_role_content(
                role=role,
                detail_level=level,
                limit=2  # Show top 2 entries
            )
            
            for entry in entries:
                print(f"\n- {entry['description']}")
                print(f"  Company: {entry['company']}")
                print(f"  Date: {entry['dates']['start']} to {entry['dates'].get('end', 'present')}")
                
                if level == 'detailed' and entry.get('metrics'):
                    print("  Key Metrics:")
                    for metric in entry['metrics']:
                        print(f"    * {metric['value']} {metric['context']}")

    # Test filtering capabilities
    print("\n=== Testing Filtering Capabilities ===\n")
    
    # Filter by skills
    print("Entries for data scientists with Python skills:")
    filtered_entries = generator.generate_role_content(
        role='data_scientist',
        skills_filter=['Python'],
        detail_level='medium'
    )
    
    for entry in filtered_entries:
        print(f"\n- {entry['description']}")
        print(f"  Skills: {', '.join(entry['skills'])}")

    # Filter by date range
    print("\nRecent entries for ML engineers (2024):")
    recent_entries = generator.generate_role_content(
        role='ml_engineer',
        date_range=('2024-01', '2024-12'),
        detail_level='short'
    )
    
    for entry in recent_entries:
        print(f"\n- {entry['description']}")
        print(f"  Date: {entry['dates']['start']} to {entry['dates'].get('end', 'present')}")

if __name__ == "__main__":
    main()