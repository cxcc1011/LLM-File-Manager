import json
from openai import OpenAI

import fileUtils

api_key = 'sk-2e114b19f0694b739d81363ba728d596'
json_file = 'fileStructure2.json'

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
    
    The user will provide some description of their new project. Please parse the description and create project's structure and output them in JSON format. 
    
    NOTE: JSON standard allows only double quoted string.

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
        }
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

    fileUtils.save_content(result, json_file)

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

    fileUtils.save_content(result, json_file)

    messages.append(response.choices[0].message)

    return messages


if __name__ == '__main__':
    # invoke_test()
    # check()
    description = input("请输入描述").strip()
    messages = creating_mode_invoke(description)
    description = input("请输入改进需求").strip()
    messages = creating_mode_iterate(description, messages)
    print(messages)