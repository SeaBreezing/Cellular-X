import argparse
import traceback
import re, os, configparser
import openai
import voice2text
from tmux_utils import *
from config_utils import *

openai.api_key = "YOUR_API_KEY_HERE"
openai.base_url="YOUR_API_FORWARDING_URL_HERE"
client = openai.OpenAI(
    api_key = "YOUR_API_KEY_HERE",
    base_url = "YOUR_API_FORWARDING_URL_HERE",
)
model = 'gpt-4'
CONFIG_FILE = "enb.conf"
DEFAULT_VOICE_REC_FILE = "user_input.wav"

def print_config(config_file):
    config = configparser.ConfigParser()
    config.read(f'generated_LTE_config/{config_file}')

    print(f'printing {config_file}:')
    for section in config.sections():
        print(f"[{section}]")
        for key, value in config.items(section):
            print(f"{key} = {value}")
        print("")

def parse_args():
    parser = argparse.ArgumentParser(description="Parser for using voice input or text input.")
    parser.add_argument("-i", "--interaction_mode", type=str, choices=["text", "voice"], default="text", help="Interact with text or voice")
    return parser.parse_args()

def get_user_input(mode: str) -> str:
    if mode == "text":
        user_input = input("Please input: ")

    elif mode == "voice":
        print("Recording your voice input...")
        user_input = None
        try:
            user_input = voice2text.v2text(DEFAULT_VOICE_REC_FILE, use_micro=True)
        except Exception as e:
            # traceback.print_exc()
            print("Error converting voice to text: ", e)
        while user_input is None:
            print(f"Please repeat your voice input.")
            try:
                user_input = voice2text.v2text(DEFAULT_VOICE_REC_FILE, use_micro=True)
            except Exception as e:
                # traceback.print_exc()
                print("Error converting voice to text: ", e)

    else:
        raise ValueError("Invalid input mode")
    return user_input

def notify_user(message: str, mode: str = "text"):
    if mode == "text":
        print(message)
    elif mode == "voice":
        voice2text.t2voice(message)
    else:
        raise ValueError("Invalid input mode")

if __name__ == '__main__':
    args = parse_args()
    
    print('Started building LTE network...')
    os.system('python build_LTE.py')
    print('LTE network started')
    print_config(CONFIG_FILE)

    print('\nPlease press Enter to continue...')
    if input() is not None:
        pass

    # User Revision
    prompt = 'Read the following configuration file and answer my question.'
    with open(f'generated_LTE_config/{CONFIG_FILE}', 'r') as f:
        content = f.read()
    prompt += content
    user_input = get_user_input(args.interaction_mode)
    print(f"User query: {user_input}")

    user_question = 'User query: '+user_input
    prompt += user_question
    prompt += "\nNote that the explaination of parameters if followed with parameter setting."
    prompt += "Below is an example."
    prompt += "Question: What is Local IP address to bind for GTP connection of eNB configuration?"
    prompt += "Your answer should be: In [enb] setting, gtp_bind_addr is 127.0.1.1."""

    # retrieve gpt response for config query
    conversation = []  
    conversation.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(model = model, messages = conversation)
    gpt_response = response.choices[0].message.content.strip()
    conversation.append({"role": "assistant", "content": gpt_response})
    notify_user("GPT response: "+gpt_response)
    time.sleep(0.5)

    # get user revision
    user_input = get_user_input(args.interaction_mode)
    print(f"User revision: {user_input}")
    user_revision = 'User: '+ user_input

    # retrieve gpt response for config revision
    revision_prompt = user_revision + 'Answer strictly in this format as "[{section}]{parameter} = 4". Equal sign should be used instead of any word. Do not add additional explaination.'
    conversation.append({"role": "assistant", "content": revision_prompt})
    response = client.chat.completions.create(model = model, messages = conversation)
    response = response.choices[0].message.content.strip()
    # print(response)

    # Matching config in the configuration file
    pattern = r'\[(\w+)\].*?(\w+)\s*=\s*(\w+)'
    match = re.search(pattern, response)
    if match:
        output = match.groups()
        # print(f"Match found: {output}")
    else:
        print("Match error")

    # Update config parameters
    section = output[0]
    new_para = output[1]
    new_value = output[-1]

    config = configparser.ConfigParser()
    config.read(f'generated_LTE_config/{CONFIG_FILE}')
    if section in config:
        config[section][new_para] = new_value
        notify_user('Revision finished.', mode=args.interaction_mode)
        print(f'Updated enb configuration:')
        for section in config.sections():
            print(f"[{section}]")  # print section title
            for key, value in config.items(section):
                print(f"{key} = {value}")  # print key value pair
            print("")
    else:
        print(f"Section '{section}' not found in the config file.")

    with open(f'generated_LTE_config/{CONFIG_FILE}', 'w') as f:
        config.write(f)

    notify_user('New configuration applied. Do you want to rebuild LTE network now?', mode=args.interaction_mode)
    user_input = get_user_input(args.interaction_mode)
    # user_input = input("Do you want to rebuild LTE network now? (yes/no): ")
    print(f"User response: {user_input}")
    if 'yes' in user_input.lower():
        print(f"Restarting LTE network...")
        kill_tasks()
        time.sleep(1)
        # print config
        isRunning_epc, output = run(host=host1, passwd=passwd1, config="epc", timeout=4)
        isRunning_enb, output = run(host=host1, passwd=passwd1, config="enb", timeout=30)
        isRunning_ue, output = run(host=host2, passwd=passwd2, config="ue", timeout=10)
        if isRunning_epc and isRunning_enb and isRunning_ue:
            print('LTE network starts successfully!')
    else:
        print("Building LTE network cancelled")
