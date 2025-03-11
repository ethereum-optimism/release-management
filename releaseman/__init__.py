from dataclasses import dataclass, field
from typing import List, Optional
import yaml
from pathlib import Path

@dataclass
class ConfigIssue:
    title: str
    body: Optional[str] = ''
    labels: List[str] = field(default_factory=list)

@dataclass
class Config:
    parent_issue: ConfigIssue
    issues: List[ConfigIssue]
    project_id: str

    @classmethod
    def from_yaml(cls, path: str | Path) -> 'Config':
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
        if 'project_id' not in data or data['project_id'] is None:
            raise ValueError("project_id is required and cannot be null")
            
        return cls(
            parent_issue=ConfigIssue(**data['parent_issue']),
            issues=[ConfigIssue(**issue) for issue in data.get('issues', [])],
            project_id=data['project_id']
        )

    def to_yaml(self, path: str | Path) -> None:
        data = {
            'project_id': self.project_id,
            'parent_issue': self.parent_issue,
            'issues': [{'title': issue.title} for issue in self.issues]
        }
        
        with open(path, 'w') as f:
            yaml.safe_dump(data, f, sort_keys=False)
