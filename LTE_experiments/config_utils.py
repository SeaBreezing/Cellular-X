# -- coding: utf-8 --**
import os
# from networkx import condensation
import scp
import json
import subprocess
import asyncio
import asyncssh
import fastapi_poe as fp
from openai import OpenAI
from typing import Union, Dict, List

from langchain.memory import ConversationBufferMemory
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import paramiko
from tmux_utils import *

config_errors_dir = "config_errors"
generated_config_dir = "generated_LTE_config"
USE_POE_KEY = False
CLAUDE_KEY = "your_api_key"

class CustomLLMChain:
    def __init__(self, memory, prompt_template, api_key, bot_name):
        self.memory = memory
        self.prompt_template = prompt_template
        self.api_key = api_key
        self.bot_name = bot_name

    def convert_role(self, message) -> Union[None, str]:
        if isinstance(message, HumanMessage):
            return "user"
        if isinstance(message, AIMessage):
            return "bot"
        if isinstance(message, SystemMessage):
            return "system"
        return None

    def run(self, inputs):
        memory_content = self.memory.load_memory_variables({})
        chat_history = memory_content.get("chat_history", [])

        if not isinstance(chat_history, list):
            raise Exception("invalid chat history type")
        if all(isinstance(msg, HumanMessage) or isinstance(msg, AIMessage) for msg in chat_history):
            chat_history = [{"role": self.convert_role(msg), "content": msg.content} for msg in chat_history]

        current_user_input = inputs["query"][0]["content"]

        messages = chat_history + [{"role": "user", "content": current_user_input}]
        if not USE_POE_KEY:
            response = get_gpt_responses(messages, self.bot_name)
        else:
            response = custom_chat_completion(messages, self.bot_name, self.api_key)
        self.memory.save_context({"input": current_user_input}, {"output": response})
        return response

async def get_poe_responses(messages, bot_name, api_key):
    response = ""
    async for partial in fp.get_bot_response(messages=messages, bot_name=bot_name, api_key=api_key):
        response += partial.text
    response = response.encode("utf-8").decode("unicode_escape")
    return response

def custom_chat_completion(messages: List[Dict[str, str]], bot_name: str, api_key: str) -> str:
    protocol_messages = [fp.ProtocolMessage(role=msg["role"], content=msg["content"]) for msg in messages]

    try:
        response = asyncio.run(get_poe_responses(protocol_messages, bot_name, api_key))
        return response
    except Exception as e:
        print(f"Error in Poe bot: {e}")
        return ""
    
def get_gpt_responses(messages: List[Dict[str, str]], bot_name: str) -> str:
    result = None
    # client = OpenAI(
    #     base_url="your_url",
    #     api_key=OPENAI_KEY,
    # )
    client = OpenAI(
        base_url="your_url",
        api_key=CLAUDE_KEY,
    )

    openai_messages = []
    for m in messages:
        role = 'assistant' if m['role'] == 'bot' else m['role']
        openai_messages.append({ 'role': role, 'content': m['content'] })
    # print(f"{openai_messages = }")

    completion = client.chat.completions.create(
        model = bot_name, # you can also use "gpt-4-1106-preview", or "gpt-4-32k"
        # model = "gpt-4-1106-preview",
        # model = "gpt-4-32k",
        messages = openai_messages,
        temperature = 0.3,
        stream = True
    )
    # get GPT response
    response = ""
    for chunk in completion:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content
    result = response
    return result

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt_template = ChatPromptTemplate(
    messages=[
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{query}")
    ]
)
# import openai
# openai.api_key = "sk-oSr5tYj0sRSGtlrcootbuH1rkjjbspyRq0c4uiLhpVyAZpx2"
# openai.base_url="https://oneapi.xty.app/v1"
# client = openai.OpenAI(
#     api_key = "sk-oSr5tYj0sRSGtlrcootbuH1rkjjbspyRq0c4uiLhpVyAZpx2",
#     base_url = "https://oneapi.xty.app/v1",
# )
# response = client.chat.completions.create(
#     model = 'gpt-4o',
#     messages = condensation
# )
conversation_chain = CustomLLMChain(
    memory=memory,
    prompt_template=prompt_template,
    api_key="ZtsSd29GUzuz2KZt8Qw7BOFg2mlixlkH_z8HsHG4788",
    # bot_name="gpt-4",
    # bot_name="Claude-3.5-Sonnet",
    # bot_name="Claude-3.7-Sonnet",
    # bot_name="claude-3-5-sonnet-20241022",
    # bot_name = "claude-3-7-sonnet-20250219",
    bot_name="claude-3-5-sonnet-20240620",
)

def count_error_samples(config_path: str = config_errors_dir) -> int:
    return len([d for d in os.listdir(config_path) if os.path.isdir(os.path.join(config_path, d)) and d.isdigit()])

def parse_config(config_contents: str) -> Union[None, Dict]:
    config_contents = config_contents.strip('```json\n')
    try:
        configs = json.loads(config_contents, strict=False)
    except Exception as e:
        open("parse_fail.json", "w").write(config_contents)
        print("Contents could not be parsed!")
        return None
    return configs

def remove_configs(config_path: str = generated_config_dir) -> None:
    os.path.exists(config_path) or os.mkdir(config_path)
    os.system(f"rm -f {config_path}/*")

def write_configs(configs: dict, config_path: str = generated_config_dir):
    """write configuration files to default LTE configuration folder"""
    for config_name in configs:
        with open(f"{config_path}/{config_name}", "w") as f:
            f.write(configs[config_name])
        # print(f"Config: {config_name} saved")

