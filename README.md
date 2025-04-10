# Cellular-X: An LLM-empowered Cellular Agent for Efficient Base Station Operations
## Introduction
* The Pytorch implementation for our paper '[Cellular-X: An LLM-empowered Cellular Agent for Efficient Base Station Operations]'
* [Our demo video](https://youtube.com/playlist?list=PLi7wIohZ9VLjfbtShawzEk49BKUE11QiU&si=Ih86vVVVR10rZNvg)</br>
![](https://github.com/SeaBreezing/Cellular-X/blob/main/IMG/subsystem.png)
## Environment & Setup
* We build a practical BS and an associated user equipment (UE) using two USRP X310. Each USRP’s host PC is powered by an AMD Ryzen 1950X processor and the Ubuntu 18.04 operating system.
* Prepare three hostPCs. PC1 is for BE building, PC2 is for UE building. PC3 is for master control to manage PC1 and PC2.
* Follow [USRP setup tutorial](https://github.com/SeaBreezing/Cellular-X/blob/main/USRP%20setup%20tutorial.md) to prepare your own USRP device from scratch on PC1 and PC2.
* Follow [SRSRAN 4G Installation Guide](https://docs.srsran.com/projects/4g/en/latest/general/source/1_installation.html#gen-installation) to prepare your SRSRAN environment on PC1 and PC2.
* To check your environment, run `srsran`, `srsenb` on PC1 and `srsue` on PC2. You will see `Network attach successful` on PC2 as output if your settings are correct.
## Data preparation
* For demo2, run
```
cd rag_experiments
python save_to_index.py
```
to obtain [Llama-Index](https://github.com/run-llama/llama_index) parsed chunking from from [TSpec-LLM](https://huggingface.co/datasets/rasoul-nikbakht/TSpec-LLM). Parsed results are saved in `rag_experiment/3GPP-index_1024` and `rag_experiment/3GPP-index_2048`.
## Getting Stared
To automatically build a cellular network as demo1, run the following commands on PC3. 
```
cd LTE_experiment
python build_LTE.py
```
To acquire an allowable parameter for BS as demo2, run the following commands on PC3. 
```
cd rag_experiments
python query.py
```
To have the agent report latest configuration and revise specific parameters as demo3, run the following commands on PC3. 
```
cd rag_experiments
python query.py
```
## Citation
If this repository is useful for your research, please cite:
```

```
