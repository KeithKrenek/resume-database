# src/pdf_generator.py

from typing import Dict, List, Optional, Set, Tuple
import logging
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Generates PDF resumes using ReportLab"""
    
    def __init__(self):
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Main title
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=20
        ))
        
        # Role target
        self.styles.add(ParagraphStyle(
            name='RoleTarget',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.gray,
            fontStyle='italic',
            spaceAfter=20
        ))
        
        # Section headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceBefore=15,
            spaceAfter=10
        ))
        
        # Company name
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Normal'],
            fontSize=14,
            fontWeight='bold',
            textColor=colors.HexColor('#1f2937')
        ))
        
        # Date range
        self.styles.add(ParagraphStyle(
            name='DateRange',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.gray,
            alignment=TA_RIGHT
        ))
        
        # Description
        self.styles.add(ParagraphStyle(
            name='Description',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=6,
            spaceAfter=8
        ))
        
        # Metrics header
        self.styles.add(ParagraphStyle(
            name='MetricsHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            fontWeight='bold',
            spaceBefore=6,
            spaceAfter=6
        ))
        
        # Skill tag
        self.styles.add(ParagraphStyle(
            name='SkillTag',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.gray
        ))
        
        # Meta info
        self.styles.add(ParagraphStyle(
            name='MetaInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_RIGHT,
            spaceBefore=20
        ))

    def generate_pdf(self, entries: List[Dict], config: Dict, output_path: Path) -> Path:
        """Generate PDF resume"""
        logger.info("Generating PDF with ReportLab...")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph("Professional Experience", self.styles['MainTitle']))
        
        # Role target
        if config.get('role'):
            story.append(Paragraph(
                f"Targeted for: {config['role']}", 
                self.styles['RoleTarget']
            ))
        
        # Required skills
        if config.get('required_skills'):
            story.append(Paragraph("Required Skills", self.styles['SectionHeader']))
            all_skills = self._collect_skills(entries)
            items = []
            for skill in config['required_skills']:
                status = "✓" if skill in all_skills else "✗"
                items.append(ListItem(
                    Paragraph(f"{status} {skill}", self.styles['Normal'])
                ))
            story.append(ListFlowable(items, bulletType='bullet'))
        
        # Preferred skills
        if config.get('preferred_skills'):
            story.append(Paragraph("Preferred Skills", self.styles['SectionHeader']))
            items = []
            for skill in config['preferred_skills']:
                status = "✓" if skill in all_skills else "○"
                items.append(ListItem(
                    Paragraph(f"{status} {skill}", self.styles['Normal'])
                ))
            story.append(ListFlowable(items, bulletType='bullet'))
        
        # Experience entries
        story.append(Paragraph("Experience", self.styles['SectionHeader']))
        
        for entry in self._format_entries(entries):
            # Company and date header
            data = [[
                Paragraph(entry['company'], self.styles['CompanyName']),
                Paragraph(entry['date_range'], self.styles['DateRange'])
            ]]
            t = Table(data, colWidths=[4*inch, 3*inch])
            t.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,0), 'LEFT'),
                ('ALIGN', (-1,-1), (-1,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            story.append(t)
            
            # Description
            story.append(Paragraph(entry['description'], self.styles['Description']))
            
            # Metrics
            if entry['metrics']:
                story.append(Paragraph("Key Achievements", self.styles['MetricsHeader']))
                items = []
                for metric in entry['metrics']:
                    items.append(ListItem(
                        Paragraph(
                            f"{metric['value']} {metric['context']}", 
                            self.styles['Normal']
                        )
                    ))
                story.append(ListFlowable(items, bulletType='bullet'))
            
            # Skills
            if entry['skills']:
                skills_text = ", ".join(entry['skills'])
                story.append(Paragraph(skills_text, self.styles['SkillTag']))
            
            story.append(Spacer(1, 20))
        
        # Meta info
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')}", 
            self.styles['MetaInfo']
        ))
        
        # Build PDF
        doc.build(story)
        logger.info(f"Successfully generated PDF at: {output_path}")
        
        return output_path

    def _format_entries(self, entries: List[Dict]) -> List[Dict]:
        """Format entries for PDF generation"""
        formatted_entries = []
        for entry in entries:
            formatted_entry = {
                'company': entry.get('company', 'Independent'),
                'date_range': self._format_date_range(entry['dates']),
                'description': entry.get('description', entry.get('core', '')),
                'metrics': [],
                'skills': entry.get('skills', [])
            }
            
            if 'metrics' in entry:
                formatted_entry['metrics'] = [
                    {
                        'value': m['value'],
                        'context': m['context']
                    }
                    for m in entry['metrics']
                ]
            
            formatted_entries.append(formatted_entry)
        return formatted_entries

    @staticmethod
    def _collect_skills(entries: List[Dict]) -> Set[str]:
        """Collect all skills from entries"""
        skills = set()
        for entry in entries:
            skills.update(entry.get('skills', []))
        return skills

    @staticmethod
    def _format_date_range(dates: Dict) -> str:
        """Format date range for display"""
        start = datetime.strptime(dates['start'], '%Y-%m').strftime('%b %Y')
        if dates.get('end'):
            end = datetime.strptime(dates['end'], '%Y-%m').strftime('%b %Y')
        else:
            end = 'Present'
        return f"{start} - {end}"