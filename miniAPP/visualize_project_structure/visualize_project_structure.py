# Построение дерева проекта (файлов, папок, кода) с красивым выводом


from rich.console import Console
from rich.tree import Tree
import os

def build_tree(path, tree):
    for entry in sorted(os.listdir(path)):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            subtree = tree.add(f"📁 {entry}")
            build_tree(full_path, subtree)
        else:
            tree.add(f"📄 {entry}")

def visualize_project_structure(root_path):
    console = Console()
    tree = Tree(f"🌍 Проект: {os.path.basename(root_path)}")
    build_tree(root_path, tree)
    console.print(tree)

# 🔹 Использование
visualize_project_structure("путь/к/твоему/проекту")
