import subprocess
import time, os
from tmux_utils import tmux_session, kill_tasks

def delete_all_files_in_directory(directory):
    # 检查目录是否存在
    if os.path.exists(directory):
        # 遍历目录下的所有文件
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # 检查是否为文件并删除
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"{file_path} removed.")
    else:
        print("directory does not exit")

def clear_tmux_session():
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.3}', f'exit', 'C-m'])
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.3}', f'exit', 'C-m'])
    time.sleep(0.1)
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.2}', f'exit', 'C-m'])
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.2}', f'exit', 'C-m'])
    time.sleep(0.1)
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.1}', f'exit', 'C-m'])
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.1}', f'exit', 'C-m'])

if __name__ == "__main__":
    kill_tasks()
    clear_tmux_session()
    delete_all_files_in_directory('./config_errors')
    delete_all_files_in_directory('./generated_LTE_config')