def save_logs(log_path: str = config_errors_dir, config_path: str = generated_config_dir):
    """Save logs to error sample folder"""
    cnt = count_error_samples()
    os.mkdir(f"{log_path}/{cnt}")
    for config, host in zip(['epc', 'enb'], ["root@192.168.81.50", "root@192.168.81.50"]):
        subprocess.run(f"cp {config_path}/{config}.conf {log_path}/{cnt}/{config}.conf", shell=True)
        subprocess.run(
            f'sshpass -p "qwe123" scp {host}:/root/.config/srsran/{config}.log {log_path}/{cnt}/{config}.log',
            shell=True
        )

def apply_configs(config_path: str = generated_config_dir):
    for config in os.listdir(config_path):
        subprocess.run(
            f'sshpass -p "qwe123" scp {config_path}/{config} {config_to_host(config)}:/root/.config/srsran',
            shell=True
        )

def generate_config(log_path: str = config_errors_dir, config_path: str = generated_config_dir):
    error_cnt = count_error_samples()
    prompt = """Last execution of epc and enb gives errors. Below shows the execution logs in the following format:
{"epc.conf":"EPC_CONFIGURATIONS_IN_PLAIN_TEXT", "enb.conf":"ENB_CONFIGURATIONS_IN_PLAIN_TEXT", "epc.log":"EPC_EXECUTION_RESULT", "enb.log":"ENB_EXECUTION_RESULT"}
"""
    i = error_cnt-1
    sample = {}
    sample["epc.conf"] = open(f"{log_path}/{i}/epc.conf").read()
    sample["enb.conf"] = open(f"{log_path}/{i}/enb.conf").read()
    sample["epc.log"] = open(f"{log_path}/{i}/epc.log").read()
    sample["enb.log"] = open(f"{log_path}/{i}/enb.log").read()
    prompt += f"Invalid configuration log {i+1}:\n{str(sample)}\n"
    prompt += "Check the log of the configurations carefully to avoiding making possible mistakes again. Now revise the configurations and generate epc and enb configurations again. Also, check former logs and avoid the misconfigured items.\n"
    prompt += open("prompts/system_config.txt").read()
    prompt += open("prompts/output_format.txt").read()
    # prompt += open("prompts/enb_format.txt").read()
    config_contents = conversation_chain.run({"query": [{"role": "user", "content": prompt}]})
    
    configs = parse_config(config_contents)
    while configs is None:
        prompt = "The configuration of epc/enb you just provided could not be parsed by json.loads(). Generate configurations of epc and enb again."
        config_contents = conversation_chain.run({"query": [{"role": "user", "content": prompt}]})

    remove_configs(config_path)
    write_configs(configs, config_path)
    apply_configs()
    

def load_examples(config_path: str = config_errors_dir) -> str:
    error_cnt = count_error_samples()
    if error_cnt == 0:
        return ""
    error_log = """Here are some examples of invalid configuration files together with the execution results. The format is:
{"epc.conf":"EPC_CONFIGURATIONS_IN_PLAIN_TEXT", "enb.conf":"ENB_CONFIGURATIONS_IN_PLAIN_TEXT", "epc.log":"EPC_EXECUTION_RESULT", , "enb.log":"ENB_EXECUTION_RESULT"}
The epc.log gives no error does not necessarily mean this log is corect. You should still check it carefully.
If the "enb.log" is "EMPTY", then it means the configuration execution aborted when using epc.conf as configuration file.
You should check the log and the configuration file to make sure that the epc and enb configurations are consistent, and avoid similar mistakes. For example:
1. If the logs indicate 'unrecognised option `SOME_OPTION`', then you should not use this option in the generated configuration file
2. If the logs indicate 'Could not initialize `SOME_OPTION`', then you should initialize the option in the generated configuration file
"""
    for i in range(error_cnt):
        sample = {}
        sample["epc.conf"] = open(f"{config_path}/{i}/epc.conf").read()
        sample["enb.conf"] = open(f"{config_path}/{i}/enb.conf").read()
        sample["epc.log"] = open(f"{config_path}/{i}/epc.log").read()
        sample["enb.log"] = open(f"{config_path}/{i}/enb.log").read()
        error_log += f"Invalid configuration log {i+1}:\n{str(sample)}\n"
    return error_log

def init_config():
    prompt = "I want to build an LTE network with my USRP devcies. Here are the system configurations for you. "
    prompt += open("prompts/system_config.txt").read()
    prompt += load_examples()
    prompt += open("prompts/output_format.txt").read()
    config_contents = conversation_chain.run({"query": [{"role": "user", "content": prompt}]})

    print(f"Init prompt: {config_contents}")
    configs = parse_config(config_contents)
    while configs is None:
        print('while')
        print(f"Received invalid configuration, regenerating configs...")
        prompt = "The configuration of epc/enb you just provided could not be parsed by json.loads(). Generate configurations of epc and enb again."
        config_contents = conversation_chain.run({"query": [{"role": "user", "content": prompt}]})
    remove_configs(generated_config_dir)
    write_configs(configs, generated_config_dir)
    apply_configs(generated_config_dir)

if __name__ == '__main__':
    config_contents = conversation_chain.run({"query": [{"role": "user", "content": "hello"}]})
    # config_contents = conversation_chain.run({"query": [{"role": "user", "content": "what is your name"}]})
    print(f"{config_contents = }")
    config_contents = conversation_chain.run({"query": [{"role": "user", "content": "what is your name"}]})
    print(f"{config_contents = }")
    pass