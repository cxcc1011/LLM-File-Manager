import json
from openai import OpenAI

import fileUtils

api_key = 'sk-2e114b19f0694b739d81363ba728d596'
json_path_old = 'fileStructure1.json'
json_path = 'fileStructure2.json'
json_path_result = 'fileStructureResult.json'

# Please install OpenAI SDK first: `pip3 install openai`

def check():
    # for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    print(client.models.list())

def invoke_test():
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello,Who are you?"},
        ],
        stream=False
    )

    print(response.choices[0].message.content)

def creating_mode_invoke(user_input):
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt = """
    You are a professional file system organizer.
    
    The user will provide some description of their new project. 
    Please parse the description and create project's structure and output them in JSON format. 
    Attach a brief, reasonable explanation of the output content.
    
    NOTE: 
    1.JSON standard allows only double quoted string.
    2.Use chinese as the output's default language.

    EXAMPLE INPUT: 
    I want to start a data-science research. It includes codes, data, and result analyzing.

    EXAMPLE JSON OUTPUT:
    {
        "data_science_project": {
            "docs": {
                "proposals": {},
                "reports": {}
            },
            "data": {
                "raw": {},
                "processed": {}
            },
            "src": {
                "data_processing": {},
                "models": {}
            },
            "results": {
                "figures": {},
                "tables": {}
            },
            "tests": {}
        },
        "reason" : "this project include folders like docs,data,src,results,tests, which is very convenient for data researchers"
    }
    """
    user_prompt = user_input

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    # 解析响应并保存到文件
    result = json.loads(response.choices[0].message.content)

    reason = result.pop("reason", None)
    print(result)
    print(reason)

    fileUtils.save_content(result, json_path)

    messages.append(response.choices[0].message)

    return messages

def creating_mode_iterate(user_input,messages):

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    user_prompt = user_input

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    # 解析响应并保存到文件
    result = json.loads(response.choices[0].message.content)

    reason = result.pop("reason", None)
    print(result)
    print(reason)

    fileUtils.save_content(result, json_path)

    messages.append(response.choices[0].message)

    return messages

