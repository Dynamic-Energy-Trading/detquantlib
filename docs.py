import importlib.util
import inspect
import sys
from collections import defaultdict
from pathlib import Path
from types import ModuleType

PROJECT_ROOT = Path.cwd()
PACKAGE_NAME = "detquantlib"
PACKAGE_ROOT = PROJECT_ROOT.joinpath(PACKAGE_NAME)
README_PATH = PROJECT_ROOT.joinpath("README.md")


def main():
    """
    Main function to auto-generate the list of exposed symbols and add it to the README.md file.
    """
    symbol_imports_by_type = defaultdict(lambda: defaultdict(set))

    # Find all init files in package
    init_files = find_all_init_files(PACKAGE_ROOT)

    # Loop over init files
    for full_init_path in init_files:
        # Compute dotted path, stripping trailing '__init__'
        init_path = full_init_path.relative_to(PACKAGE_ROOT.parent).parent
        init_path_dotted = ".".join(init_path.parts)

        try:
            module = load_module_from_file(init_path_dotted, full_init_path)
        except Exception as e:
            print(f"⚠️ Could not import {init_path_dotted}: {e}")
            continue

        exposed_symbols = get_exposed_symbols_from_module(module)

        # Loop over exposed symbols in current init file
        for name, obj in exposed_symbols.items():
            obj_module = inspect.getmodule(obj)
            if not obj_module:
                continue
            obj_path_dotted = obj_module.__name__

            # Define exposed import command and full path import command
            exposed_import = f"from {init_path_dotted} import {name}"
            full_path_import = f"from {obj_path_dotted} import {name}"

            # Find type of exposed symbol
            symbol_type = detect_symbol_type(obj)
            symbol_imports_by_type[symbol_type][name].update({exposed_import, full_path_import})

    auto_section_text = generate_readme_section(symbol_imports_by_type)
    update_readme(auto_section_text)
    print("✅ README updated with exposed symbols from all __init__.py files.")


def find_all_init_files(root: Path) -> list:
    """
    Recursively finds all __init__.py files under the given root path.

    Args:
        root: Root directory to search

    Returns:
        List of paths to __init__.py files
    """
    init_files = [f for f in root.rglob("__init__.py")]
    return init_files


def load_module_from_file(module_name: str, file_path: Path) -> ModuleType:
    """
    Dynamically loads a Python module from a given file path.

    Args:
        module_name: Module name
        file_path: Path to the Python file

    Returns:
        The loaded module object
    """
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def get_exposed_symbols_from_module(module: ModuleType) -> dict:
    """
    Extracts all symbols listed in __all__ from the given module.

    Args:
        module: The imported module object

    Returns:
        Mapping of symbol names to their objects
    """
    exposed_names = getattr(module, "__all__", [])
    exposed_symbols = dict()
    for name in exposed_names:
        try:
            obj = getattr(module, name)
            exposed_symbols[name] = obj
        except AttributeError:
            continue
    return exposed_symbols


def detect_symbol_type(obj: ModuleType) -> str:
    """
    Determines the type category of a given symbol.

    Args:
        obj: Symbol

    Returns:
        Symbol type
    """
    if inspect.ismodule(obj):
        symbol_type = "Modules"
    elif inspect.isclass(obj):
        symbol_type = "Classes"
    elif inspect.isfunction(obj):
        symbol_type = "Functions"
    elif isinstance(obj, (int, float, str, bool, tuple, list, dict, set)):
        symbol_type = "Constants"
    else:
        symbol_type = "Others"
    return symbol_type


def generate_readme_section(symbol_imports_by_type: dict) -> str:
    """
    Formats the exposed symbols into a structured markdown section.

    Args:
        symbol_imports_by_type: Mapping from symbol type → symbol name → set of import paths

    Returns:
        Markdown-formatted string to inject into the README.md
    """
    lines = []
    for symbol_type in sorted(symbol_imports_by_type.keys()):
        lines.append(f"{symbol_type}:\n")
        for name, import_paths in sorted(symbol_imports_by_type[symbol_type].items()):
            lines.append(f"- `{name}`:")
            for path in sorted(import_paths):
                lines.append(f"  - `{path}`")
        lines.append("")  # blank line between types
    auto_section_text = "\n".join(lines)
    return auto_section_text


def update_readme(auto_section_text: str, readme_path: Path = README_PATH):
    """
    Inserts or updates the auto-generated section of the README.md file between markers.

    Args:
        auto_section_text: Markdown content to insert
        readme_path: Path to the README.md file
    """
    start_marker = "<!-- START EXPOSED SYMBOLS AUTO-GENERATED -->"
    end_marker = "<!-- END EXPOSED SYMBOLS AUTO-GENERATED -->"

    with open(readme_path, "r+", encoding="utf-8") as f:
        content = f.read()

        if start_marker in content and end_marker in content:
            start = content.index(start_marker) + len(start_marker)
            end = content.index(end_marker)
            new_content = (
                    content[:start]
                    + "\n\n"  # blank line after start marker
                    + auto_section_text.strip()
                    + "\n\n"  # blank line before end marker
                    + content[end:]
            )
        else:
            # If the markers don't exist, append the section
            new_content = (
                content.strip()
                + "\n\n## Exposed symbols\n\n#### List of exposed symbols\n\n"
                + start_marker
                + "\n\n"
                + auto_section_text.strip()
                + "\n\n"
                + end_marker
            )

        f.seek(0)
        f.write(new_content)
        f.truncate()


if __name__ == "__main__":
    main()
