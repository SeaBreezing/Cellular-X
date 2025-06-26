# Cellular-X: An LLM-empowered Cellular Agent for Efficient Base Station Operations
## Introduction
* This repository contains implementation for paper '[Cellular-X: An LLM-empowered Cellular Agent for Efficient Base Station Operations](https://arxiv.org/abs/2504.13190)', accepted by The 23rd ACM International Conference on Mobile Systems, Applications, and Service. (ACM MobiSys 2025).
* Check our [demo video here](https://youtube.com/playlist?list=PLi7wIohZ9VLjfbtShawzEk49BKUE11QiU&si=Ih86vVVVR10rZNvg)</br>
[![](https://github.com/SeaBreezing/Cellular-X/blob/main/IMG/subsystem.png)](https://youtube.com/playlist?list=PLi7wIohZ9VLjfbtShawzEk49BKUE11QiU&si=itgn1zcYQcKRmPOV "")
## Features
* Demo1: Automatic cellular network base station configuration
* Demo2: Retrieve base station maintenance knowledge with voice commands (*powered by OpenAI Whisper*)
* Demo3: Real-time configuration reporting and revision
## Environment & Setup
* We build a practical BS and an associated user equipment (UE) using two USRP X310. Each USRP's host PC is powered by an AMD Ryzen 1950X processor and the Ubuntu 18.04 operating system.
* Prepare two host PCs. PC1 is for BS building and UI display, PC2 is for UE connection.
* Follow [USRP setup tutorial](https://github.com/SeaBreezing/Cellular-X/blob/main/USRP%20setup%20tutorial.md) to prepare your RF device on PC1 and PC2 respectively. 
* Follow [srsRAN 4G Installation Guide](https://docs.srsran.com/projects/4g/en/latest/general/source/1_installation.html#gen-installation) to prepare your srsRAN environment on PC1 and PC2.
* To check your environment, run `srsran`, `srsenb` on PC1 and `srsue` on PC2. You will see `Network attach successful` on PC2 as output if the connection is successful.
* Install the following libraries for API calling, UI display, and audio setup requirements.
  ```
  git clone https://github.com/SeaBreezing/Cellular-X.git
  cd Cellular-X
  pip install -r requirements.txt
  ```
* For PC1, install `tmux` for BS setup logging display. For both PCs, install `figlet` for UI display and `sshpass` for ssh password-free login.
  ```
  sudo apt install tmux figlet sshpass
  ```
## Data preparation
For demo2, run the following commands to obtain [LlamaIndex](https://github.com/run-llama/llama_index)-parsed chunks from [TSpec-LLM](https://huggingface.co/datasets/rasoul-nikbakht/TSpec-LLM). Change the chunk size `W` in `save_to_index.py` for different chunk size. Parsed results are saved in `rag_experiment/3GPP-index_W`.
```
cd rag_experiments
python save_to_index.py
```

## Getting Started
Before building up the cellular network, update your system information in [system_config.txt](LTE_experiments/prompts/system_config.txt) and update your host PC information at [tmux_utils.py](LTE_experiments/tmux_utils.py).
```
host1, passwd1 = ('root@xxx.xxx.xxx.xxx', "your_password")
host2, passwd2 = ('root@xxx.xxx.xxx.xxx', "your_password")
```

To automatically build a cellular network as in demo1, run the following commands on PC1. 
```
cd LTE_experiments
tmux new-session -t lte
python build_LTE.py
```

To acquire an allowable parameter for BS as in demo2, run the following commands on PC1. 
```
cd rag_experiments
python query.py
```

To have the agent report latest configuration and revise specific parameters as in demo3, run the following commands on PC1. 
```
cd LTE_experiments
tmux new-session -t lte
python user_revision.py
```

## Citation
If this repository is useful for your research, please cite:
```bibtex
@inproceedings{Cellular-X2025,
      title={Cellular-X: An LLM-empowered Cellular Agent for Efficient Base Station Operations},
      booktitle = {The 23rd ACM International Conference on Mobile Systems, Applications, and Services (MobiSys Demo)},
      author={Liujianfu Wang and Xinyi Long and Yuyang Du and Xiaoyan Liu and Kexin Chen and Soung Chang Liew},
      year={2025}
}
```
