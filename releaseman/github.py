from dataclasses import dataclass, field

from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github.Issue import Issue
from github.Label import Label
from github.GithubException import GithubException
from typing import Optional, Any, Dict, List, Generic
import requests


@dataclass
class GithubIssue:
    title: str
    body: Optional[str] = None
    labels: List[str] = field(default_factory=list)


class GitHubClient:
    def __init__(self, token: str, repo_name: str):
        self.token = token
        self.repo_name = repo_name
        self.github = Github(token)
        self.repo: Repository = self.github.get_repo(repo_name)
        self.known_labels: Dict[str, Label] = {}

    def get_or_create_label(self, name: str) -> Label:
        if name in self.known_labels:
            return self.known_labels[name]

        try:
            label = self.repo.get_label(name)
            self.known_labels[name] = label
            return label
        except GithubException as e:
            if e.status == 404:
                label = self.repo.create_label(name=name, color='CCCCCC')
                self.known_labels[name] = label
                return label
            raise

    def add_issue(self, issue: GithubIssue) -> Issue:
        labels = [self.get_or_create_label(label) for label in issue.labels]

        return self.repo.create_issue(
            title=issue.title,
            body=issue.body,
            labels=labels,
        )

    def add_issue_to_project(self, issue: Issue, project_id: str) -> None:
        self._make_graphql_request(
            query="""
                mutation {
                    addProjectV2ItemById(input: {projectId: "%s" contentId: "%s"}) {
                        item {
                            id
                        }
                    }
                }
            """ % (project_id, issue.node_id),
            variables={"projectId": project_id, "issueId": issue.id}
        )

    def add_sub_issue(self, parent: Issue, child: GithubIssue) -> Issue:
        # First create the issue normally
        child_issue = self.add_issue(child)

        # Then link it as a sub-issue using GitHub's API
        self._make_github_request(
            method="POST",
            path=f"issues/{parent.number}/sub_issues",
            data={"sub_issue_id": child_issue.id, "replace_parent": True}
        )

        return child_issue

    def search_issues(self, query: str) -> PaginatedList[Issue]:
        return self.github.search_issues(query=query, type='issue', repo=self.repo_name)

    def update_issue(self, issue_id: int, title: Optional[str] = None, body: Optional[str] = None):
        issue = self.repo.get_issue(issue_id)

        edit_args = {}
        if title:
            edit_args['title'] = title
        if body:
            edit_args['body'] = body
        assert len(edit_args) > 0, "Must specify at least one field to update"

        return issue.edit(**edit_args)

    def _make_github_request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        owner, repo = self.repo_name.split('/')
        url = f"https://api.github.com/repos/{owner}/{repo}/{path}"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response

    def _make_graphql_request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = "https://api.github.com/graphql"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        data = {
            "query": query,
            "variables": variables or {}
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL query failed: {result['errors']}")

        return result["data"]
