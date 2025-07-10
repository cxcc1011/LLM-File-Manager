import os
import json
import basicFunction
import fileUtils
from typing import Dict, Any, Optional

json_path_result = 'fileStructureResult.json'
json_path_new = 'fileStructure2.json'

def generate_operations_from_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            new_structure = json.load(f)
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return False
    operations = []

    def traverse(new_path, new_node):
        # 解析当前节点的操作信息
        op_info = new_node.get("__operation__")
        if op_info is None:
            # 无操作：递归处理子节点（确保子节点变更被捕获）
            if isinstance(new_node, dict):
                for name, child in new_node.items():
                    if name.startswith("__"):
                        continue  # 跳过元数据
                    print(name)
                    child_new_path = f"{new_path}/{name}" if new_path else name
                    traverse(child_new_path, child)
            return

        # 解析操作类型和原路径（格式："类型:原路径"）
        op_type, _, source_path = op_info.partition(":")

        if op_type == "create":
            print(op_info)
            # # 新建操作：先确保父目录存在，再创建当前节点
            # parent_path = "/".join(new_path.split("/")[:-1])
            # if not path_exists(old_structure, parent_path) and parent_path:
            #     operations.append(("create_dir", parent_path))  # 递归创建父目录
            # if isinstance(new_node, dict):
            #     operations.append(("create_dir", new_path))  # 新建目录
            # else:
            #     # 新建文件（含内容）
            #     content = new_node.get("__content__", "")
            #     operations.append(("create_file", new_path, content))

        elif op_type == "move":
            print(op_info)
            # 移动操作：先确保目标父目录存在，再执行移动
            # parent_path = "/".join(new_path.split("/")[:-1])
            # if not path_exists(old_structure, parent_path) and parent_path:
            #     operations.append(("create_dir", parent_path))
            # operations.append(("move", source_path, new_path))

        elif op_type == "delete":
            print(op_info)
            # 删除操作：直接记录原路径
            # operations.append(("delete", source_path))

    # 从根目录开始遍历新结构
    traverse("", new_structure)
    return operations

def path_exists(structure, path):
    """检查路径在旧结构中是否存在"""
    if not path:
        return True  # 根目录默认存在
    parts = path.split("/")
    current = structure
    for part in parts:
        if part not in current:
            return False
        current = current[part]
    return True

def transfer_result_json(path):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            json_content = json.load(f)
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return False

    """
        将新版JSON格式转换为原始JSON格式
        参数:new_json (Dict[str, Any]): 新版JSON数据
        返回:Dict[str, Any]: 转换后的原始JSON数据
    """
    old_json = {}

    def process_directory(dir_content):
        """
            处理目录内容，递归转换子目录和文件
            参数:dir_content (Dict[str, Any]): 目录内容
            返回:Dict[str, Any]: 转换后的目录内容
        """
        result = {}

        for name, item in dir_content.items():
            if name == '__operation__':
                continue  # 跳过元数据
                # 处理目录
            if isinstance(item, dict):
                # 如果包含子项，则递归处理, 检查是否为文件
                if all(key != '__content__' for key in item.keys()):
                    # print(f"{name}is file")
                    result[name] = process_directory(item)
                else:
                    result[name] = ""
        return result

    # 处理根目录
    for root_name, root_content in json_content.items():
        if root_name.startswith('__'):  # 跳过元数据
            continue

        old_json[root_name] = process_directory(root_content)

    return old_json

if __name__=="__main__":
    # 内容优化功能测试用例
    # generate_operations_from_json(json_path)
    fileUtils.save_content(transfer_result_json(json_path_result), json_path_new)
    fileUtils.display_json_tree(json_path_new)