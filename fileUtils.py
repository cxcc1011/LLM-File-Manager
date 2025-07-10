import os
import sys
import json

json_file = 'fileStructure2.json'

def display_directory_tree(path):
    """Display the directory tree in a format similar to the 'tree' command, including the full path."""
    def tree(dir_path, prefix=''):
        contents = sorted([c for c in os.listdir(dir_path) if not c.startswith('.')])
        pointers = ['├── '] * (len(contents) - 1) + ['└── '] if contents else []
        for pointer, name in zip(pointers, contents):
            full_path = os.path.join(dir_path, name)
            display_name = name + '/' if os.path.isdir(full_path) else name
            print(prefix + pointer + display_name)
            if os.path.isdir(full_path):
                extension = '│   ' if pointer == '├── ' else '    '
                tree(full_path, prefix + extension)
    if os.path.isdir(path):
        print(os.path.basename(os.path.abspath(path)) + '/')
        tree(path)
    else:
        print(os.path.abspath(path))

def display_json_tree(path):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            json_content = json.load(f)
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return False
    """Display the directory tree from JSON content in a format similar to the 'tree' command."""

    def tree(node, prefix=''):
        # 处理目录节点（字典类型）
        if isinstance(node, dict):
            contents = sorted(node.items())
            pointers = ['├── '] * (len(contents) - 1) + ['└── '] if contents else []

            for pointer, (name, child) in zip(pointers, contents):
                display_name = name + '/' if isinstance(child, dict) else name
                print(prefix + pointer + display_name)

                if isinstance(child, dict):
                    extension = '│   ' if pointer == '├── ' else '    '
                    tree(child, prefix + extension)

    # 获取根目录名和结构（第一个键值对）
    root_name, root_structure = next(iter(json_content.items())) if json_content else ("root", {})

    print(root_name + '/')
    tree(root_structure)


def save_content(content, path):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        print("保存成功")
        return True

    except Exception as e:
        print(f"保存失败：{e}")
        sys.exit(1)

if __name__ == '__main__':

    ''' 接口测试专用'''
    # fileUtils.display_directory_tree(base_dir)
    # display_json_tree(json_file)