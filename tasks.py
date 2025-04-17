"""
Tasks for maintaining the project.

The tasks are defined with the Invoke package. In the terminal, execute 'inv --list' for guidance
on using Invoke.
"""

import pathlib
import platform

from invoke import task
from invoke.context import Context
from invoke.runners import Result


# Project related paths
ROOT_DIR = pathlib.Path(__file__).parent
SOURCE_DIR = ROOT_DIR.joinpath("detquantlib/")
TEST_DIR = ROOT_DIR.joinpath("tests/")
README_DIR = ROOT_DIR.joinpath("README.md")
PYTHON_TARGETS = [SOURCE_DIR, TEST_DIR]  # directories containing .py files
PYTHON_TARGETS_STR = " ".join([str(p) for p in PYTHON_TARGETS])


def _run(c: Context, command: str) -> Result:
    return c.run(command, pty=platform.system() != "Windows")


@task()
def test(c, coverage_report=False):
    # type: (Context, bool) -> None
    """
    Run tests with pytest.

    Args:
        coverage_report: If true, produces a coverage report as well.
    """
    options = (
        f"--cov-report term-missing " f"--cov={SOURCE_DIR} {TEST_DIR}" if coverage_report else ""
    )
    _run(c, f"poetry run pytest {TEST_DIR} --verbose {options}")


@task()
def run_lint_imports(c, check=False):
    # type: (Context, bool) -> None
    """
    Run linters on the imports section.

    Args:
        check: If true, checks if code should be formatted, but does not apply any formatting
            changes. Otherwise, applies formatting changes.
    """
    action_log_str = "Running linters on" if check else "Formatting"
    print(f"{action_log_str} imports section ...")
    options = "--check --diff --color" if check else ""
    _run(c, f"poetry run isort {PYTHON_TARGETS_STR} {options}")


@task()
def run_lint_docstrings(c):
    # type: (Context) -> None
    """Run linters on the docstrings descriptions."""
    print("Running linters on docstrings descriptions ...")
    _run(c, f"poetry run darglint -v 2 {PYTHON_TARGETS_STR}")


@task()
def run_lint_code(c, check=False):
    # type: (Context, bool) -> None
    """
    Run linters on the main code.

    Args:
        check: If true, checks if code should be formatted, but does not apply any formatting
            changes. Otherwise, applies formatting changes.
    """
    action_log_str = "Running linters on" if check else "Formatting"
    print(f"{action_log_str} main code ...")
    options = "--check --diff --color" if check else ""
    _run(c, f"poetry run black {PYTHON_TARGETS_STR} {options}")


@task()
def run_readme_toc(c):
    # type: (Context) -> None
    """Creates/updates the table of contents of the markdown file README.md."""
    if not README_DIR.is_file():
        print(
            f"File '{README_DIR}' not found! Please make sure that a README.md file exists "
            f"and that it is located in the project's root directory."
        )
        exit(1)

    print(f"Updating table of contents of markdown file README.md ...")
    _run(c, f"md_toc --in-place --no-list-coherence --newline-string '\\n' github {README_DIR}")


@task()
def run_lint_readme(c, check=False):
    # type: (Context, bool) -> None
    """
    Run linters on the markdown file README.md.

    Args:
        check: If true, checks if code should be formatted, but does not apply any formatting
            changes. Otherwise, applies formatting changes.
    """
    if not README_DIR.is_file():
        print(
            f"File '{README_DIR}' not found! Please make sure that a README.md file exists "
            f"and that it is located in the project's root directory."
        )
        exit(1)

    action_log_str = "Running linters on" if check else "Formatting"
    print(f"{action_log_str} markdown file README.md ...")
    options = "scan" if check else "fix"
    _run(c, f"poetry run pymarkdown {options} {README_DIR}")


@task()
def lint(c, check=False, type_="all"):
    # type: (Context, bool, str) -> None
    """
    Run linters.

    Args:
        check: If true, checks if code should be formatted, but does not apply any formatting
            changes. Otherwise, applies formatting changes.
        type_: Determines on which part of the code to run the linters.
            - type="imports": run linters on imports section
            - type="docstrings": run linters on docstrings descriptions
            - type="code": run linters on main code
            - type="readme": run linters on markdown file README.md
            - type="all": (default) run linters on all of the above
    """
    if type_ in ["imports", "all"]:
        run_lint_imports(c, check=check)
    if type_ in ["docstrings", "all"]:
        run_lint_docstrings(c)
    if type_ in ["code", "all"]:
        run_lint_code(c, check=check)
    if type_ in ["readme", "all"]:
        run_readme_toc(c)
        run_lint_readme(c, check=check)
