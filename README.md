# release-management

This repo contains a tool called `releaseman` that generates GitHub issues based on a template. It is also used as a
database to house issues for the release management tracker.

## Prerequisites

You will need to install [uv][uv] to use this project.

[uv]: https://docs.astral.sh/uv/getting-started/installation/

## Usage

To run the CLI, run `./releaseman.sh <args>`. To see command help run `./releaseman.sh <command> --help`.

### Commands

#### `./releaseman.sh release [OPTIONS]`

Creates issues for a numbered release. Parent issues represent the release, and child issues represent each step in the
release process. Used by the release management [board].

[board]: https://github.com/orgs/ethereum-optimism/projects/117/views/12

Options:

```
-r, --repo TEXT The repository to create the issues in [required]
-p, --project [optimism-protocol-roadmap] The project to create the issues in
-u, --upgrade-number INTEGER The upgrade number to use [required]
--help Show this message and exit.
```

#### `./releaseman.sh sup [OPTIONS]`

Creates a tracking ticket for a Superchain upgrade proposal (SUP). Parent issues represent the SUP, and child issues
represent stages in our SDLC process.

Options:

```
-r, --repo TEXT The repository to create the issues in [required]
-p, --project [optimism-protocol-roadmap] The project to create the issues in
-s, --shortname TEXT The shortname of the SUP  [required]
-t, --title TEXT The title of the SUP  [required]
--help Show this message and exit.
```

## How it Works

`releaseman` creates issues with one or more child-issues based on a recipe. The recipe is a YAML file that defines
how each issue should be formatted. The schema for the recipe is below:

```yaml
global_prefix: "prefix" # optional: string to prefix all issues with

global_labels: # optional: list of labels to apply to all issues
  - "issue-name"

parent_issue: # required: format of the parent issue
  title: "some title" # required: parent issue title
  body: "some body" # optional: parent issue body
  labels: # optional: list of labels to apply to the parent issue
    - "some-label"

issues: # optional: list of child issues
  - title: "some title" # required: child issue title
    body: "some body" # optional: child issue body
    labels: # optional: list of labels to apply to the child issue 
      - "some-label""
```

You can see an example recipe in [sup.yaml][sup.yaml].

All the string fields in the above schema support templating. Templating is powered by Python's `format()` method, so
anything that works in there can be used in the template. Variables are passed in via a `template_context` dict. See
[main.py][main.py] for an example invocation.

[main.py]: ./main.py

[sup.yaml]: ./recipes/sup.yaml