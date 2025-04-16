# DET Quant Library

The DET Quant Library is an internal library containing functions and classes that can be used
across Quant models.

## Instructions

#### Version control

- This repository contains a version control workflow.
- The version number is specified via the `version` field in the pyproject.toml file.
- The version number needs to be updated with every new master commit. If the version is not
  updated, the GitHub workflow will fail.
- Version numbers should follow semantic versioning (i.e. `X.Y.Z`). That is:
  - `X` increments represent major, non-backward compatible updates.
  - `Y` increments represent minor, backward compatible functionality updates.
  - `Z` increments represent patch/bugfix, backward compatible updates.

#### Release notes

- When deemed necessary (especially in case of major updates), developers can document code
  changes in dedicated GitHub release notes.
- Release notes can be created via
  <https://github.com/Dynamic-Energy-Trading/detquantlib/releases.>
- In any case, all codes changes should always be properly described/documented in GitHub
  issues and/or pull requests.

## Dependencies

### Dependency manager

Project dependencies are managed by [Poetry](https://python-poetry.org/).

The project follows the standard Poetry structure:

```
detquantlib
├── pyproject.toml
├── README.md
├── detquantlib
│   └── __init__.py
└── tests
    └── __init__.py
```

### Dependabot

This project is executing automated dependency updates using
[Dependabot](https://docs.github.com/en/code-security/dependabot).

## GitHub actions

This project is executing CI/CD checks using [GitHub actions](https://docs.github.com/en/actions)
workflows.

### Workflow: Continuous integration (CI)

The continuous integration (CI) workflow runs tests to check the integrity of the codebase's 
content, and linters to check the consistency of its format.

The workflow was inspired by the following preconfigured templates:

- [Python package](https://github.com/actions/starter-workflows/blob/main/ci/python-package.yml):
  A general workflow template for Python packages.
- [Poetry action](https://github.com/marketplace/actions/install-poetry-action): A GitHub action
  for installing and configuring Poetry.

#### Invoke tasks

The workflow's checks and linters are defined with [Invoke](https://www.pyinvoke.org/) tasks.

**What is Invoke?**

The Invoke package provides a clean, high level API for running shell commands and 
defining/organizing task functions from a tasks.py file.

**How to run Invoke tasks?**

Development tasks can be executed directly from the terminal, using the `inv` (or `invoke`)
command line tool.

For guidance on the available Invoke development tasks, execute the following command in the
terminal:

```cmd
inv --list
```

Use the `-h` (or `--help`) argument for help about a particular development task. For example:

```cmd
inv lint -h
```

#### CI check: Testing

Code changes are tested with the [Pytest](https://github.com/pytest-dev/pytest) package.

The CI check is executed with the following the development task:

```cmd
inv test -c
```

#### CI check: Code formatting

Linters are used to check that the code is properly formatted:

- [Isort](https://github.com/timothycrosley/isort) for the imports section
- [Darglint](https://github.com/terrencepreilly/darglint) for the docstrings description
- [Black](https://github.com/psf/black) for the main code
- [Pymarkdown](https://github.com/jackdewinter/pymarkdown) for the markdown file README.md

The CI check is executed with the following development task:

```cmd
inv lint -c
```

If the CI check fails, execute the following command in the terminal:

```cmd
inv lint
```

This command fixes the parts of the code that should be reformatted. Adding the `-c` (or
`--check`) optional argument instructs the command to only _check_ if parts of the code should be
reformatted, without applying any actual changes.

### Workflow: Package publisher

WIP
