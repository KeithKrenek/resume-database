# test_exporters.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.database import ResumeDatabase
from src.exporters import MarkdownExporter, JSONExporter
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test the export functionality"""
    # Initialize database with test directory
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Initialize database
    db = ResumeDatabase(test_dir)
    
    # Create output directory for exports
    output_dir = Path("exports")
    output_dir.mkdir(exist_ok=True)
    
    print("\n=== Testing Export Functionality ===\n")
    
    # Test Markdown export
    md_exporter = MarkdownExporter(db, output_dir)
    
    # Export role-specific content
    print("Exporting role-specific Markdown...")
    md_file = md_exporter.export(
        role='data_scientist',
        detail_level='detailed',
        include_metrics=True
    )
    print(f"Created Markdown file: {md_file}")
    
    # Test JSON export with different structures
    json_exporter = JSONExporter(db, output_dir)
    
    # Chronological export
    print("\nExporting chronological JSON...")
    chrono_file = json_exporter.export(
        structure='chronological',
        include_all_fields=True
    )
    print(f"Created chronological JSON file: {chrono_file}")
    
    # Category-based export
    print("\nExporting category-based JSON...")
    category_file = json_exporter.export(
        structure='by_category',
        include_all_fields=False
    )
    print(f"Created category-based JSON file: {category_file}")
    
    # Company-based export
    print("\nExporting company-based JSON...")
    company_file = json_exporter.export(
        structure='by_company',
        include_all_fields=False
    )
    print(f"Created company-based JSON file: {company_file}")

if __name__ == "__main__":
    main()