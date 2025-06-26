from typing import Tuple
import sys
import subprocess
import time

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

host1, passwd1 = ('root@172.16.77.242', "    ")
host2, passwd2 = ('root@172.16.74.93', "    ")

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

def config_to_passwd(config: str) -> str:
    d = { "epc":passwd1, "enb":passwd1, "ue":passwd2 }
    d |= { "epc.conf":passwd1, "enb.conf":passwd1, "ue.conf":passwd2 }
    d |= { "srsepc":passwd1, "srsenb":passwd1, "srsue":passwd2 }
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
    subprocess.run(['tmux', 'split-window', '-v', '-l', '66%', '-t', f'{tmux_session}:0.0'])
    subprocess.run(['tmux', 'split-window', '-h', '-l', '79%', '-t', f'{tmux_session}:0.1'])
    subprocess.run(['tmux', 'split-window', '-h', '-l', '28%', '-t', f'{tmux_session}:0.2'])
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.1}', f'sshpass -p "{passwd1}" ssh {host1}', 'C-m'])
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.2}', f'sshpass -p "{passwd1}" ssh {host1}', 'C-m'])
    subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:{0.3}', f'sshpass -p "{passwd2}" ssh {host2}', 'C-m'])

    set_cpu_performance = 'echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'
    for p in ["0.1", "0.2", "0.3"]:
        send_command_to_pane(p, set_cpu_performance)

    for i in range(1, 4):
        subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:0.{i}', "cd /root/.config/srsran", 'C-m'])
    
    for i in range(1, 4):
        subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:0.{i}', "clear", 'C-m'])
        
    for i, role in zip(range(1, 4), ["epc", "enb", "ue"]):
        subprocess.run(['tmux', 'send-keys', '-t', f'{tmux_session}:0.{i}', f"figlet {role}", 'C-m'])

def check_remote_process(host, passwd, process_name) -> int:
    """returns 0 (process not running) or the pid"""
    result = subprocess.run(
        f'sshpass -p "{passwd}" ssh {host} pgrep -f [{process_name[0]}]{process_name[1:]}',
        capture_output=True,
        text=True,
        shell=True
    )
    return 0 if result.returncode != 0 else int(result.stdout.strip('\n'))

def run(host: str, passwd: str, config: str, timeout: float = 10) -> Tuple[bool, str]:
    print(f"Starting srs{config} on remote host {host}...")
    pane_id = config_to_pane(config)

    # print the last modified time of the config file
    send_command_to_pane(pane_id, f'echo -e "\\e[33m$(basename {config}.conf) last modified on $(stat -c "%y" {config}.conf | cut -d. -f1)\\e[0m"')
    time.sleep(1)
    result = send_command_to_pane(pane_id, f'srs{config} 2>&1 | tee {config}.log')
    
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[yellow]Executing srs{config}..."),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"exec_srs{config}", total=100)
        start_time = time.time()
        while time.time() - start_time < timeout:
            pid = check_remote_process(host, passwd, f'srs{config}')
            # print(f'is srs{config} running? {pid}')
            if pid:
                time.sleep(1)
            else:
                break
        progress.update(task, completed=100)
    if pid:
        console.print(f"[green]srs{config} executes successfully![/green]")
        return True, result
    else:
        console.print(f"[red]srs{config} failed to start![/red]")
        return False, result

def kill_tasks():
    ue_pid = check_remote_process(host2, passwd2, 'srsue')
    if ue_pid > 0:
        subprocess.run(f'sshpass -p "{passwd2}" ssh {host2} kill -9 {ue_pid}', shell=True)

    enb_pid = check_remote_process(host1, passwd1, 'srsenb')
    if enb_pid > 0:
        subprocess.run(f'sshpass -p "{passwd1}" ssh {host1} kill -9 {enb_pid}', shell=True)

    epc_pid = check_remote_process(host1, passwd1, 'srsepc')
    if epc_pid > 0:
        subprocess.run(f'sshpass -p "{passwd1}" ssh {host1} kill -9 {epc_pid}', shell=True)

if __name__ == "__main__":
    # create_tmux_session()
    run("epc")