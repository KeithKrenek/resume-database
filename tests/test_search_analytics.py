# test_search_analytics.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import shutil
from src.database import ResumeDatabase
from src.analytics import SearchAnalytics
from test_data_helper import setup_test_data
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test the search and analytics functionality"""
    # Initialize test directory
    test_dir = Path("test_data")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Initialize database and load test data
    db = ResumeDatabase(test_dir)
    test_entries = setup_test_data(db)
    
    # Initialize analytics
    analytics = SearchAnalytics(db)
    
    print("\n=== Testing Search Functionality ===\n")
    
    # Test simple search
    print("Searching for 'machine learning'...")
    results = analytics.search("machine learning")
    print("\nSearch results:")
    for result in results:
        print(f"\n{result}")
        for field, highlights in result.highlights.items():
            print(f"  In {field}:")
            for highlight in highlights:
                print(f"    {highlight}")
    
    # Test filtered search
    print("\nSearching with filters...")
    filters = {
        'skills': ['Python'],
        'date_range': ('2023-01', '2024-12')
    }
    results = analytics.search(
        "development",
        filters=filters,
        sort_by='date'
    )
    print(f"\nFound {len(results)} filtered results")
    for result in results:
        entry = result.entry_data
        print(f"\n- {entry['core']}")
        print(f"  Date: {entry['dates']['start']}")
        print(f"  Skills: {', '.join(entry['skills'])}")
    
    print("\n=== Testing Analytics Functionality ===\n")
    
    # Generate comprehensive analytics
    analytics_data = analytics.analyze_experience()
    
    # Display timeline analysis
    print("Timeline Analysis:")
    timeline = analytics_data['timeline']['monthly_activity']
    if timeline:
        print(f"- Activity spans from {min(timeline.keys())} to {max(timeline.keys())}")
        print(f"- Peak activity: {max(timeline.values())} concurrent projects")
    
    # Display skills analysis
    print("\nSkills Analysis:")
    skills = analytics_data['skills']['frequency']
    if skills:
        print("Top skills by frequency:")
        for skill, count in sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"- {skill}: {count} entries")
    
    # Display company analysis
    print("\nCompany Analysis:")
    companies = analytics_data['companies']
    for company, stats in companies.items():
        print(f"\n{company}:")
        print(f"- Duration: {stats['duration']} months")
        print(f"- Projects: {stats['projects']}")
        print(f"- Unique skills: {len(stats['skills'])}")
    
    # Display growth analysis
    print("\nGrowth Analysis:")
    growth = analytics_data['growth']
    if growth['role_timeline']:
        print("\nRole progression:")
        for role_entry in growth['role_timeline']:
            print(f"- {role_entry['date']}: {role_entry['role']}")
    
    # Display impact analysis
    print("\nImpact Analysis:")
    impact = analytics_data['impact']
    if impact['achievement_types']:
        print("\nAchievement distribution:")
        for type_name, count in impact['achievement_types'].items():
            print(f"- {type_name}: {count}")

if __name__ == "__main__":
    main()