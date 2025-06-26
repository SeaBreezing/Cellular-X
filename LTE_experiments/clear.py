import subprocess
import time, os
from tmux_utils import tmux_session, kill_tasks

def delete_all_files_in_directory(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"{file_path} removed.")
    else:
        print("directory does not exit")

def clear_tmux_session():
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.3}', f'exit', 'C-m'])
    time.sleep(0.1)
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.2}', f'exit', 'C-m'])
    time.sleep(0.1)
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.1}', f'exit', 'C-m'])
    time.sleep(0.1)
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.3}', f'exit', 'C-m'])
    time.sleep(0.1)
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.2}', f'exit', 'C-m'])
    time.sleep(0.1)
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.1}', f'exit', 'C-m'])

if __name__ == "__main__":
    kill_tasks()
    clear_tmux_session()
    delete_all_files_in_directory('./config_errors')
    delete_all_files_in_directory('./generated_LTE_config')
    with open("./generated_LTE_config/epc.conf", "w") as f:
        pass
    with open("./generated_LTE_config/enb.conf", "w") as f:
        pass
        
