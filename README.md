# Cellular-X: An LLM-empowered Cellular Agent for Efficient Base Station Operations
## Introduction
* The Pytorch implementation for our paper '[Cellular-X: An LLM-empowered Cellular Agent for Efficient Base Station Operations]'
* [Our demo video](https://youtube.com/playlist?list=PLi7wIohZ9VLjfbtShawzEk49BKUE11QiU&si=Ih86vVVVR10rZNvg)</br>
![](https://github.com/SeaBreezing/Cellular-X/blob/main/IMG/subsystem.png)
## Environment & Setup
* We build a practical BS and an associated user equipment (UE) using two USRP X310. Each USRP’s host PC is powered by an AMD Ryzen 1950X processor and the Ubuntu 18.04 operating system.
* Follow [USRP setup tutorial](https://github.com/SeaBreezing/Cellular-X/blob/main/USRP%20setup%20tutorial.md) to prepare your own USRP device on each hostPC from scratch.
* Follow [SRSRAN 4G Installation Guide](https://docs.srsran.com/projects/4g/en/latest/general/source/1_installation.html#gen-installation) to prepare your SRSRAN environment.
* To check your environment, run `srsran`, `srsenb` on hostPC1 and `srsue` on hostPC2. You will see `Network attach successful` as output if your settings are correct.
* Take a third HostPC as a master control for the two hostPCs connecting USRP devices.
## Getting Stared


## Citation
If this repository is useful for your research, please cite:
```

```
