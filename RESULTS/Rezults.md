
PPO, with .2 learning rate and fixed seed (474806171) converged in a little over 2000 steps.
Policy it converged was "always, only recruit army"
Potential pitfalls at this time:
* penalty for invalid actions might be too small: -1 compared to thousands for recruiting army
* simplification or implementation problem masking invalid actions: when recruiting army, if the hero is in town it also transfers everything to the hero, and this marks the action of recruiting as being valid even if nothing was recruited
  * could be viewed as an exploitation, should be fixed in successive runs


PPO, same as above, still converges to "always only recruit army". Convergs at around 2130 steps.
Suspicion of too large values for rewards. Will try to use log of army strength gain instead.

DQN, .02 learning rate and fixed seed seemed promising:
* for a while it learned to only end turn
* then it started to only end turn and move the hero a bit (gain reward for exploring)
* then it started recruiting army, but too much causing invalid action penalties
* then it reverted to ending turn, moving the hero a bit, building something (promising)