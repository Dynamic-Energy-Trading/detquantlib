import importlib.util
import inspect
import os
from pathlib import Path
import sys
from collections import defaultdict


PACKAGE_ROOT = Path(__file__).parent / "detquantlib"  # adjust if needed
PACKAGE_NAME = "detquantlib"
README_PATH = Path(__file__).parent / "README.md"


def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def find_all_init_files(root):
    return [p for p in root.rglob("__init__.py")]


def detect_symbol_type(obj):
    if inspect.ismodule(obj):
        return "Modules"
    elif inspect.isclass(obj):
        return "Classes"
    elif inspect.isfunction(obj):
        return "Functions"
    elif isinstance(obj, (int, float, str, bool, tuple, list, dict, set)):
        return "Constants"
    else:
        return "Others"



def get_exposed_symbols_from_module(module):
    exposed = getattr(module, "__all__", [])
    exposed_symbols = {}
    for name in exposed:
        try:
            obj = getattr(module, name)
            exposed_symbols[name] = obj
        except AttributeError:
            continue
    return exposed_symbols


def get_class_full_import_path(cls):
    module = inspect.getmodule(cls)
    return module.__name__ if module else None


def generate_readme_section(symbol_imports_by_type):
    lines = []
    for symbol_type in sorted(symbol_imports_by_type.keys()):
        lines.append(f"### {symbol_type}\n")
        for name, import_paths in sorted(symbol_imports_by_type[symbol_type].items()):
            lines.append(f"- `{name}`:")
            for path in sorted(import_paths):
                lines.append(f"  - `{path}`")
        lines.append("")  # blank line between types
    return "\n".join(lines)


def update_readme(auto_section_text, readme_path=README_PATH):
    begin_marker = "<!-- BEGIN AUTO-GENERATED -->"
    end_marker = "<!-- END AUTO-GENERATED -->"

    with open(readme_path, "r+", encoding="utf-8") as f:
        content = f.read()

        if begin_marker in content and end_marker in content:
            start = content.index(begin_marker) + len(begin_marker)
            end = content.index(end_marker)
            new_content = (
                content[:start] + "\n" + auto_section_text.strip() + "\n" + content[end:]
            )
        else:
            # If the markers don't exist, append the section
            new_content = (
                content.strip()
                + "\n\n## Exposed Classes\n\nList of exposed classes:\n\n"
                + begin_marker
                + "\n"
                + auto_section_text.strip()
                + "\n"
                + end_marker
            )

        f.seek(0)
        f.write(new_content)
        f.truncate()


if __name__ == "__main__":

    symbol_imports_by_type = defaultdict(lambda: defaultdict(set))

    init_files = find_all_init_files(PACKAGE_ROOT)

    for init_path in init_files:
        # Compute dotted module path, stripping trailing '__init__'
        rel_path = init_path.relative_to(PACKAGE_ROOT.parent)
        if rel_path.name == "__init__.py":
            rel_path = rel_path.parent
        module_name = ".".join(rel_path.parts)

        try:
            module = load_module_from_file(module_name, init_path)
        except Exception as e:
            print(f"⚠️ Could not import {module_name}: {e}")
            continue

        exposed_symbols = get_exposed_symbols_from_module(module)

        for name, obj in exposed_symbols.items():
            full_module = inspect.getmodule(obj)
            if not full_module:
                continue
            full_module_name = full_module.__name__

            top_level_import = f"from {module_name} import {name}"
            full_path_import = f"from {full_module_name} import {name}"

            symbol_type = detect_symbol_type(obj)
            symbol_imports_by_type[symbol_type][name].update({top_level_import, full_path_import})

    section = generate_readme_section(symbol_imports_by_type)
    update_readme(section)
    print("✅ README updated with exposed classes from all __init__.py files.")
