# Resume Database System

A sophisticated Python-based system for managing, querying, and generating role-specific content from structured professional experience entries. This system provides a robust foundation for maintaining and leveraging career accomplishments effectively.

## Features

### Core Functionality
- 📝 JSON-based storage with individual entry files
- 🔍 Flexible and powerful querying capabilities
- 🎯 Role-specific content generation
- ✅ Comprehensive data validation
- 🔄 Automatic indexing for efficient searches
- 💾 Backup and recovery functionality

### Data Management
- Individual JSON files for each entry
- Structured data validation using JSON Schema
- Automated entry indexing for quick searches
- Date range filtering and validation
- Skills and category-based organization

### Query Capabilities
- Multi-criteria search functionality
- Date range filtering
- Skills and technology matching
- Company and category filtering
- Tag-based searching
- Complex boolean queries

### Data Validation
- JSON Schema validation
- Date format verification
- Required field checking
- Data type validation
- Cross-reference validation

## Installation

### Requirements
- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-database.git
cd resume-database
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the package and dependencies:
```bash
# For basic installation
pip install -e .

# For development installation (includes testing tools)
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```python
from resume_database import ResumeDatabase
from pathlib import Path

# Initialize the database
db = ResumeDatabase(Path("data/entries"))

# Add a new entry
entry_data = {
    "core": "Led development of machine learning system",
    "dates": {
        "start": "2024-01",
        "end": "2024-03",
        "status": "completed"
    },
    "category": "technical_projects",
    "company": "Tech Corp",
    "skills": ["Python", "Machine Learning", "Project Management"]
}

db.add_entry("PROJ001", entry_data)

# Query entries
ml_projects = db.query_entries(
    skills=["Machine Learning"],
    date_range=("2023-01", "2024-12")
)
```

### Advanced Querying

```python
# Multiple criteria query
results = db.query_entries(
    skills=["Python", "Machine Learning"],
    categories=["technical_projects"],
    companies=["Tech Corp"],
    tags=["AI/ML"],
    date_range=("2020-01", "2024-12")
)

# Process results
for entry in results:
    print(f"\nProject: {entry['core']}")
    print(f"Company: {entry.get('company', 'N/A')}")
    print(f"Skills: {', '.join(entry.get('skills', []))}")
```

### Backup and Recovery

```python
# Create a backup
db.backup_entries(Path("backups/2024-03"))

# Initialize from backup
backup_db = ResumeDatabase(Path("backups/2024-03"))
```

## Project Structure

```
resume-database/
├── data/
│   └── entries/          # Individual JSON entry files
├── src/
│   ├── __init__.py
│   ├── database.py       # Main database implementation
│   ├── models.py         # Data models
│   ├── validators.py     # Data validation
│   └── utils.py         # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   └── test_models.py
├── setup.py
└── README.md
```

## Entry Format

Each entry is stored as a JSON file with the following structure:

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
    "skills": ["Skill1", "Skill2"],
    "metrics": [
        {
            "value": "50%",
            "context": "improvement in efficiency",
            "verified": true,
            "category": "performance",
            "timeframe": "3 months",
            "impact_area": "productivity"
        }
    ],
    "technical_details": [
        {
            "category": "backend",
            "detail": "Python development",
            "proficiency": "expert"
        }
    ],
    "tags": ["Backend", "Python", "Automation"]
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/test_database.py
```

### Code Style

This project uses:
- Black for code formatting
- Flake8 for style guide enforcement

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- JSON Schema for data validation
- Python's pathlib for file operations
- pytest for testing framework

## Support

For support, please open an issue in the GitHub repository or contact [your.email@example.com](mailto:your.email@example.com).