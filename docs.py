import importlib.util
import inspect
import os
from pathlib import Path
import sys


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


def get_exposed_classes_from_module(module):
    exposed = getattr(module, "__all__", [])
    exposed_classes = {}
    for name in exposed:
        try:
            obj = getattr(module, name)
            if inspect.isclass(obj):
                exposed_classes[name] = obj
        except AttributeError:
            continue
    return exposed_classes


def get_class_full_import_path(cls):
    module = inspect.getmodule(cls)
    return module.__name__ if module else None


def generate_readme_section(class_imports):
    lines = []
    for cls_name, import_paths in sorted(class_imports.items()):
        lines.append(f"- `{cls_name}`:")
        for path in sorted(import_paths):
            lines.append(f"  - `{path}`")
    return "\n".join(lines) + "\n\n"


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
    class_imports = {}

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

        exposed_classes = get_exposed_classes_from_module(module)

        for cls_name, cls_obj in exposed_classes.items():
            full_module = get_class_full_import_path(cls_obj)
            if not full_module:
                continue
            top_level_import = f"from {module_name} import {cls_name}"
            full_path_import = f"from {full_module} import {cls_name}"

            if cls_name not in class_imports:
                class_imports[cls_name] = set()

            class_imports[cls_name].update({top_level_import, full_path_import})

    section = generate_readme_section(class_imports)
    update_readme(section)
    print("✅ README updated with exposed classes from all __init__.py files.")
