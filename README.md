Environment inspired by **Heroes of Might and Magic III**.
Renderer is tested in Windows console, but should work on Linux as well.

# Example
A played game versus a dummy player 2 by a poorly trained model. Done with script `test_model.py`
![DQN trained for 100 000 steps](./examples/HOMMTextAnimation%202022-06-27%2022.53.46.gif)

# Requirements

## General requirements

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

# Reward

The reward function is kept relatively low in values, mostly reduced using logarithm. The reward is based on a few simple rules:
* `+1000` for win, but only when defeating all enemies by taking all their towns and defeating all their heroes
* `-1000` for loss, but only by losing all towns and heroes
* Difference in total army strength before and after an action, taken as a logarithm
* `0.1` for every tile explored
* Difference in total equivalent resources divided by 10, taken as a logarithm
* `2` for every hero level gained
* `-2` for every **invalid** action, e.g. moving a hero into a wall
* `-10` for every **unacceptable** action, e.g. when a hero has leveled up doing anything other than choosing the skill to level up

# Limitations

## Detailed environment limitations
* Currently works only with automatic battles, a.k.a. auto-combat
* Only 1 faction out of 10 is implemented, namely Castle
* Building requirements are currently removed
* Only 21 spells out of 73 are currently implemented, all of them are combat spells

## Gym environment limitations
* Renderer displays the state of the detailed game, there is currently no way to only render the observation presented to the RL model
* The most complete observation and action mapper pair is very unoptimal, has almost 400 000 discrete inputs
* Currently limited to at most 1 hero, 8 neutral armies, 4 total towns
* Currently limited to only 2 players
* Only tested with 1 model yet


# Implementation details
There is a detailed enviroment that has the "complete" capabilities, and actions set.

This detailed environment includes battles, but they only work as auto-combat using a very simple procedural AI.

## Detailed environment


[1]: [Environment architecture](https://drive.google.com/file/d/1858e7LHRXBo5cOBhIVx9gKQdIzGW49DG/view)

[2]: [Detailed environment class diabram](https://drive.google.com/file/d/1ltE9sgVXWXbtds0qoD0A--rqmbHA-zBA/view?usp=sharing)

[3]: [Gym environment class diagram](https://drive.google.com/file/d/11vOTt2CSG8C8B-b4XSZKUGTW8aH6p6p-/view?usp=sharing)