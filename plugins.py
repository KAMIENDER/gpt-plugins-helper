import os, json, re, requests
from constant import ENV_OPENAI_API_KEY, ENV_MODEL_NAME

# 这里可以改成你要的配置
class AIConfig():
    UserRole = "user"
    AIRole = "assistant"
    Temperature = 0.7
    
    def prompt(self) -> str:
        with open('info.txt', 'r', encoding='utf-8') as file:
            data = file.read()

            # 解析 JSON
            json_data = json.loads(data)
        out : str = "接下来我会给你一些gpt的插件信息，格式为(其中***表示内容)：\n\
            Name(名称):***\n\
            Function and Description(功能和描述):***\n\
            你根据我的需要从里面挑选出最适合的3个插件推荐给我。\n\
            插件列表如下:\n"
        for d in json_data['items']:
            out = out + "Name(名称):" + d['manifest']['name_for_human'] + "\n" + "Function and Description(功能和描述):" + d['manifest']['description_for_human'] + "\n"
        return out
    
# 我想要帮我制定营销策略的插件

def get_code(user_prompt: str):
    user_openai_key = os.environ.get(ENV_OPENAI_API_KEY, None)
    if user_openai_key is None:
        raise Exception("OPENAI_API_KEY Not set")
    model_name = os.environ.get(ENV_MODEL_NAME, None)
    if model_name is None:
        raise Exception("MODEL_NAME Not set")

    now_msg = {"role": AIConfig.UserRole, "content": user_prompt}
    message_array = [
        {
            "role": "system",
            "content": AIConfig().prompt(),
        },
    ]
    message_array.append(now_msg)

    data = {
        "model": model_name,
        "messages": message_array,
        "temperature": AIConfig().Temperature,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {user_openai_key}",
    }

    response = requests.post(
        f"https://api.openai.com/v1/chat/completions",
        data=json.dumps(data),
        headers=headers,
    )

    def extract_code(text):
        # Match triple backtick blocks first
        triple_match = re.search(r'```(?:\w+\n)?(.+?)```', text, re.DOTALL)
        if triple_match:
            return triple_match.group(1).strip()
        else:
            # If no triple backtick blocks, match single backtick blocks
            single_match = re.search(r'`(.+?)`', text, re.DOTALL)
            if single_match:
                return single_match.group(1).strip()
        # If no code blocks found, return original text
        return text

    if response.status_code != 200:
        return "Error: " + response.text, 500

    # Append all messages to the message buffer for later use
    code = extract_code(response.json()["choices"][0]["message"]["content"])
    return code, 200


if __name__ == '__main__':
    prompt = input("Please provide your requirements for the plugin(请输入你对插件的要求):")
    out = get_code(prompt)
    print(out[0])