import argparse
from typing import Tuple
from tmux_utils import *
from config_utils import *
import pdb

def main():
    create_tmux_session()
    init_config()
    print('Finished Initialization')
    epc_success, enb_success, ue_success, iteration = False, False, False, 0
    execution_successs = True
    while (not epc_success or not enb_success or not ue_success) and iteration < 30:
        if not execution_successs:
            iteration += 1
            print("="*20+f" Attempt: {iteration} "+"="*20)

        if not epc_success:
            isRunning, output = run(host=host1, passwd=passwd1, config="epc", timeout=2)
            if isRunning:
                epc_success = execution_successs = True
            else:
                send_command_to_pane(config_to_pane("enb"), 'echo "EMPTY" > enb.log')
                epc_success = execution_successs = False

        elif not enb_success:
            isRunning, output = run(host=host1, passwd=passwd1, config="enb", timeout=15)
            if isRunning:
                enb_log = get_remote_file_contets(host1, passwd1, "/root/.config/srsran/enb.log")
                if "Network is unreachable" in enb_log:
                    print("Network is unreachable!")
                    epc_success = enb_success = execution_successs = False
                    kill_tasks()
                else:
                    enb_success = execution_successs = True
            else:
                epc_success = enb_success = execution_successs = False
                kill_tasks()
        
        elif not ue_success:
            isRunning, output = run(host=host2, passwd=passwd2, config="ue", timeout=8)
            if isRunning:
                ue_log = get_remote_file_contets(host2, passwd2, '/root/.config/srsran/ue.log')
                if "Network attach successful." not in ue_log:
                    print("UE connection failed.")
                    epc_success = enb_success = ue_success = execution_successs = False
                    kill_tasks()
                else:
                    ue_success = execution_successs = True
                    print("LTE network started.")
                    break
            else:
                ue_success = epc_success = enb_success = execution_successs = False
                kill_tasks()
        
        else:
            print("LTE network started.")
            break
        
        if not execution_successs:
            save_logs(config_errors_dir, generated_config_dir)
            generate_config(log_path=config_errors_dir, config_path=generated_config_dir)


if __name__ == "__main__":
    main()