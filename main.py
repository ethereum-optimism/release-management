from email.policy import default

from dotenv import load_dotenv
from releaseman import Recipe
from releaseman.github import GitHubClient
import os
import click
import time

from releaseman.projects import get_project_slugs
from releaseman.tasks import create_prefixed_issues

load_dotenv()  # Load environment variables from .env file


@click.group()
def cli():
    pass


@cli.command()
@click.option('--repo', '-r', required=True, type=str, help='The repository to create the issues in',
              default='ethereum-optimism/release-management')
@click.option('--project', '-p', type=click.Choice(get_project_slugs()), help='The project to create the issues in')
@click.option('--upgrade-number', '-u', required=True, type=int, help='The upgrade number to use')
def release(repo: str, project: str, upgrade_number: int):
    """
    Creates issues for a numbered release. Parent issues represent the release, and child issues represent each step in
    the release process. Used by the release management [board].

    [board]: https://github.com/orgs/ethereum-optimism/projects/117/views/12
    """
    recipe = Recipe.from_yaml("recipes/releases.yaml")
    github = GitHubClient(os.getenv("GITHUB_TOKEN"), repo)

    create_prefixed_issues(
        recipe=recipe,
        github=github,
        project=project,
        template_context={
            'upgrade_number': upgrade_number
        }
    )


@cli.command()
@click.option('--repo', '-r', required=True, type=str, help='The repository to create the issues in',
              default='ethereum-optimism/release-management')
@click.option('--project', '-p', type=click.Choice(get_project_slugs()), help='The project to create the issues in')
@click.option('--shortname', '-s', required=True, type=str, help='The shortname of the SUP')
@click.option('--title', '-t', required=True, type=str, help='The title of the SUP')
def sup(repo: str, project: str, shortname: str, title: str):
    """
    Creates a tracking ticket for a Superchain upgrade proposal (SUP). Parent issues represent the SUP, and child issues
    represent stages in our SDLC process.
    """
    recipe = Recipe.from_yaml("recipes/sup.yaml")
    github = GitHubClient(os.getenv("GITHUB_TOKEN"), repo)

    create_prefixed_issues(
        recipe=recipe,
        github=github,
        project=project,
        template_context={
            'shortname': shortname,
            'title': title
        }
    )


if __name__ == "__main__":
    cli(prog_name='releaseman')
