from pathlib import Path
import sys
sys.path.append('src')
from database import ResumeDatabase

# Initialize database with path to entries directory
db = ResumeDatabase(Path("data"))

# Query entries
ai_entries = db.query_entries(
    tags=["AI/ML"],
    companies=["Draper"]
)

print(ai_entries)