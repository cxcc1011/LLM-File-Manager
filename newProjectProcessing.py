import os
import json
import basicFunction
import fileUtils

def creat_dir_from_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            json_content = json.load(f)
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return False

    def create(node, base_path=''):
        """递归创建目录和文件"""
        if isinstance(node, dict):
            # 处理目录节点
            for name, child in node.items():
                item_path = os.path.join(base_path, name)
                if isinstance(child, dict):
                    # 创建子目录
                    basicFunction.create_dir(item_path)
                    create(child, item_path)
                else:
                    # 创建空文件（值为空字符串时）
                    if child == '':
                        open(item_path, 'a').close()

    # 获取根目录名和结构
    root_name, root_structure = next(iter(json_content.items())) if json_content else ("root", {})

    # 创建根目录
    basicFunction.create_dir(root_name)
    # 递归创建子目录和文件
    create(root_structure, root_name)