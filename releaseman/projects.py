from dataclasses import dataclass
from typing import List


@dataclass
class Project:
    id: str
    name: str
    slug: str


projects = (
    # Protocol roadmap at https://github.com/orgs/ethereum-optimism/projects/117
    Project('PVT_kwDOA4EWJM4AwluD', 'Optimism Protocol Roadmap', 'optimism-protocol-roadmap'),
)

projects_by_slug = {project.slug: project for project in projects}

def get_project_by_slug(slug: str) -> Project:
    if slug not in projects_by_slug:
        raise ValueError(f"Unknown project: {slug}")

    return projects_by_slug[slug]

def get_project_slugs() -> List[str]:
    return [project.slug for project in projects]