from dataclasses import dataclass, field
from typing import List, Optional
import yaml
from pathlib import Path


@dataclass
class ConfigIssue:
    title: str
    body: str = ''
    labels: List[str] = field(default_factory=list)


@dataclass
class Recipe:
    global_prefix: str
    global_labels: List[str]
    parent_issue: ConfigIssue
    issues: List[ConfigIssue]

    @classmethod
    def from_yaml(cls, path: str | Path, overrides: dict = None) -> 'Recipe':
        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        if overrides:
            data = cls._deep_merge(data, overrides)

        return cls(
            global_prefix=data.get('global_prefix', ''),
            global_labels=data.get('global_labels', []),
            parent_issue=ConfigIssue(**data['parent_issue']),
            issues=[ConfigIssue(**issue) for issue in data.get('issues', [])],
        )

    @staticmethod
    def _deep_merge(source: dict, override: dict) -> dict:
        """
        Performs a deep merge of two dictionaries, with values from override
        taking precedence over values from source for the same keys.
        Lists are replaced, not merged.
        """
        result = source.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Recipe._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def to_yaml(self, path: str | Path) -> None:
        data = {
            'project_id': self.project_id,
            'parent_issue': self.parent_issue,
            'issues': [{'title': issue.title} for issue in self.issues]
        }

        with open(path, 'w') as f:
            yaml.safe_dump(data, f, sort_keys=False)
