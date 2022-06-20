Required:
* python 3.9 or 3.10, python 3.10 preferred
* numpy: `pip install numpy`
* jsonpickle: `pip install jsonpickle`
* colorama: `pip install colorama`
* win32gui, but install this instead: `pip install pywin32`
* keyboard: `pip install keyboard`
* OpenAI Gym: `pip install gym`
* stable-baselines3: `pip install stable-baselines3[extra]`

For Ray tuning:
* `pip install ray torch torchvision`
* `pip install "ray[rllib]" tensorflow`
* `pip install wmi` -- this might be needed to enable a workaround to detect GPU in Windows -- DOES NOT WORK for me
* `pip install gputil` -- this might help with the GPU?