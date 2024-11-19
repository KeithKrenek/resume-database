# src/integrity.py

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

@dataclass
class IntegrityIssue:
    """Represents a data integrity or consistency issue"""
    category: str
    severity: str  # 'critical', 'warning', 'info'
    message: str
    entry_id: Optional[str] = None
    field: Optional[str] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        location = f" in {self.entry_id}" if self.entry_id else ""
        field = f" (field: {self.field})" if self.field else ""
        suggestion = f"\n   Suggestion: {self.suggestion}" if self.suggestion else ""
        return f"{self.severity.upper()}: {self.message}{location}{field}{suggestion}"

class DataIntegrityChecker:
    """System for checking data integrity and consistency"""
    
    def __init__(self, database):
        self.db = database
        self.skill_variants = self._build_skill_variants()
        self.company_variants = self._build_company_variants()

    def _build_skill_variants(self) -> Dict[str, Set[str]]:
        """Build dictionary of skill name variants"""
        variants = defaultdict(set)
        for entry in self.db.entries.values():
            for skill in entry.get('skills', []):
                # Store lowercase version
                base = skill.lower()
                variants[base].add(skill)
                
                # Store without version numbers
                base_no_version = re.sub(r'\s*\d+(\.\d+)*', '', base)
                if base_no_version != base:
                    variants[base_no_version].add(skill)
        
        return variants

    def _build_company_variants(self) -> Dict[str, Set[str]]:
        """Build dictionary of company name variants"""
        variants = defaultdict(set)
        for entry in self.db.entries.values():
            if company := entry.get('company'):
                # Store original
                base = company.lower()
                variants[base].add(company)
                
                # Store without common suffixes
                base_no_suffix = re.sub(r'\s+(Inc\.|LLC|Ltd\.|Corp\.?|Corporation)$', 
                                      '', base, flags=re.IGNORECASE)
                if base_no_suffix != base:
                    variants[base_no_suffix].add(company)
        
        return variants

    def check_integrity(self) -> List[IntegrityIssue]:
        """Perform comprehensive integrity check"""
        issues = []
        
        # Check individual entries
        for entry_id, entry in self.db.entries.items():
            issues.extend(self._check_entry(entry_id, entry))
        
        # Check cross-entry consistency
        issues.extend(self._check_cross_entry_consistency())
        
        # Check data quality
        issues.extend(self._check_data_quality())
        
        return sorted(issues, key=lambda x: (
            {'critical': 0, 'warning': 1, 'info': 2}[x.severity],
            x.category,
            x.entry_id or ''
        ))

    def _check_entry(self, entry_id: str, entry: Dict) -> List[IntegrityIssue]:
        """Check individual entry integrity"""
        issues = []
        
        # Check date consistency
        if date_issues := self._check_dates(entry_id, entry):
            issues.extend(date_issues)
        
        # Check skill consistency
        if skill_issues := self._check_skills(entry_id, entry):
            issues.extend(skill_issues)
        
        # Check metrics consistency
        if metric_issues := self._check_metrics(entry_id, entry):
            issues.extend(metric_issues)
        
        # Check content quality
        if content_issues := self._check_content(entry_id, entry):
            issues.extend(content_issues)
        
        return issues

    def _check_dates(self, entry_id: str, entry: Dict) -> List[IntegrityIssue]:
        """Check date-related integrity"""
        issues = []
        dates = entry.get('dates', {})
        
        try:
            start = datetime.strptime(dates.get('start', ''), '%Y-%m')
            if 'end' in dates:
                end = datetime.strptime(dates['end'], '%Y-%m')
                
                # Check for future end dates
                if end > datetime.now():
                    issues.append(IntegrityIssue(
                        category="dates",
                        severity="warning",
                        message="End date is in the future",
                        entry_id=entry_id,
                        suggestion="Update end date or change status to 'ongoing'"
                    ))
                
                # Check for very long durations
                duration = (end.year - start.year) * 12 + end.month - start.month
                if duration > 60:  # 5 years
                    issues.append(IntegrityIssue(
                        category="dates",
                        severity="info",
                        message=f"Unusually long duration: {duration} months",
                        entry_id=entry_id,
                        suggestion="Verify duration is accurate"
                    ))
        except ValueError as e:
            issues.append(IntegrityIssue(
                category="dates",
                severity="critical",
                message=f"Invalid date format: {str(e)}",
                entry_id=entry_id
            ))
        
        return issues

    def _check_skills(self, entry_id: str, entry: Dict) -> List[IntegrityIssue]:
        """Check skill-related integrity"""
        issues = []
        skills = entry.get('skills', [])
        
        # Check for skill variants
        for skill in skills:
            base_skill = skill.lower()
            variants = self.skill_variants[base_skill]
            if len(variants) > 1:
                issues.append(IntegrityIssue(
                    category="skills",
                    severity="warning",
                    message=f"Inconsistent skill naming: {', '.join(variants)}",
                    entry_id=entry_id,
                    suggestion=f"Standardize on one variant"
                ))
        
        # Check for missing proficiency
        tech_details = entry.get('technical_details', [])
        tech_skills = {td['detail'].lower() for td in tech_details}
        skills_lower = {s.lower() for s in skills}
        
        missing_proficiency = skills_lower - tech_skills
        if missing_proficiency:
            issues.append(IntegrityIssue(
                category="skills",
                severity="info",
                message=f"Skills missing proficiency details: {', '.join(missing_proficiency)}",
                entry_id=entry_id,
                suggestion="Add technical_details for these skills"
            ))
        
        return issues

    def _check_metrics(self, entry_id: str, entry: Dict) -> List[IntegrityIssue]:
        """Check metrics-related integrity"""
        issues = []
        metrics = entry.get('metrics', [])
        
        for i, metric in enumerate(metrics):
            # Check value format
            value = metric.get('value', '')
            if not any(c.isdigit() for c in value):
                issues.append(IntegrityIssue(
                    category="metrics",
                    severity="warning",
                    message=f"Metric value contains no numbers: {value}",
                    entry_id=entry_id,
                    field=f"metrics[{i}].value",
                    suggestion="Include specific numerical measures"
                ))
            
            # Check context completeness
            context = metric.get('context', '')
            if len(context.split()) < 3:
                issues.append(IntegrityIssue(
                    category="metrics",
                    severity="info",
                    message=f"Brief metric context: {context}",
                    entry_id=entry_id,
                    field=f"metrics[{i}].context",
                    suggestion="Provide more detailed context"
                ))
        
        return issues

    def _check_content(self, entry_id: str, entry: Dict) -> List[IntegrityIssue]:
        """Check content quality"""
        issues = []
        
        # Check core description
        core = entry.get('core', '')
        if not any(word in core.lower() for word in [
            'led', 'developed', 'created', 'implemented', 'managed',
            'designed', 'built', 'architected', 'analyzed'
        ]):
            issues.append(IntegrityIssue(
                category="content",
                severity="info",
                message="Core description lacks strong action verbs",
                entry_id=entry_id,
                suggestion="Start with impactful action verbs"
            ))
        
        # Check for metric references
        if entry.get('metrics') and not re.search(r'\d+%|\$\d+|\d+x', core):
            issues.append(IntegrityIssue(
                category="content",
                severity="info",
                message="Core description could include metrics",
                entry_id=entry_id,
                suggestion="Consider adding key metrics to core description"
            ))
        
        return issues

    def _check_cross_entry_consistency(self) -> List[IntegrityIssue]:
        """Check consistency across entries"""
        issues = []
        
        # Check company name consistency
        for base_name, variants in self.company_variants.items():
            if len(variants) > 1:
                issues.append(IntegrityIssue(
                    category="companies",
                    severity="warning",
                    message=f"Inconsistent company naming: {', '.join(variants)}",
                    suggestion="Standardize company names"
                ))
        
        # Check for overlapping dates within companies
        company_timelines = defaultdict(list)
        for entry_id, entry in self.db.entries.items():
            if company := entry.get('company'):
                start = datetime.strptime(entry['dates']['start'], '%Y-%m')
                end = (datetime.strptime(entry['dates']['end'], '%Y-%m')
                      if entry['dates'].get('end')
                      else datetime.now())
                company_timelines[company].append((start, end, entry_id))
        
        for company, timeline in company_timelines.items():
            timeline.sort()  # Sort by start date
            for i in range(len(timeline)-1):
                current_end = timeline[i][1]
                next_start = timeline[i+1][0]
                if current_end > next_start:
                    issues.append(IntegrityIssue(
                        category="timeline",
                        severity="warning",
                        message=f"Overlapping dates at {company}",
                        entry_id=timeline[i][2],
                        suggestion="Verify date ranges"
                    ))
        
        return issues

    def _check_data_quality(self) -> List[IntegrityIssue]:
        """Check overall data quality"""
        issues = []
        total_entries = len(self.db.entries)
        
        # Check metric coverage
        entries_with_metrics = sum(
            1 for e in self.db.entries.values()
            if e.get('metrics')
        )
        if entries_with_metrics < total_entries * 0.8:  # 80% threshold
            issues.append(IntegrityIssue(
                category="quality",
                severity="info",
                message=f"Low metric coverage: {entries_with_metrics}/{total_entries} entries",
                suggestion="Add quantifiable metrics to more entries"
            ))
        
        # Check technical detail coverage
        entries_with_tech = sum(
            1 for e in self.db.entries.values()
            if e.get('technical_details')
        )
        if entries_with_tech < total_entries * 0.7:  # 70% threshold
            issues.append(IntegrityIssue(
                category="quality",
                severity="info",
                message=f"Low technical detail coverage: {entries_with_tech}/{total_entries} entries",
                suggestion="Add technical details to more entries"
            ))
        
        return issues

    def fix_common_issues(self) -> Tuple[List[str], List[str]]:
        """Attempt to fix common integrity issues"""
        fixed = []
        failed = []
        
        # Standardize company names
        for base_name, variants in self.company_variants.items():
            if len(variants) > 1:
                # Use the most common variant
                standard_name = max(variants, key=lambda x: sum(
                    1 for e in self.db.entries.values()
                    if e.get('company') == x
                ))
                
                try:
                    for entry_id, entry in self.db.entries.items():
                        if entry.get('company') in variants:
                            entry['company'] = standard_name
                    fixed.append(f"Standardized company name variants to '{standard_name}'")
                except Exception as e:
                    failed.append(f"Failed to standardize company names: {str(e)}")
        
        # Standardize skill names
        for base_skill, variants in self.skill_variants.items():
            if len(variants) > 1:
                # Use the most common variant
                standard_skill = max(variants, key=lambda x: sum(
                    1 for e in self.db.entries.values()
                    if x in e.get('skills', [])
                ))
                
                try:
                    for entry_id, entry in self.db.entries.items():
                        if 'skills' in entry:
                            entry['skills'] = [
                                standard_skill if s in variants else s
                                for s in entry['skills']
                            ]
                    fixed.append(f"Standardized skill name variants to '{standard_skill}'")
                except Exception as e:
                    failed.append(f"Failed to standardize skill names: {str(e)}")
        
        return fixed, failed