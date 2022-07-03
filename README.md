Environment inspired by Heroes of Might and Magic III.
Renderer is tested in Windows console, but should work on Linux as well.

# Requirements

## Required
* python 3.9 or 3.10, python 3.10 preferred
  * For hyperparameter tuning with Ray python 3.9 is required 
* numpy: `pip install numpy`
* jsonpickle: `pip install jsonpickle`
* colorama: `pip install colorama`
* win32gui, but install this instead: `pip install pywin32`
* keyboard: `pip install keyboard`
* OpenAI Gym: `pip install gym`
* stable-baselines3: `pip install stable-baselines3[extra]`

## For Ray tuning
* only python 3.9 is currently supported by Ray
* `pip install ray torch torchvision`
* `pip install "ray[rllib]" tensorflow`

# Example
A played game versus a dummy player 2 by a poorly trained model. Done with script `test_model.py`
![DQN trained for 100 000 steps](./examples/HOMMTextAnimation%202022-06-27%2022.53.46.gif)

# Implementation details

## Detailed environment architecture
<iframe src="https://drive.google.com/file/d/1858e7LHRXBo5cOBhIVx9gKQdIzGW49DG/preview" width="640" height="480" allow="autoplay"></iframe>
