import os
import re
import json
import basicFunction
import fileUtils
from typing import Dict, Any, Optional

base_dir = os.path.dirname(os.path.abspath(__file__))+ "//base_dir"
json_path_result = 'fileStructureResult.json'
json_path_new = 'fileStructure2.json'
json_path_operations = 'processList.json'

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

        # 递归处理子节点（确保子节点变更被捕获）
        if isinstance(new_node, dict):
            for name, child in new_node.items():
                if name.startswith("__"):
                    continue  # 跳过元数据
                # print(name)
                child_new_path = f"{new_path}/{name}" if new_path else name
                traverse(child_new_path, child)

        if op_info is None:
            # 无操作：返回递归
            return

        # 解析操作类型和原路径（格式："类型:原路径"）
        op_type, _, source_path = op_info.partition(":")

        if op_type == "create":
            # print(op_info)
            # # 新建操作：先确保父目录存在，再创建当前节点
            # parent_path = "/".join(new_path.split("/")[:-1])
            # if not path_exists(old_structure, parent_path) and parent_path:
            #     operations.append(("create_dir", parent_path))  # 递归创建父目录
            if isinstance(new_node, dict):
                operations.append(("create", new_path))  # 新建目录
            # else:
            #     # 新建文件（含内容）
            #     content = new_node.get("__content__", "")
            #     operations.append(("create_file", new_path, content))

        elif op_type == "move":
            # print(op_info)
            # 移动操作：先确保目标父目录存在，再执行移动
            # parent_path = "/".join(new_path.split("/")[:-1])
            # if not path_exists(old_structure, parent_path) and parent_path:
            #     operations.append(("create_dir", parent_path))
            operations.append(("move", source_path, new_path))

        # elif op_type == "delete":
            # print(op_info)
            # 删除操作：直接记录原路径
            # operations.append(("delete", source_path))

    # 从根目录开始遍历新结构
    traverse("", new_structure)

    result = {
        "create": {},
        "move": [],
        "delete": []  # 预留删除操作字段，保持扩展性
    }

    for op in operations:
        op_type = op[0]
        if op_type == "move":
            # 解析移动操作：(move, from_path, to_path)
            _, from_path, to_path = op
            result["move"].append({
                "from": from_path,
                "to": to_path
            })
        elif op_type == "create":
            # 解析创建操作：(create, path)
            _, path = op
            # 对于目录，值为空字典；若为文件可后续扩展为内容
            result["create"][path] = {}
        elif op_type == "delete":
            # 解析删除操作：(delete, path)
            _, path = op
            result["delete"].append(path)

        # 转换为JSON字符串，确保键的顺序（Python 3.7+字典保留插入顺序）

    # result = json.dumps(result, indent=2)
    fileUtils.save_content(result, json_path_operations)

    return result
    # return operations

def execute_operations(json_path):
    try:
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            operations = json.load(f)

        # 确保creates操作优先执行
        if 'create' in operations:
            for path in operations['create']:
                basicFunction.create_dir(path)

        # 执行移动操作
        if 'move' in operations:
            for move_op in operations['move']:
                from_path = move_op['from']
                to_path = move_op['to']
                # 判断是否为文件（通过扩展名或路径特征）
                if fileUtils.is_file(from_path) or fileUtils.is_file(to_path):
                    basicFunction.move_file(from_path, to_path)
                else:
                    basicFunction.move_dir(from_path, to_path)

        print("所有操作执行完毕")

    except Exception as e:
        print(f"执行操作时出错: {e}")
    return True

def transfer_result_json(path):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            json_content = json.load(f)
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return False
    old_json = {}

    def process_directory(dir_content):

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

    # 原先的文件夹结构
    # fileUtils.display_directory_tree(base_dir + "//年度总结")

    # # 新变化的json结构
    # fileUtils.save_content(transfer_result_json(json_path_result), json_path_new)
    # fileUtils.display_json_tree(json_path_new)

    # 生成操作序列
    # generate_operations_from_json(json_path_result)

    # 执行操作序列
    # execute_operations(json_path_operations)

    # 查看变更结果
    fileUtils.display_directory_tree(base_dir + "//年度总结")



