import os
from typing import Optional, Union

from releaseman import Recipe
from releaseman.github import GitHubClient, GithubIssue
from releaseman.projects import get_project_by_slug


def create_prefixed_issues(
        recipe: Recipe,
        github: GitHubClient,
        project: str = None,
        template_context: dict = None
):
    template_context = template_context or {}

    parent = github.add_issue(GithubIssue(
        title=f'{recipe.global_prefix}{recipe.parent_issue.title}'.format(**template_context),
        body=recipe.parent_issue.body.format(**template_context),
        labels=[label.format(**template_context) for label in recipe.global_labels + recipe.parent_issue.labels],
    ))

    if project:
        gh_project = get_project_by_slug(project)
        github.add_issue_to_project(parent, gh_project.id)

    print(f"Created parent issue #{parent.number}: {parent.title}")
    for issue in recipe.issues:
        child = github.add_sub_issue(parent, GithubIssue(
            title=f'{recipe.global_prefix}{issue.title}'.format(**template_context),
            body=issue.body.format(**template_context),
            labels=[label.format(**template_context) for label in recipe.global_labels + issue.labels],
        ))
        print(f"Created sub-issue #{child.number}: {child.title}")


def rename_issues(github: GitHubClient, find: str, replace: str, field: str = 'title', dry_run: bool = False):
    if dry_run:
        print('DRY RUN - issues will not be renamed')

    issues = github.search_issues(find)

    for issue in issues:
        match_field = getattr(issue, field)

        if find not in match_field:
            continue

        new_field = match_field.replace(find, replace)
        if not dry_run:
            github.update_issue(issue.number, **{field: new_field})

        print(f'Issue #{issue.number}: Renamed {field} {match_field} -> {new_field}')
