from typing import Tuple
import sys
import subprocess
import time

host1, passwd1 = ('root@192.168.81.50', "qwe123")
host2, passwd2 = ('root@192.168.81.90', "qwe123")

tmux_session = 'lte'

def config_to_pane(config: str) -> str:
    d = { "epc":"0.1", "enb":"0.2", "ue":"0.3" }
    d |= { "epc.conf":"0.1", "enb.conf":"0.2", "ue.conf":"0.3" }
    assert config in d
    return d[config]

def config_to_host(config: str) -> str:
    d = { "epc":host1, "enb":host1, "ue":host2 }
    d |= { "epc.conf":host1, "enb.conf":host1, "ue.conf":host2 }
    assert config in d
    return d[config]

def send_command_to_pane(pane_id: str, command: str) -> str:
    result = subprocess.run(
        f"tmux send-keys -t {tmux_session}:{pane_id} '{command}' C-m",
        capture_output=True,
        text=True,
        shell=True
    )
    # print(result)
    return "execution success" if result.returncode == 0 else result.stderr

def create_tmux_session():
    subprocess.run(['tmux', 'split-window', '-v', '-p', '70', '-t', f'{tmux_session}:0.0'])
    subprocess.run(['tmux', 'split-window', '-h', '-p', '66', '-t', f'{tmux_session}:0.1'])
    subprocess.run(['tmux', 'split-window', '-h', '-p', '50', '-t', f'{tmux_session}:0.2'])

    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.1}', f'sshpass -p "{passwd1}" ssh {host1}', 'C-m'])
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.2}', f'sshpass -p "{passwd1}" ssh {host1}', 'C-m'])
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.3}', f'sshpass -p "{passwd2}" ssh {host2}', 'C-m'])

    set_cpu_performance = 'echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'
    for p in ["0.1", "0.2", "0.3"]:
        send_command_to_pane(p, set_cpu_performance)

    for i in range(1, 4):
        subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:0.{i}', "cd /root/.config/srsran", 'C-m'])
    
def check_remote_process(host, process_name) -> int:
    """returns 0 (process not running) or the pid"""
    result = subprocess.run(
        f'sshpass -p "qwe123" ssh {host} pgrep -f [{process_name[0]}]{process_name[1:]}',
        capture_output=True,
        text=True,
        shell=True
    )
    return 0 if result.returncode != 0 else int(result.stdout.strip('\n'))

def run(host: str, config: str, timeout: float = 10) -> Tuple[bool, str]:
    print(f"Starting srs{config} on remote host {host}...")
    pane_id = config_to_pane(config)

    # print the last modified time of the config file
    send_command_to_pane(pane_id, f'echo "$(basename {config}.conf) last modified on $(stat -c "%y" {config}.conf | cut -d. -f1)"')
    time.sleep(1)
    result = send_command_to_pane(pane_id, f'srs{config} 2>&1 | tee {config}.log')
    start_time = time.time()
    while time.time() - start_time < timeout:
        pid = check_remote_process(host, f'srs{config}')
        print(f'is srs{config} running? {pid}')
        if pid:
            time.sleep(1)
        else:
            break
    else:
        print(f"srs{config} is running successfully.")
        return True, result
    print(f"srs{config} failed to start.")
    return False, result

def kill_tasks():
    epc_pid = check_remote_process(host1, 'srsepc')
    if epc_pid > 0:
        subprocess.run(f'sshpass -p "qwe123" ssh {host1} kill -9 {epc_pid}', shell=True)
    enb_pid = check_remote_process(host1, 'srsenb')
    if enb_pid > 0:
        subprocess.run(f'sshpass -p "qwe123" ssh {host1} kill -9 {enb_pid}', shell=True)
    ue_pid = check_remote_process(host2, 'srsue')
    if ue_pid > 0:
        subprocess.run(f'sshpass -p "qwe123" ssh {host2} kill -9 {ue_pid}', shell=True)

if __name__ == "__main__":
    # create_tmux_session()
    run("epc")