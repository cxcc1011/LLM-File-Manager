import os
import sys
import shutil
import json
import fileUtils
from pathlib import Path
from datetime import datetime

# 主要变更操作的根目录
base_dir = os.path.dirname(os.path.abspath(__file__)) + "//base_dir"

# 当前选取的根目录
json_file_old = 'fileStructure2.json'
# base_dir_old = os.path.dirname(os.path.abspath(__file__)) + '\\base_dir'

def create_dir(path):
    try:
        new_dir_path = os.path.join(base_dir,path)

        if not os.path.exists(new_dir_path):
            os.makedirs(new_dir_path)
            print(f"成功创建文件夹：{new_dir_path}")
            return True
        else:
            print(f"文件夹已存在：{new_dir_path}")
            return False

    except OSError as e:
        print(f"创建文件夹失败：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"创建文件夹失败：{e}")
        sys.exit(1)

def delete_dir(path):
    try:
        to_delete_path = os.path.join(base_dir, path)

        if any(os.scandir(to_delete_path)):
            print(f"删除失败：当前文件夹非空")
            return False

        if  os.path.exists(to_delete_path):
            shutil.rmtree(to_delete_path)
            print(f"成功删除文件夹：{to_delete_path}")
            return True
        else:
            print(f"错误：文件夹不存在：{to_delete_path}")
            return False

    except PermissionError:
        print(f"错误：没有权限删除：{to_delete_path}")
        sys.exit(1)
    except OSError as e:
        print(f"删除文件夹失败：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"删除文件夹失败：{e}")
        sys.exit(1)

def move_dir(from_path, to_path):
    try:
        from_path = Path(os.path.join(base_dir, from_path)).resolve()
        to_path = Path(os.path.join(base_dir, to_path)).resolve()

        # 检查源路径是否存在且是目录
        if not from_path.exists():
            print(f"错误: 源路径不存在 - {from_path}")
            return False

        if not from_path.is_dir():
            print(f"错误: 源路径不是文件夹 - {from_path}")
            return False

        # 检查目标路径是否已存在
        if to_path.exists():
            print(f"错误: 目标路径已存在 - {to_path}")
            return False

        # 执行移动操作
        shutil.move(from_path, to_path)
        print(f"成功移动文件夹: {from_path} -> {to_path}")
        return True

    except PermissionError:
        print(f"错误: 权限不足 - 无法移动 {from_path}")
        return False
    except OSError as e:
        print(f"错误: 移动文件夹失败 - {e}")
        return False
    except Exception as e:
        print(f"移动文件夹失败: {e}")
        return False

def read_dir(path):
    result = {}
    if not path == "" :
        path = os.path.join(base_dir, path)
    else : path = base_dir

    # 递归读取文件夹结构
    def read(path, result):
        base_name = os.path.basename(path)
        if os.path.isfile(path):
            result[base_name] = ""
        else:
            result[base_name] = {}
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    result[base_name].update(read_dir(item_path))
                else:
                    result[base_name][item] = ""
        return result

    try:
        return read(path, result)

    except Exception as e:
        print(f"读取文件夹结构失败：{e}")
        sys.exit(1)

def rename(old_path,new_path):
    try:
        old_path = os.path.join(base_dir,old_path)
        new_path = os.path.join(base_dir,new_path)

        if not os.path.exists(old_path):
            print(f"目标文件夹/文件不存在：{old_path}")
            return False

        if os.path.exists(new_path):
            print(f"新文件夹/文件名已存在：{new_path}")
            return False

        os.rename(old_path,new_path)
        print(f"成功重命名文件夹/文件:{new_path}")
        return True

    except Exception as e:
        print(f"重命名失败：{e}")
        sys.exit(1)

def move_file(from_path, to_path):
    try:
        from_path = Path(os.path.join(base_dir, from_path)).resolve()
        to_path = Path(os.path.join(base_dir, to_path)).resolve()

        # 检查源路径是否存在且是文件
        if not from_path.exists():
            print(f"错误: 源路径不存在 - {from_path}")
            return False

        if not from_path.is_file():
            print(f"错误: 源路径不是文件 - {from_path}")
            return False

        # 检查目标路径是否已存在
        if to_path.exists():
            print(f"错误: 目标路径已存在 - {to_path}")
            return False

        # 执行移动操作
        shutil.move(from_path, to_path)
        print(f"成功移动文件: {from_path} -> {to_path}")
        return True

    except PermissionError:
        print(f"错误: 权限不足 - 无法移动 {from_path}")
        return False
    except OSError as e:
        print(f"错误: 移动文件失败 - {e}")
        return False
    except Exception as e:
        print(f"移动文件失败: {e}")
        return False

def get_file_mata(path):
    try:
        path = os.path.join(base_dir, path)

        if not os.path.exists(path):
            print(f"错误: 文件 '{path}' 不存在")
            return False

        meta_info = os.stat(path)

        # 文件类型
        file_type = Path(path).suffix.lower()

        # 文件大小
        size_bytes = meta_info.st_size
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        while size_bytes >= 1024 and unit_index < len(units) - 1:
            size_bytes /= 1024
            unit_index += 1
        file_size = f"{size_bytes:.2f} {units[unit_index]}"

        # 文件最后编辑时间
        last_modified = datetime.fromtimestamp(meta_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        meta_data = {
            "type": file_type,
            "size": file_size,
            "last_modified":last_modified
        }

        print(f"文件元数据：\n类型：{meta_data['type']}\n大小：{meta_data['size']}\n最后编辑时间：{meta_data['last_modified']}")

    except Exception as e:
        print(f"读取失败：{e}")
        sys.exit(1)

if __name__=="__main__":
    # 文件夹功能测试用例
    dir_name = ""
    # dir_name_new = "test_dir1\\child_dir2"
    # new_path = "test_dir2\\child_dir"
    # rename(dir_name_new, dir_name)

    # create_dir(dir_name_new)
    # delete_dir(dir_name)
    # move_dir(new_dir_name,new_path)
    # move_dir(new_path, new_dir_name)

    fileUtils.save_content(read_dir(dir_name), json_file_old)
    fileUtils.display_json_tree(json_file_old)

    # 文件功能测试用例
    # file_name = "test_dir1\\test.txt"
    # file_name_new = "test_dir2\\test"
    # rename(file_name_new, file_name)
    # move_file(file_name, file_name_new)
    # get_file_mata(file_name)
