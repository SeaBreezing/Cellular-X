import openai
import re, os, configparser
from typing import Tuple
from tmux_utils import *
from config_utils import *
import pdb
openai.api_key = "sk-oSr5tYj0sRSGtlrcootbuH1rkjjbspyRq0c4uiLhpVyAZpx2"
openai.base_url="https://oneapi.xty.app/v1"
client = openai.OpenAI(
    api_key = "sk-oSr5tYj0sRSGtlrcootbuH1rkjjbspyRq0c4uiLhpVyAZpx2",
    base_url = "https://oneapi.xty.app/v1",
)
model = 'gpt-4'
prompt = 'Read the following configuration file and answer my question.'
print('build started')
os.system('python build_LTE.py')
print('build finished')
time.sleep(2)

config = configparser.ConfigParser()
config.read('generated_LTE_config/enb.conf')

print(f'eNB configurations:')
for section in config.sections():
    print(f"[{section}]")
    for key, value in config.items(section):
        print(f"{key} = {value}")
    print()

if input() is not None:
    pass
kill_tasks()

# User Revision
with open('generated_LTE_config/enb.conf', 'r') as f:
    content = f.read()
prompt += content
time.sleep(2)
user_question = 'User: '+'What is receive gain of RF configuration?'
time.sleep(1)
print(user_question)
prompt += user_question
prompt += 'Note that the explaination of parameters if followed with parameter setting.'
prompt += 'Here I give you an example.'
prompt += 'Question: What is Local IP address to bind for GTP connection of eNB configuration?'
prompt += 'Your answer should be: In [enb] setting, gtp_bind_addr is 127.0.1.1.'

conversation = []  
user_input = prompt
conversation.append({"role": "user", "content": user_input})
response = client.chat.completions.create(
    model = model,
    messages = conversation
)
gpt_response = response.choices[0].message.content.strip()
conversation.append({"role": "assistant", "content": gpt_response})
time.sleep(1)
print("GPT-4:", gpt_response)
user_revision = 'User: '+'Revise the parameter you just answered to 45.'
time.sleep(1)
print(user_revision)
revision_prompt = user_revision + 'Answer strictly in this format as "[{section}]{parameter} = 4". Equal sign should be used instead of any word'
conversation.append({"role": "assistant", "content": revision_prompt})
response = client.chat.completions.create(
    model = model,
    messages = conversation
)
response = response.choices[0].message.content.strip()
# print(response)

# Matching
pattern = r'\[(\w+)\].*?(\w+)\s*=\s*(\w+)'
match = re.search(pattern, response)
if match:
    output = match.groups()
    # print(f"Match found: {output}")
else:
    print("Match error")

# Update parameters
section = output[0]
new_para = output[1]
new_value = output[-1]


config = configparser.ConfigParser()
config.read('generated_LTE_config/enb.conf')
if section in config:
    config[section][new_para] = new_value
    print('Revision finished.')
    print(f'Updated enb configuration:')
    for section in config.sections():
        print(f"[{section}]")  # 打印 section 的标题
        for key, value in config.items(section):
            print(f"{key} = {value}")  # 打印键值对
        print()  # 每个 section 后插入一个空行
else:
    print(f"Section '{section}' not found in the config file.")

with open('generated_LTE_config/enb.conf', 'w') as configfile:
    config.write(configfile)

time.sleep(3)
user_input = input("Do you want to rebuild LTE network now? (yes/no): ")

if user_input.lower() == 'yes':
    time.sleep(1)
    # print config
    isRunning_epc, output = run(host=host1, config="epc", timeout=4)
    isRunning_enb, output = run(host=host1, config="enb", timeout=30)
    isRunning_ue, output = run(host=host2, config="ue", timeout=10)
    if isRunning_epc and isRunning_enb and isRunning_ue:
        print('LTE starts successfully')

else:
    print("Building LTE network cancelled")