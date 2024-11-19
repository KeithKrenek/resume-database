# src/exporters.py

from typing import Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import json
import logging
from abc import ABC, abstractmethod
from .content_generator import ContentGenerator

logger = logging.getLogger(__name__)

class BaseExporter(ABC):
    """Abstract base class for resume exporters"""
    
    def __init__(self, database, output_dir: Path):
        self.db = database
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.content_generator = ContentGenerator(database)

    @abstractmethod
    def export(self, **kwargs) -> Path:
        """Export entries to file"""
        pass

    def _format_date_range(self, dates: Dict) -> str:
        """Format date range for display"""
        start = datetime.strptime(dates['start'], '%Y-%m').strftime('%b %Y')
        if dates.get('end'):
            end = datetime.strptime(dates['end'], '%Y-%m').strftime('%b %Y')
        else:
            end = 'Present'
        return f"{start} - {end}"

class MarkdownExporter(BaseExporter):
    """Exports resume content in Markdown format"""
    
    def export(self, 
               role: Optional[str] = None,
               categories: Optional[List[str]] = None,
               detail_level: str = 'detailed',
               include_metrics: bool = True) -> Path:
        """
        Export entries as Markdown
        
        Args:
            role: Optional role for role-specific content
            categories: Optional list of categories to include
            detail_level: Level of detail ('short', 'medium', 'detailed')
            include_metrics: Whether to include metrics
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"resume_{timestamp}.md"
        
        content = []
        
        # Add header
        content.append("# Professional Experience\n")
        
        if role:
            # Use role-specific content
            entries = self.content_generator.generate_role_content(
                role=role,
                detail_level=detail_level
            )
            content.append(f"## {role.replace('_', ' ').title()} Experience\n")
        else:
            # Use raw entries filtered by category
            entries = []
            for entry_id, entry in self.db.entries.items():
                if not categories or entry.get('category') in categories:
                    entries.append(entry)
            
            # Sort by date (most recent first)
            entries.sort(
                key=lambda x: datetime.strptime(x['dates']['start'], '%Y-%m'),
                reverse=True
            )

        # Format entries
        for entry in entries:
            # Company and date
            company = entry.get('company', '')
            date_range = self._format_date_range(entry['dates'])
            content.append(f"### {company}")
            content.append(f"*{date_range}*\n")
            
            # Description
            if role:
                description = entry['description']  # Already formatted for role
            else:
                description = entry['core']
            content.append(description + "\n")
            
            # Metrics (if included and available)
            if include_metrics and entry.get('metrics'):
                content.append("**Key Achievements:**")
                for metric in entry['metrics']:
                    content.append(f"- {metric['value']} {metric['context']}")
                content.append("")
            
            # Skills
            if entry.get('skills'):
                content.append("**Skills:** " + ", ".join(entry['skills']) + "\n")

        # Write to file
        with open(output_file, 'w') as f:
            f.write("\n".join(content))
            
        return output_file

class JSONExporter(BaseExporter):
    """Exports resume content in JSON format"""
    
    def export(self, 
               structure: str = 'chronological',
               include_all_fields: bool = True) -> Path:
        """
        Export entries as JSON
        
        Args:
            structure: How to structure the export ('chronological', 'by_category', 'by_company')
            include_all_fields: Whether to include all fields or just core fields
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"resume_export_{timestamp}.json"
        
        if structure == 'chronological':
            export_data = self._export_chronological(include_all_fields)
        elif structure == 'by_category':
            export_data = self._export_by_category(include_all_fields)
        elif structure == 'by_company':
            export_data = self._export_by_company(include_all_fields)
        else:
            raise ValueError(f"Unknown structure: {structure}")
            
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        return output_file
    
    def _export_chronological(self, include_all_fields: bool) -> Dict:
        """Export entries in chronological order"""
        entries = []
        for entry_id, entry in self.db.entries.items():
            if include_all_fields:
                entries.append(entry)
            else:
                entries.append({
                    'core': entry['core'],
                    'dates': entry['dates'],
                    'company': entry.get('company', ''),
                    'skills': entry.get('skills', [])
                })
        
        # Sort by date (most recent first)
        entries.sort(
            key=lambda x: datetime.strptime(x['dates']['start'], '%Y-%m'),
            reverse=True
        )
        
        return {
            'format': 'chronological',
            'generated_at': datetime.now().isoformat(),
            'entries': entries
        }
    
    def _export_by_category(self, include_all_fields: bool) -> Dict:
        """Export entries organized by category"""
        categories = {}
        for entry_id, entry in self.db.entries.items():
            category = entry.get('category', 'uncategorized')
            if category not in categories:
                categories[category] = []
                
            if include_all_fields:
                categories[category].append(entry)
            else:
                categories[category].append({
                    'core': entry['core'],
                    'dates': entry['dates'],
                    'company': entry.get('company', ''),
                    'skills': entry.get('skills', [])
                })
        
        # Sort entries within each category
        for category in categories:
            categories[category].sort(
                key=lambda x: datetime.strptime(x['dates']['start'], '%Y-%m'),
                reverse=True
            )
        
        return {
            'format': 'by_category',
            'generated_at': datetime.now().isoformat(),
            'categories': categories
        }
    
    def _export_by_company(self, include_all_fields: bool) -> Dict:
        """Export entries organized by company"""
        companies = {}
        for entry_id, entry in self.db.entries.items():
            company = entry.get('company', 'independent')
            if company not in companies:
                companies[company] = []
                
            if include_all_fields:
                companies[company].append(entry)
            else:
                companies[company].append({
                    'core': entry['core'],
                    'dates': entry['dates'],
                    'category': entry.get('category', ''),
                    'skills': entry.get('skills', [])
                })
        
        # Sort entries within each company
        for company in companies:
            companies[company].sort(
                key=lambda x: datetime.strptime(x['dates']['start'], '%Y-%m'),
                reverse=True
            )
        
        return {
            'format': 'by_company',
            'generated_at': datetime.now().isoformat(),
            'companies': companies
        }