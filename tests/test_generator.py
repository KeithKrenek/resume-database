# test_generator.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import shutil
from src.database import ResumeDatabase
from src.generator import ResumeGenerator, GenerationConfig
from src.pdf_generator import PDFGenerator
from test_data_helper import setup_test_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_output(content: str, filename: str) -> None:
    """Save generated content to file"""
    output_dir = Path("exports")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / filename, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Test the resume generation functionality"""
    # Initialize test directory
    test_dir = Path("test_data")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Initialize database and load test data
    db = ResumeDatabase(test_dir)
    test_entries = setup_test_data(db)
    
    # Initialize generator
    generator = ResumeGenerator(db)
    
    print("\n=== Testing Resume Generation ===\n")
    
    # Test 1: Role-specific HTML resume
    print("Generating role-specific HTML resume (ML Engineer)...")
    config = GenerationConfig(
        role="ml_engineer",
        required_skills=["Python", "Machine Learning"],
        preferred_skills=["TensorFlow", "Deep Learning"],
        detail_level="detailed",
        include_metrics=True,
        format="html"
    )
    
    resume = generator.generate_resume(config)
    save_output(resume, "ml_engineer_resume.html")
    print("Saved ML Engineer resume to 'exports/ml_engineer_resume.html'")
    
    # Get scored and sorted entries for PDF generation
    scored_entries = generator._score_entries(config)
    sorted_entries = generator._sort_entries(scored_entries, config.sort_by)
    
    print("\nGenerating PDF resume...")
    pdf_generator = PDFGenerator()
    output_path = Path("exports/ml_engineer_resume.pdf")
    
    # Prepare entries for PDF generation
    formatted_entries = []
    for _, entry, _ in sorted_entries:
        # Format description based on role variations
        if config.role and 'variations' in entry and config.role in entry['variations']:
            description = entry['variations'][config.role][config.detail_level]
        else:
            description = entry['core']
            
        formatted_entries.append({
            'company': entry.get('company', 'Independent'),
            'dates': entry['dates'],
            'description': description,
            'metrics': entry.get('metrics', []),
            'skills': entry.get('skills', [])
        })
    
    # Generate PDF with properly formatted entries
    pdf_generator.generate_pdf(
        entries=formatted_entries,
        config={
            'role': config.role,
            'required_skills': config.required_skills,
            'preferred_skills': config.preferred_skills,
            'detail_level': config.detail_level,
            'include_metrics': config.include_metrics
        },
        output_path=output_path
    )
    print("Saved ML Engineer PDF resume to 'exports/ml_engineer_resume.pdf'")
    
    # Test 2: Time-window filtered HTML resume
    print("\nGenerating recent experience HTML resume...")
    config = GenerationConfig(
        time_window=1,  # Last year only
        sort_by="date",
        format="html"
    )
    
    resume = generator.generate_resume(config)
    save_output(resume, "recent_experience.html")
    print("Saved recent experience resume to 'exports/recent_experience.html'")
    
    # Test 3: Impact-focused HTML resume
    print("\nGenerating impact-focused HTML resume...")
    config = GenerationConfig(
        sort_by="impact",
        include_metrics=True,
        detail_level="detailed",
        format="html"
    )
    
    resume = generator.generate_resume(config)
    save_output(resume, "impact_focused.html")
    print("Saved impact-focused resume to 'exports/impact_focused.html'")

if __name__ == "__main__":
    main()