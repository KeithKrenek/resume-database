# src/version_control.py

from typing import Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import json
import logging
from dataclasses import dataclass
import difflib
import copy
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ChangeRecord:
    """Represents a single change to an entry"""
    timestamp: str
    entry_id: str
    change_type: str  # 'create', 'update', 'delete'
    fields_changed: List[str]
    previous_hash: Optional[str]
    new_hash: str
    comment: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'timestamp': self.timestamp,
            'entry_id': self.entry_id,
            'change_type': self.change_type,
            'fields_changed': self.fields_changed,
            'previous_hash': self.previous_hash,
            'new_hash': self.new_hash,
            'comment': self.comment
        }

class VersionControl:
    """Handles version control for resume entries"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.history_dir = self.data_dir / 'history'
        self.changes_file = self.data_dir / 'changes.json'
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.changes: List[ChangeRecord] = []
        self._load_changes()

    def _load_changes(self) -> None:
        """Load change history from file"""
        if self.changes_file.exists():
            try:
                with open(self.changes_file, 'r') as f:
                    changes_data = json.load(f)
                    self.changes = [
                        ChangeRecord(**change) for change in changes_data
                    ]
            except Exception as e:
                logger.error(f"Error loading changes: {e}")
                self.changes = []

    def _save_changes(self) -> None:
        """Save change history to file"""
        try:
            with open(self.changes_file, 'w') as f:
                json.dump(
                    [change.to_dict() for change in self.changes],
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Error saving changes: {e}")
            raise

    def _compute_hash(self, data: Dict) -> str:
        """Compute hash of entry data"""
        # Sort keys for consistent hashing
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def _save_version(self, entry_id: str, data: Dict, version_hash: str) -> None:
        """Save a version of an entry"""
        version_file = self.history_dir / f"{entry_id}_{version_hash[:8]}.json"
        with open(version_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_version(self, entry_id: str, version_hash: str) -> Optional[Dict]:
        """Retrieve a specific version of an entry"""
        version_file = self.history_dir / f"{entry_id}_{version_hash[:8]}.json"
        if version_file.exists():
            with open(version_file, 'r') as f:
                return json.load(f)
        return None

    def _detect_changes(self, old_data: Optional[Dict], new_data: Dict) -> List[str]:
        """Detect which fields have changed"""
        if old_data is None:
            return ['initial_creation']
            
        changed_fields = []
        
        def compare_values(old_val, new_val, field_path=""):
            if type(old_val) != type(new_val):
                changed_fields.append(field_path)
            elif isinstance(old_val, dict):
                for key in set(old_val.keys()) | set(new_val.keys()):
                    new_path = f"{field_path}.{key}" if field_path else key
                    if key not in old_val:
                        changed_fields.append(f"{new_path} (added)")
                    elif key not in new_val:
                        changed_fields.append(f"{new_path} (removed)")
                    else:
                        compare_values(old_val[key], new_val[key], new_path)
            elif isinstance(old_val, list):
                if old_val != new_val:
                    changed_fields.append(field_path)
            else:
                if old_val != new_val:
                    changed_fields.append(field_path)

        compare_values(old_data, new_data)
        return changed_fields

    def record_change(self, 
                     entry_id: str, 
                     new_data: Dict, 
                     change_type: str,
                     comment: Optional[str] = None) -> ChangeRecord:
        """Record a change to an entry"""
        timestamp = datetime.now().isoformat()
        new_hash = self._compute_hash(new_data)
        
        # Get previous version
        previous_hash = None
        previous_data = None
        if change_type != 'create':
            previous_changes = [
                c for c in reversed(self.changes)
                if c.entry_id == entry_id
            ]
            if previous_changes:
                previous_hash = previous_changes[0].new_hash
                previous_data = self._get_version(entry_id, previous_hash)
        
        # Detect changed fields
        fields_changed = self._detect_changes(previous_data, new_data)
        
        # Create change record
        change = ChangeRecord(
            timestamp=timestamp,
            entry_id=entry_id,
            change_type=change_type,
            fields_changed=fields_changed,
            previous_hash=previous_hash,
            new_hash=new_hash,
            comment=comment
        )
        
        # Save new version and update changes
        self._save_version(entry_id, new_data, new_hash)
        self.changes.append(change)
        self._save_changes()
        
        return change

    def get_history(self, entry_id: str) -> List[ChangeRecord]:
        """Get change history for an entry"""
        return [c for c in self.changes if c.entry_id == entry_id]

    def get_version(self, entry_id: str, version_hash: str) -> Optional[Dict]:
        """Get a specific version of an entry"""
        return self._get_version(entry_id, version_hash)

    def get_diff(self, entry_id: str, version1_hash: str, version2_hash: str) -> List[str]:
        """Get differences between two versions"""
        version1 = self._get_version(entry_id, version1_hash)
        version2 = self._get_version(entry_id, version2_hash)
        
        if not version1 or not version2:
            raise ValueError("One or both versions not found")
            
        # Convert to string for comparison
        v1_str = json.dumps(version1, indent=2).splitlines()
        v2_str = json.dumps(version2, indent=2).splitlines()
        
        # Generate diff
        diff = list(difflib.unified_diff(
            v1_str,
            v2_str,
            fromfile=f'Version {version1_hash[:8]}',
            tofile=f'Version {version2_hash[:8]}',
            lineterm=''
        ))
        
        return diff

    def rollback(self, entry_id: str, version_hash: str) -> Dict:
        """Rollback an entry to a specific version"""
        version_data = self.get_version(entry_id, version_hash)
        if not version_data:
            raise ValueError(f"Version {version_hash} not found")
            
        # Record rollback as a new change
        change = self.record_change(
            entry_id=entry_id,
            new_data=version_data,
            change_type='rollback',
            comment=f"Rolled back to version {version_hash[:8]}"
        )
        
        return version_data