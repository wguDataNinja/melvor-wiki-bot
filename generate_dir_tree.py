# generate_dir_tree.py

import os

EXCLUDE = ['.*', 'config.py', '__pycache__', '.git', 'widget_env', 'old', 'env', 'venv']
MAX_DEPTH = 2

def generate_tree(directory, root_dir):
    tree = {}
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not any(d.startswith(pattern.strip('*')) for pattern in EXCLUDE)]

        depth = root.replace(root_dir, "").count(os.sep)
        if depth > MAX_DEPTH:
            dirs[:] = []
            continue

        relative_path = os.path.relpath(root, root_dir)
        if relative_path == ".":
            parts = []
        else:
            parts = relative_path.split(os.sep)

        current_level = tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        for file in files:
            if not any(file.startswith(pattern.strip('*')) for pattern in EXCLUDE):
                current_level[file] = None
    return tree

def format_tree(tree, indent=""):
    result = ""
    for key, value in sorted(tree.items()):
        if value is None:
            result += f"{indent}{key}\n"
        else:
            result += f"{indent}{key}/\n"
            result += format_tree(value, indent + "    ")
    return result

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    tree = generate_tree(root_dir, root_dir)
    print(format_tree(tree).rstrip())

if __name__ == "__main__":
    main()