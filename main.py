import basicFunction
import fileUtils
import newProjectProcessing
import contentRefiningProcessing
import llmManager
import os
import json
from flask import Flask,request,jsonify

base_dir = os.path.dirname(os.path.abspath(__file__)) + "//base_dir"
json_path_old = 'fileStructure1.json'
json_path = 'fileStructure2.json'
json_path_result = 'fileStructureResult.json'
json_path_operations = 'processList.json'

def get_yes_no(prompt):
    """Prompt the user for a yes/no response."""
    while True:
        response = input(prompt).strip().lower()
        if response in ('yes', 'y'):
            return True
        elif response in ('no', 'n'):
            return False
        elif response == '/exit':
            print("Exiting program.")
            exit()
        else:
            print("Please enter 'yes' or 'no'. To exit, type '/exit'.")

def get_mode_selection():
    """Prompt the user to select a mode."""
    while True:
        print("Please choose the mode to use our system:\n")
        print("1. Creating Mode (I want to start a new project) ")
        print("2. Organizing Mode (I already have a project to organize) \n")
        response = input("Enter 1 or 2 (or type '/exit' to exit): ").strip()
        if response == '/exit':
            print("Exiting program.")
            exit()
        elif response == '1':
            return 'creating mode'
        elif response == '2':
            return 'organizing mode'
        else:
            print("Invalid selection. Please enter 1 or 2. To exit, type '/exit'.")

def main():
    print("-" * 50)
    print("Welcome to file organizing system.")

    mode = get_mode_selection()
    print("-" * 40)
    print(mode)

    if mode == 'creating mode':
        flag_new_completion = True
        messages = []
        while True:
            if flag_new_completion:
                print("Please describe your project:\n")
                description = input("Enter your description: ").strip()
                # print(description)

                print("-" * 30)
                print("Your new project is under creating...")
                messages = llmManager.creating_mode_invoke(description)
                flag_new_completion = False
                print("-" * 30)
                print("Advised project's structure is as follow:\n")
                fileUtils.display_json_tree(json_path)

                if_completion = get_yes_no("\nWould you like to take the advice? (yes/no): ")
                if if_completion:
                    newProjectProcessing.creat_dir_from_json(json_path)
                    print("Your new project has been created. ")
                    break  # Exit the main loop
            else:
                print("Please describe your improvement opinions:\n")
                description = input("Enter your description: ").strip()

                print("-" * 30)
                print("Your new project is under modification...")
                messages = llmManager.creating_mode_iterate(description, messages)
                print("-" * 30)
                print("Modified project's structure is as follow:\n")
                fileUtils.display_json_tree(json_path)

                if_completion = get_yes_no("\nWould you like to take the advice? (yes/no): ")
                if if_completion:
                    newProjectProcessing.creat_dir_from_json(json_path)
                    print("Your new project has been created. ")
                    break  # Exit the main loop

    elif mode == 'organizing mode':
        flag_new_completion = True
        messages = []
        while True:
            if flag_new_completion:
                print("Please choose your root path:\n")
                root_name = input("Enter root path: ").strip()
                # root_path = base_dir + "//" + root_name
                fileUtils.save_content(fileUtils.read_metadata(root_name), json_path_old)

                """输出现有架构"""
                print("-" * 30)
                print("Your project's structure is as following:")
                fileUtils.display_json_tree(json_path_old)
                print("-" * 30)

                print("Please describe your improvement opinions:\n")
                description = input("Enter your description: ").strip()

                """读取并解析现有文件"""
                try:
                    with open(json_path_old, 'r', encoding='utf-8-sig') as f:
                        json_content = json.load(f)
                        # print(json_content)
                except FileNotFoundError:
                    print("Error: JSON file not found.")

                root_keys = list(json_content.keys())
                if len(root_keys) != 2:
                    raise ValueError("原始JSON必须包含且仅包含两个根级键")
                # 动态获取两个根键
                key1, key2 = root_keys

                # 分别创建两个新的字典
                data1 = {key1: json_content[key1]}
                data2 = {key2: json_content[key2]}

                full_description = f"user description: {description}\ndirectory input:\n{data1}\nmetadata input:\n{data2}"

                """调用LLM"""
                print("-" * 30)
                print("Your project is under modification...")
                messages = llmManager.organizing_mode_invoke_new(full_description)
                flag_new_completion = False
                print("-" * 30)
                print("Refined project's structure is as follow:\n")
                fileUtils.save_content(contentRefiningProcessing.transfer_result_json_new(json_path_result), json_path)
                fileUtils.display_json_tree(json_path)

                if_completion = get_yes_no("\nWould you like to take the advice? (yes/no): ")
                if if_completion:
                    # contentRefiningProcessing.generate_operations_from_json(json_path_result)
                    contentRefiningProcessing.execute_operations_new(json_path_result)
                    print("Advised operations have been executed. ")
                    break  # Exit the main loop
            else:
                print("Please describe your improvement opinions:\n")
                description = "改进需求：" + input("Enter your description: ").strip()

                print("-" * 30)
                print("Your project is under modification...")
                messages = llmManager.organizing_mode_iterate(description, messages)
                print("-" * 30)
                print("Refined project's structure is as follow:\n")
                fileUtils.save_content(contentRefiningProcessing.transfer_result_json_new(json_path_result), json_path)
                fileUtils.display_json_tree(json_path)

                if_completion = get_yes_no("\nWould you like to take the advice? (yes/no): ")
                if if_completion:
                    # contentRefiningProcessing.generate_operations_from_json(json_path_result)
                    contentRefiningProcessing.execute_operations_new(json_path_result)
                    print("Advised operations have been executed. ")
                    break  # Exit the main loop
        exit()

app = Flask(__name__)
@app.route("/structure", methods=["POST"])
def getStructure():
    if request.is_json:
        data = request.get_json()
        root_path = data.get("root_input")
        json_result = fileUtils.read_directory(root_path)
        fileUtils.save_content(json_result, json_path_old)
        print("接受输入成功")
        return jsonify(json_result), 200
    else:
        print("处理失败")
        return jsonify({'error': 'Request content is not JSON'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)

    ''' 接口测试专用'''
    # fileUtils.display_directory_tree(base_dir)
    # fileUtils.display_json_tree(json_file)
    # newProjectProcessing.creat_dir_from_json(json_file)
    # llmManager.invoke()
    # description = "一项人机交互研究，包括相关论文、项目代码、实验结果等部分"
    # llmManager.creating_mode_invoke(description)

    '''暂用：每次启动前清理'''
    # dir_to_delete = 'student_admission_project_2025'
    # basicFunction.delete_dir(dir_to_delete)

    # main()




