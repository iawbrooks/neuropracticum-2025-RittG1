
# Template for making a pose estimating Hailo Raspi App

Modified from the [Hailo Raspberry Pi examples repo](https://github.com/hailo-ai/hailo-rpi5-examples/) by removing extra content and installers, focussing on just the core steps needed to get a working python pipeline.

See also:
- [Hailo Official Website](https://hailo.ai/)
- [Hailo Community Forum](https://community.hailo.ai/)

## Installation

```shell
source install.sh
```
The install script is simplified from [Hailo Raspberry Pi 5 installation guide](doc/install-raspberry-pi5.md#how-to-set-up-raspberry-pi-5-and-hailo), and eliminates the example downloads. However, one must still compile XXX.

### Usage

If not already done, activate the environment:
```shell
source setup_env.sh
```
then
```shell
python pose_estimation.py --input /dev/video8
```

Change the device to any applicable camera.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

All code provided on an “AS IS” basis and “with all faults.” No responsibility or liability is accepted or shall be imposed upon provider regarding the accuracy, merchantability, completeness, or suitability of the code example. Use at your own risk. No liability or responsibility for errors or omissions in, or any business decisions made by you in reliance on this code or any part of it, is expressed or implied.
