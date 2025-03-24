# DET Quant Library

An internal library containing functions and classes that can be used across Quant models.

## Development settings

### Dependency management

Project dependencies are managed by [Poetry](https://python-poetry.org/).

The project follows the standard Poetry structure:

```
poetrytemplate
├── pyproject.toml
├── README.md
├── src
│   └── __init__.py
└── tests
    └── __init__.py
```

### Dependency updates

This project is executing automated dependency updates using
[Dependabot with GitHub actions](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions).

### Invoke development tasks

Development tasks are defined with the [Invoke](https://www.pyinvoke.org/) package.

#### What is Invoke?

Invoke provides a clean, high level API for running shell commands and defining/organizing task
functions from a tasks.py file.

#### How to run development tasks?

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

### CI/CD process

This project is executing CI checks using [GitHub actions](https://docs.github.com/en/actions)
workflows.

The GitHub workflow defined in this project was inspired by the following preconfigured templates:

- [Python package](https://github.com/actions/starter-workflows/blob/main/ci/python-package.yml):
  A general workflow template for Python packages.
- [Poetry action](https://github.com/marketplace/actions/install-poetry-action): A GitHub action
  for installing and configuring Poetry.

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