def organizing_mode_invoke(user_input):
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt = """
    You are a professional file system organizer.
    
    The user will provide an existing file directory structure and their desired changes. 
    
    Based on these requirements, output a JSON file representing the modified file directory.
    
    The input directory structure‘s schema ：
    {
      "base_dir": {
        "test_dir1": {
          "child_dir": {},
          "test.txt": ""
        },
        "test_dir2": {
          "test.txt": ""
        },
        "test.txt": ""
      }
    }Among them, {} represents a folder, and "" represents a file.
    
    The output‘s schema ：
    {
      "年度总结": {
        "__operation__": null,
        "技术部": {
          "__operation__": null,
          "文档": {
            "__operation__": "create:",
            "工作总结.docx": {
              "__operation__": "move:年度总结/技术部/工作总结.docx",
              "__content__": ""
            }
          }
        }
      }
    }Among them, __operation__ represents change operations, including three types: create, move, and rename.
     If there is no operation, it is represented by null; __content__ is an attribute unique to files, and it is generally empty.
    
    EXAMPLE INPUT 1: 
    user description ：市场部 Q3 活动策划的相关文件分散在 “临时存放” 和 “素材库” 文件夹中，导致团队成员查找资料时需切换多个目录，影响工作效率。
    directory structure：
    {
      "市场部项目": {
        "Q3活动策划": {},
        "临时存放": {
          "活动流程.docx": "",
          "预算表.xlsx": ""
        },
        "素材库": {
          "宣传海报.psd": "",
          "活动视频.mp4": ""
        }
      }
    }
    
    EXAMPLE OUTPUT 1: 
    {
      "市场部项目": {
        "__operation__": null,
        "Q3活动策划": {
          "__operation__": null,
          "活动流程.docx": {
            "__operation__": "move:市场部项目/临时存放/活动流程.docx",
            "__content__": ""
          },
          "预算表.xlsx": {
            "__operation__": "move:市场部项目/临时存放/预算表.xlsx",
            "__content__": ""
          },
          "宣传海报.psd": {
            "__operation__": "move:市场部项目/素材库/宣传海报.psd",
            "__content__": ""
          },
          "活动视频.mp4": {
            "__operation__": "move:市场部项目/素材库/活动视频.mp4",
            "__content__": ""
          }
        },
        "临时存放": {
          "__operation__": null
        },
        "素材库": {
          "__operation__": null
        }
      }
    }
    reason：将所有与 Q3 活动相关的文件集中至 “Q3 活动策划” 文件夹，实现项目资料的统一管理。

    EXAMPLE INPUT 2: 
    user description ：年度工作总结项目的文件混乱存放，既有按部门划分的子文件夹，也有直接存放在根目录的汇总文件，需按 “部门 - 文档类型” 二级结构整理。
    directory structure：
    {
      "年度总结": {
        "技术部": {
          "工作总结.docx": "",
          "数据统计.xlsx": ""
        },
        "市场部": {
          "活动总结.pptx": ""
        },
        "全公司汇总.docx": "",
        "预算分析.xlsx": ""
      }
    }
    
    EXAMPLE OUTPUT 2: 
    {
      "年度总结": {
        "__operation__": null,
        "技术部": {
          "__operation__": null,
          "文档": {
            "__operation__": "create:",
            "工作总结.docx": {
              "__operation__": "move:年度总结/技术部/工作总结.docx",
              "__content__": ""
            }
          },
          "数据": {
            "__operation__": "create:",
            "数据统计.xlsx": {
              "__operation__": "move:年度总结/技术部/数据统计.xlsx",
              "__content__": ""
            }
          }
        },
        "市场部": {
          "__operation__": null,
          "演示文稿": {
            "__operation__": "create:",
            "活动总结.pptx": {
              "__operation__": "move:年度总结/市场部/活动总结.pptx",
              "__content__": ""
            }
          }
        },
        "全公司": {
          "__operation__": "create:",
          "文档": {
            "__operation__": "create:",
            "全公司汇总.docx": {
              "__operation__": "move:年度总结/全公司汇总.docx",
              "__content__": ""
            }
          },
          "数据": {
            "__operation__": "create:",
            "预算分析.xlsx": {
              "__operation__": "move:年度总结/预算分析.xlsx",
              "__content__": ""
            }
          }
        }
      }
    }
    reason：建立清晰的层级结构，方便跨部门查阅和汇总分析，提升年终汇报准备效率。
    
    EXAMPLE INPUT 3:
    user description ：某学生整理课程作业项目文件，需将零散命名的文件按规范重命名，方便后续查阅和提交
    directory structure：
    {
      "course_work": {
        "hw": {
          "doc1.docx": "",
          "doc2.docx": "",
          "img": {
            "pic1.png": "",
            "screenshot.jpg": ""
          }
        },
        "readme.md": ""
      }
    }
    
    EXAMPLE OUTPUT 3: 
    {
      "course_work": {
        "__operation__": null,
        "hw": {
          "__operation__": null,
          "作业1_初稿.docx": {
            "__operation__": "rename:course_work/hw/doc1.docx",
            "__content__": ""
          },
          "作业1_终稿.docx": {
            "__operation__": "rename:course_work/hw/doc2.docx",
            "__content__": ""
          },
          "img": {
            "__operation__": null,
            "图表1.png": {
              "__operation__": "rename:course_work/hw/img/pic1.png",
              "__content__": ""
            },
            "screenshot.jpg": {
              "__operation__": null,
              "__content__": ""
            }
          }
        },
        "readme.md": {
          "__operation__": null,
          "__content__": ""
        }
      }
    }


    
    NOTE: 1.JSON standard allows only double quoted string.
    2.Carefully check to ensure consistency in the attributes of folders and files before and after the operation.Guarantee that no existing files are lost.
    3.folders only have __operation__ and other child nodes and don't exist __content__ attribute！
    """

    user_prompt = user_input

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    # 解析响应并保存到文件
    result = json.loads(response.choices[0].message.content)

    fileUtils.save_content(result, json_path_result)

    messages.append(response.choices[0].message)

    return messages

def organizing_mode_iterate(user_input,messages):

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    user_prompt = user_input

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    # 解析响应并保存到文件
    result = json.loads(response.choices[0].message.content)

    fileUtils.save_content(result, json_path_result)

    messages.append(response.choices[0].message)

    return messages

if __name__ == '__main__':

    # invoke_test()
    # check()
    description = input("请输入描述").strip()
    messages = creating_mode_invoke(description)
    description = input("请输入改进需求").strip()
    messages = creating_mode_iterate(description, messages)
    # print(messages)

    ''' 文件内容优化测试'''
    # try:
    #     with open(json_path_old, 'r', encoding='utf-8-sig') as f:
    #         json_content = json.load(f)
    #         print(json_content)
    # except FileNotFoundError:
    #     print("Error: JSON file not found.")
    #
    # description = input("请输入描述").strip()
    # formatted_json = json.dumps(json_content, ensure_ascii=False, indent=2)
    # full_description = f"user description: {description}\ndirectory structure:\n{formatted_json}"
    # # print(full_description)
    #
    # messages = organizing_mode_invoke(full_description)
    # # print(messages)
    # description = "改进需求：" + input("请输入改进需求").strip()
    # messages = organizing_mode_iterate(description, messages)
    # # print(messages)
