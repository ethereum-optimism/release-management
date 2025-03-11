from dotenv import load_dotenv
from releaseman import Config
from releaseman.github import GitHubClient
import os
import click
import time
load_dotenv()  # Load environment variables from .env file

@click.command()
@click.option('--upgrade-number', '-u', required=True, type=int, help='The upgrade number to use')
def main(upgrade_number: int):
    config = Config.from_yaml("config.yaml")
    # Replace any template variables in the parent issue title
    github = GitHubClient(os.getenv("GITHUB_TOKEN"), "ethereum-optimism/release-management")

    config.parent_issue.title = f'[U{upgrade_number}] {config.parent_issue.title}'
    config.parent_issue.labels.append(f'M-upgrade-{upgrade_number}')
    parent = github.add_issue(config.parent_issue)
    github.add_issue_to_project(parent, config.project_id)
    print(f"Created parent issue #{parent.number}: {parent.title}")
    for issue in config.issues:
        issue.title = f'[U{upgrade_number}] {issue.title}'
        issue.labels.append(f'M-upgrade-{upgrade_number}')
        child = github.add_sub_issue(issue, parent)
        print(f"Created sub-issue #{child.number}: {child.title}")


if __name__ == "__main__":
    main()
