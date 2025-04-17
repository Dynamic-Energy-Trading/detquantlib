"""
Tasks for maintaining the project.

The tasks are defined with the Invoke package. In the terminal, execute 'inv --list' for guidance
on using Invoke.
"""

import pathlib
import platform
import subprocess

from invoke import task
from invoke.context import Context
from invoke.runners import Result

# Project related paths
ROOT_DIR = pathlib.Path(__file__).parent
SOURCE_DIR = ROOT_DIR.joinpath("detquantlib/")
TEST_DIR = ROOT_DIR.joinpath("tests/")
TASKS_DIR = ROOT_DIR.joinpath("tasks.py")
README_DIR = ROOT_DIR.joinpath("README.md")
PYTHON_TARGETS = [SOURCE_DIR, TEST_DIR, TASKS_DIR]  # directories containing .py files
PYTHON_TARGETS_STR = " ".join([str(p) for p in PYTHON_TARGETS])


def _run(c: Context, command: str) -> Result:
    return c.run(command, pty=platform.system() != "Windows")


@task()
def test(c, coverage_report=False):
    # type: (Context, bool) -> None
    """
    Run tests with pytest.

    Args:
        c: Invoke Context object. Note that this argument does not need to be passed when calling
            the task through the CLI because Invoke does it automatically.
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
        c: Invoke Context object. Note that this argument does not need to be passed when calling
            the task through the CLI because Invoke does it automatically.
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
    """
    Run linters on the docstrings descriptions.

    Args:
        c: Invoke Context object. Note that this argument does not need to be passed when calling
            the task through the CLI because Invoke does it automatically.
    """
    print("Running linters on docstrings descriptions ...")
    _run(c, f"poetry run darglint -v 2 {PYTHON_TARGETS_STR}")


@task()
def run_lint_code(c, check=False):
    # type: (Context, bool) -> None
    """
    Run linters on the main code.

    Args:
        c: Invoke Context object. Note that this argument does not need to be passed when calling
            the task through the CLI because Invoke does it automatically.
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
    """
    Creates/updates the table of contents of the markdown file README.md.

    Note: The task is run with subprocess.run() instead of Invoke's c.run(), because invoke
    cannot handle the "\\n" argument cross-platform.

    Args:
        c: Invoke Context object. Note that this argument does not need to be passed when calling
            the task through the CLI because Invoke does it automatically.
    """
    if not README_DIR.is_file():
        print(
            f"File '{README_DIR}' not found! Please make sure that a README.md file exists "
            f"and that it is located in the project's root directory."
        )
        exit(1)

    # Build command. Note:
    print(f"Updating table of contents of markdown file README.md ...")
    command = ["md_toc", "--in-place", "-c", "--newline-string", "\\n", "github", f"{README_DIR}"]
    subprocess.run(command, check=True)


@task()
def run_lint_readme(c, check=False):
    # type: (Context, bool) -> None
    """
    Run linters on the markdown file README.md.

    Args:
        c: Invoke Context object. Note that this argument does not need to be passed when calling
            the task through the CLI because Invoke does it automatically.
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
        c: Invoke Context object. Note that this argument does not need to be passed when calling
            the task through the CLI because Invoke does it automatically.
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
