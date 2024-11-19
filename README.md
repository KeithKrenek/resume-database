# Resume Database System

A sophisticated Python-based system for managing, querying, and generating role-specific content from structured professional experience entries. This system provides a robust foundation for maintaining and leveraging career accomplishments effectively.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

The Resume Database System helps professionals maintain and leverage their career accomplishments through:
- 📝 Structured storage of professional experiences
- 🎯 Role-specific content generation
- 🔍 Advanced searching and filtering
- 📊 Experience analytics and insights
- 📄 Multiple export formats (JSON, Markdown, PDF)
- ✅ Comprehensive data validation

## Features

### Core Functionality
- **Structured Data Storage**: Individual JSON files for each entry with comprehensive schema validation
- **Advanced Querying**: Multi-criteria search with boolean logic and relevance scoring
- **Role-Specific Content**: Generate tailored content for different roles and contexts
- **Data Validation**: Comprehensive validation system with multiple validation levels
- **Version Control**: Track changes and maintain entry history
- **Export System**: Generate resumes in multiple formats (PDF, Markdown, JSON)

### Advanced Features
- **Intelligent Search**
  - Full-text search with relevance scoring
  - Skills and technology matching
  - Date range filtering
  - Company and category filtering
  - Tag-based searching
  - Complex boolean queries

- **Content Generation**
  - Role-specific variations
  - Multiple detail levels
  - Automatic formatting
  - Context-aware content selection
  - Metric highlighting

- **Data Analytics**
  - Skill progression tracking
  - Experience timeline analysis
  - Impact measurement
  - Career trajectory visualization
  - Competency mapping

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager
- Git (for cloning the repository)

### Basic Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-database.git
cd resume-database
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the package:
```bash
# Basic installation
pip install -e .

# With development tools
pip install -e ".[dev]"

# With PDF export support
pip install -e ".[pdf]"

# Full installation (all features)
pip install -e ".[dev,pdf]"
```

## Usage

### Quick Start

```python
from resume_database import ResumeDatabase
from pathlib import Path

# Initialize database
db = ResumeDatabase(Path("data/entries"))

# Add an entry
entry = {
    "core": "Led development of machine learning system",
    "dates": {
        "start": "2024-01",
        "end": "2024-03",
        "status": "completed"
    },
    "category": "technical_projects",
    "company": "Tech Corp",
    "skills": ["Python", "Machine Learning"],
    "metrics": [
        {
            "value": "25%",
            "context": "improvement in model accuracy",
            "verified": True,
            "category": "performance",
            "timeframe": "3 months",
            "impact_area": "ml_systems"
        }
    ]
}

db.add_entry("PROJ001", entry)
```

### Advanced Usage

#### Complex Queries
```python
# Search with multiple criteria
results = db.query_entries(
    skills=["Python", "Machine Learning"],
    categories=["technical_projects"],
    companies=["Tech Corp"],
    tags=["AI/ML"],
    date_range=("2020-01", "2024-12")
)

# Generate role-specific content
ml_engineer_resume = db.generate_content(
    role="ml_engineer",
    required_skills=["Python", "Machine Learning"],
    detail_level="detailed"
)

# Export as PDF
db.export_pdf(
    output_path="resume.pdf",
    role="ml_engineer",
    include_metrics=True
)
```

#### Data Analytics
```python
# Analyze skill progression
skill_analysis = db.analyze_skills()
print(f"Top skills: {skill_analysis['top_skills']}")
print(f"Skill growth: {skill_analysis['skill_growth']}")

# Generate experience timeline
timeline = db.generate_timeline(
    group_by="company",
    include_metrics=True
)
```

## Data Structure

### Entry Format
```json
{
    "id": "PROJ001",
    "core": "Project description",
    "dates": {
        "start": "2024-01",
        "end": "2024-03",
        "status": "completed"
    },
    "category": "technical_projects",
    "company": "Company Name",
    "variations": {
        "ml_engineer": {
            "short": "Brief ML focus",
            "medium": "More detailed ML perspective",
            "detailed": "Complete ML narrative"
        }
    },
    "skills": ["Python", "Machine Learning"],
    "metrics": [
        {
            "value": "25%",
            "context": "improvement in accuracy",
            "verified": true,
            "category": "performance",
            "timeframe": "3 months",
            "impact_area": "ml_systems"
        }
    ],
    "technical_details": [
        {
            "category": "ml",
            "detail": "Custom model development",
            "proficiency": "expert"
        }
    ],
    "tags": ["AI/ML", "Python", "Data Science"]
}
```

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_database.py

# Generate coverage report
pytest --cov=src --cov-report=html tests/
```

### Code Quality
```bash
# Format code
black src/ tests/

# Check types
mypy src/

# Lint code
pylint src/

# Run all quality checks
make lint
```

### Documentation
```bash
# Generate documentation
make docs

# View documentation locally
make docs-serve
```

## Project Structure
```
resume-database/
├── data/                  # Data storage
│   └── entries/          # Individual JSON entries
├── src/                  # Source code
│   ├── database.py      # Database operations
│   ├── models.py        # Data models
│   ├── validators.py    # Validation logic
│   ├── pdf_generator.py # PDF generation
│   └── utils.py         # Utility functions
├── tests/                # Test suite
├── docs/                 # Documentation
└── examples/             # Usage examples
```

## Contributing

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Make your changes and commit:
   ```bash
   git commit -m 'Add AmazingFeature'
   ```
4. Push to your fork:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [Link to docs]
- Issues: [GitHub Issues]
- Email: [your.email@example.com]

## Acknowledgments

- JSON Schema for data validation
- ReportLab for PDF generation
- Python pathlib for file operations
- pytest for testing framework

## Roadmap

- [ ] GraphQL API
- [ ] Web interface
- [ ] Interactive visualization
- [ ] AI-powered content suggestions
- [ ] Multiple language support