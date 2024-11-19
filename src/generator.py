# src/generator.py

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import json
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    """Configuration for resume generation"""
    role: Optional[str] = None          # Target role
    max_entries: Optional[int] = None   # Max number of entries
    time_window: Optional[int] = None   # Years to include
    required_skills: List[str] = None   # Must-have skills
    preferred_skills: List[str] = None  # Nice-to-have skills
    detail_level: str = 'detailed'      # 'short', 'medium', 'detailed'
    include_metrics: bool = True        # Include quantitative metrics
    format: str = 'markdown'            # 'markdown', 'json', 'text'
    sort_by: str = 'date'              # 'date', 'relevance', 'impact'

class ResumeGenerator:
    """Generates targeted resumes and reports"""
    
    def __init__(self, database):
        self.db = database
        self._initialize_indices()

    def _initialize_indices(self) -> None:
        """Initialize scoring and relevance indices"""
        self.skill_importance = defaultdict(float)
        self.impact_scores = {}
        
        # Calculate skill importance based on recency and frequency
        now = datetime.now()
        for entry_id, entry in self.db.entries.items():
            start_date = datetime.strptime(entry['dates']['start'], '%Y-%m')
            months_ago = (now.year - start_date.year) * 12 + now.month - start_date.month
            recency_weight = 1.0 / (months_ago + 1)
            
            for skill in entry.get('skills', []):
                self.skill_importance[skill] += recency_weight
            
            # Calculate impact score based on metrics
            impact_score = 0
            for metric in entry.get('metrics', []):
                value = metric['value']
                if '%' in value:
                    try:
                        impact_score += float(value.strip('%')) / 100
                    except ValueError:
                        pass
            self.impact_scores[entry_id] = impact_score

    def generate_resume(self, config: GenerationConfig) -> str:
        """Generate a targeted resume based on configuration"""
        # Select and score entries
        scored_entries = self._score_entries(config)
        
        # Sort entries
        sorted_entries = self._sort_entries(scored_entries, config.sort_by)
        
        # Apply limits
        if config.max_entries:
            sorted_entries = sorted_entries[:config.max_entries]
            
        # Generate content
        if config.format == 'markdown':
            return self._generate_markdown(sorted_entries, config)
        elif config.format == 'json':
            return self._generate_json(sorted_entries, config)
        elif config.format == 'html':
            return self._generate_html(sorted_entries, config)
        else:
            return self._generate_text(sorted_entries, config)

    def _score_entries(self, config: GenerationConfig) -> List[tuple]:
        """Score entries based on relevance to configuration"""
        scored_entries = []
        
        for entry_id, entry in self.db.entries.items():
            # Skip entries outside time window
            if config.time_window:
                start_date = datetime.strptime(entry['dates']['start'], '%Y-%m')
                years_ago = (datetime.now() - start_date).days / 365
                if years_ago > config.time_window:
                    continue
            
            # Calculate base score
            score = 0.0
            
            # Score required skills
            if config.required_skills:
                entry_skills = set(s.lower() for s in entry.get('skills', []))
                required_skills = set(s.lower() for s in config.required_skills)
                if not required_skills.issubset(entry_skills):
                    continue
                score += len(required_skills)
            
            # Score preferred skills
            if config.preferred_skills:
                entry_skills = set(s.lower() for s in entry.get('skills', []))
                preferred_skills = set(s.lower() for s in config.preferred_skills)
                matching_preferred = preferred_skills.intersection(entry_skills)
                score += len(matching_preferred) * 0.5
            
            # Add impact score
            score += self.impact_scores.get(entry_id, 0) * 2
            
            # Score role-specific content
            if config.role and 'variations' in entry:
                if config.role in entry['variations']:
                    score += 1.0
            
            scored_entries.append((entry_id, entry, score))
        
        return scored_entries

    def _sort_entries(self, entries: List[tuple], sort_by: str) -> List[tuple]:
        """Sort entries based on specified criteria"""
        if sort_by == 'date':
            return sorted(
                entries,
                key=lambda x: datetime.strptime(x[1]['dates']['start'], '%Y-%m'),
                reverse=True
            )
        elif sort_by == 'relevance':
            return sorted(entries, key=lambda x: x[2], reverse=True)
        elif sort_by == 'impact':
            return sorted(
                entries,
                key=lambda x: self.impact_scores.get(x[0], 0),
                reverse=True
            )
        return entries

    def _generate_markdown(self, entries: List[tuple], config: GenerationConfig) -> str:
        """Generate markdown formatted resume"""
        lines = []
        
        # Header
        lines.append("# Professional Experience\n")
        
        if config.role:
            lines.append(f"*Targeted for: {config.role}*\n")
        
        # Skills summary
        all_skills = set()
        for _, entry, _ in entries:
            all_skills.update(entry.get('skills', []))
        
        if config.required_skills:
            lines.append("\n## Key Skills")
            lines.append("**Required Skills:**")
            for skill in config.required_skills:
                status = "✓" if skill in all_skills else "✗"
                lines.append(f"- {status} {skill}")
        
        if config.preferred_skills:
            lines.append("\n**Preferred Skills:**")
            for skill in config.preferred_skills:
                status = "✓" if skill in all_skills else "○"
                lines.append(f"- {status} {skill}")
        
        # Experience entries
        lines.append("\n## Experience\n")
        
        for entry_id, entry, score in entries:
            # Company and date
            company = entry.get('company', 'Independent')
            dates = entry['dates']
            date_str = self._format_date_range(dates)
            lines.append(f"### {company}")
            lines.append(f"*{date_str}*\n")
            
            # Description
            if config.role and 'variations' in entry:
                if config.role in entry['variations']:
                    description = entry['variations'][config.role][config.detail_level]
                else:
                    description = entry['core']
            else:
                description = entry['core']
            
            lines.append(description + "\n")
            
            # Metrics
            if config.include_metrics and entry.get('metrics'):
                lines.append("**Key Achievements:**")
                for metric in entry['metrics']:
                    lines.append(f"- {metric['value']} {metric['context']}")
                lines.append("")
            
            # Skills
            if entry.get('skills'):
                lines.append("**Skills:** " + ", ".join(entry['skills']) + "\n")
        
        return "\n".join(lines)

    def _generate_json(self, entries: List[tuple], config: GenerationConfig) -> str:
        """Generate JSON formatted resume"""
        resume_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "role": config.role,
                "required_skills": config.required_skills,
                "preferred_skills": config.preferred_skills
            },
            "entries": [
                {
                    "id": entry_id,
                    "company": entry.get('company'),
                    "dates": entry['dates'],
                    "description": (
                        entry['variations'][config.role][config.detail_level]
                        if config.role and 'variations' in entry 
                        and config.role in entry['variations']
                        else entry['core']
                    ),
                    "metrics": entry.get('metrics') if config.include_metrics else None,
                    "skills": entry.get('skills'),
                    "relevance_score": score
                }
                for entry_id, entry, score in entries
            ]
        }
        return json.dumps(resume_data, indent=2)


    def _generate_text(self, entries: List[tuple], config: GenerationConfig) -> str:
        """Generate plain text formatted resume"""
        lines = []
        
        # Header
        lines.append("PROFESSIONAL EXPERIENCE")
        lines.append("=" * 22 + "\n")
        
        if config.role:
            lines.append(f"Role: {config.role}\n")
        
        # Experience entries
        for entry_id, entry, score in entries:
            # Company and date
            company = entry.get('company', 'Independent')
            dates = entry['dates']
            date_str = self._format_date_range(dates)
            lines.append(f"{company}")
            lines.append(f"{date_str}\n")
            
            # Description
            if config.role and 'variations' in entry:
                if config.role in entry['variations']:
                    description = entry['variations'][config.role][config.detail_level]
                else:
                    description = entry['core']
            else:
                description = entry['core']
            
            lines.append(description + "\n")
            
            # Metrics
            if config.include_metrics and entry.get('metrics'):
                lines.append("Key Achievements:")
                for metric in entry['metrics']:
                    lines.append(f"* {metric['value']} {metric['context']}")
                lines.append("")
            
            # Skills
            if entry.get('skills'):
                lines.append("Skills: " + ", ".join(entry['skills']) + "\n")
            
            lines.append("-" * 50 + "\n")
        
        return "\n".join(lines)

    @staticmethod
    def _format_date_range(dates: Dict) -> str:
        """Format date range for display"""
        start = datetime.strptime(dates['start'], '%Y-%m').strftime('%b %Y')
        if dates.get('end'):
            end = datetime.strptime(dates['end'], '%Y-%m').strftime('%b %Y')
        else:
            end = 'Present'
        return f"{start} - {end}"

    def _generate_html(self, entries: List[tuple], config: GenerationConfig) -> str:
        """Generate HTML formatted resume with modern styling"""
        
        # Build content sections first
        sections = []
        
        # Add role target if specified
        if config.role:
            sections.append(f'<div class="role-target">Targeted for: {config.role}</div>')
        
        # Add skills summary if required/preferred skills specified
        if config.required_skills or config.preferred_skills:
            skills_section = ['<div class="skills-summary">']
            
            if config.required_skills:
                skills_section.append('<div class="required-skills">')
                skills_section.append('<h2>Required Skills</h2>')
                skills_section.append('<ul>')
                all_skills = {skill for _, entry, _ in entries 
                            for skill in entry.get('skills', [])}
                for skill in config.required_skills:
                    check = "✓" if skill in all_skills else "✗"
                    class_name = "skill-check" if skill in all_skills else "skill-missing"
                    skills_section.append(
                        f'<li><span class="{class_name}">{check}</span> {skill}</li>'
                    )
                skills_section.append('</ul>')
                skills_section.append('</div>')
            
            if config.preferred_skills:
                skills_section.append('<div class="preferred-skills">')
                skills_section.append('<h2>Preferred Skills</h2>')
                skills_section.append('<ul>')
                for skill in config.preferred_skills:
                    check = "✓" if skill in all_skills else "○"
                    class_name = "skill-check" if skill in all_skills else "skill-optional"
                    skills_section.append(
                        f'<li><span class="{class_name}">{check}</span> {skill}</li>'
                    )
                skills_section.append('</ul>')
                skills_section.append('</div>')
            
            skills_section.append('</div>')
            sections.append('\n'.join(skills_section))
        
        # Add experience entries
        sections.append('<h2>Experience</h2>')
        
        for entry_id, entry, score in entries:
            # Start entry
            entry_html = ['<div class="experience-entry">']
            
            # Company header
            company = entry.get('company', 'Independent')
            date_str = self._format_date_range(entry['dates'])
            entry_html.append('<div class="company-header">')
            entry_html.append(f'<span class="company-name">{company}</span>')
            entry_html.append(f'<span class="date-range">{date_str}</span>')
            entry_html.append('</div>')
            
            # Description
            if config.role and 'variations' in entry and config.role in entry['variations']:
                description = entry['variations'][config.role][config.detail_level]
            else:
                description = entry['core']
            entry_html.append(f'<div class="description">{description}</div>')
            
            # Metrics
            if config.include_metrics and entry.get('metrics'):
                entry_html.append('<div class="metrics">')
                entry_html.append('<h4>Key Achievements</h4>')
                entry_html.append('<ul>')
                for metric in entry['metrics']:
                    entry_html.append(
                        f'<li>{metric["value"]} {metric["context"]}</li>'
                    )
                entry_html.append('</ul>')
                entry_html.append('</div>')
            
            # Skills
            if entry.get('skills'):
                entry_html.append('<div class="skills">')
                entry_html.append('<div class="skills-list">')
                for skill in entry['skills']:
                    entry_html.append(f'<span class="skill-tag">{skill}</span>')
                entry_html.append('</div>')
                entry_html.append('</div>')
            
            # Close entry
            entry_html.append('</div>')
            sections.append('\n'.join(entry_html))
        
        # Combine all sections
        content = '\n'.join(sections)
        generation_date = datetime.now().strftime('%B %d, %Y')
        
        # Create the complete HTML document
        return f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Professional Resume</title>
        <style>
            :root {{
                --primary-color: #2563eb;
                --text-color: #1f2937;
                --secondary-color: #6b7280;
                --border-color: #e5e7eb;
                --background-color: #ffffff;
                --section-bg: #f9fafb;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: var(--text-color);
                max-width: 900px;
                margin: 0 auto;
                padding: 2rem;
                background: var(--background-color);
            }}
            
            h1, h2, h3 {{
                color: var(--primary-color);
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }}
            
            h1 {{
                font-size: 2.2em;
                border-bottom: 2px solid var(--primary-color);
                padding-bottom: 0.3em;
            }}
            
            h2 {{
                font-size: 1.8em;
            }}
            
            h3 {{
                font-size: 1.4em;
                color: var(--text-color);
            }}
            
            .role-target {{
                color: var(--secondary-color);
                font-style: italic;
                margin-bottom: 2em;
            }}
            
            .experience-entry {{
                background: var(--section-bg);
                padding: 1.5em;
                border-radius: 8px;
                margin-bottom: 2em;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            
            .company-header {{
                display: flex;
                justify-content: space-between;
                align-items: baseline;
                margin-bottom: 1em;
            }}
            
            .company-name {{
                font-size: 1.4em;
                font-weight: bold;
                color: var(--primary-color);
            }}
            
            .date-range {{
                color: var(--secondary-color);
                font-style: italic;
            }}
            
            .description {{
                margin-bottom: 1em;
            }}
            
            .metrics {{
                margin: 1em 0;
            }}
            
            .metrics h4 {{
                color: var(--text-color);
                margin-bottom: 0.5em;
            }}
            
            .metrics ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            
            .metrics li {{
                margin-bottom: 0.5em;
                padding-left: 1.5em;
                position: relative;
            }}
            
            .metrics li:before {{
                content: "•";
                color: var(--primary-color);
                font-weight: bold;
                position: absolute;
                left: 0;
            }}
            
            .skills {{
                margin-top: 1em;
                color: var(--secondary-color);
            }}
            
            .skills-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.5em;
                margin-top: 0.5em;
            }}
            
            .skill-tag {{
                background: var(--primary-color);
                color: white;
                padding: 0.2em 0.8em;
                border-radius: 15px;
                font-size: 0.9em;
            }}
            
            .required-skills, .preferred-skills {{
                margin: 1em 0;
            }}
            
            .skill-check {{
                color: #059669;
                margin-right: 0.5em;
            }}
            
            .skill-missing {{
                color: #dc2626;
                margin-right: 0.5em;
            }}
            
            .skill-optional {{
                color: #9ca3af;
                margin-right: 0.5em;
            }}
            
            .meta-info {{
                color: var(--secondary-color);
                font-size: 0.9em;
                text-align: right;
                margin-top: 2em;
                padding-top: 1em;
                border-top: 1px solid var(--border-color);
            }}
        </style>
    </head>
    <body>
        <main>
            <h1>Professional Experience</h1>
            {content}
            <div class="meta-info">
                Generated on {generation_date}
            </div>
        </main>
    </body>
    </html>"""