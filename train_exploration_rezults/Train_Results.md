# General notes
Training is done playing against a procedural AI. The procedural AI is inspired by this description: https://heroes.thelazy.net/index.php/Difficulty_level
Note: the procedural AI does not have any rules to build its towns, so it is weaker than the one described above.

The reward is simply the difference in army strength between the two players.
Winning the game gives an additional reward of 100 000, while losing the game gives a reward of -100 000.
Invalid actions are penalized with a reward of -1.
A typical starting army has an equivalent reward of approx 2000.

To avoid endless turns there are 2 limitations implemented:
1. maximum number of attempted actions per turn, after which ActionEndTurn is forced (done automatically by the env)
2. small penalty for invalid actions

Examples of invalid actions:
* level up hero when no hero is leveling up
* any action other than level up hero when a hero is leveling up
* recruiting hero or army from a town that the player does not own
* transfering army that does not exist
* moving a hero the player does not own
* moving a hero to an invalid destination, e.g. inside or through a wall

# DQN

## Dict observation space, 8k+ action space
With:
* allowed_actions_per_turn=100 - maximum number of attempted actions per turn (including invalid ones)
* 20 000 total_timesteps
* DQN params:
  * gamma: 0.99
  * tau: 1.0 (hard update)
  * train_freq=(100, 'step')
Result:
* evaluated on 5 episodes in  128.45s, mean_reward=-680.0, std_reward=263.8
* playing a game (at most 1000 steps):
`after 999 steps played in  35.66s: game.ended=True, day=1:2:4
         total-actions=1124, P1-total-actions=1010
         num-invalid-actions=1000,
         num-valid-actions-not-forced=0,
         won=False, defeated=False, end-AIVal=2452`
* conclusion: agent does not learn anything

With:
* allowed_actions_per_turn=100 - maximum number of attempted actions per turn (including invalid ones)
* 100 000 total_timesteps
* DQN params:
  * gamma: 0.99
  * tau: 1.0 (hard update)
  * train_freq=(100, 'step')
Result:
* training done in  2680.87s
* evaluated on 5 episodes in  169.41s, mean_reward=-880.0, std_reward=240.0
* playing a game (at most 1500 steps)
`after 499 steps played in  17.52s: game.ended=True, day=1:1:5
         total-actions=603, P1-total-actions=517
         num-invalid-actions=500,
         num-valid-actions-not-forced=0
         won=False, defeated=True, end-AIVal=0`

With:
* same as above, except train_freq=(50, 'step')
Result:
* train episodes: 108+
* training done in  2855.23s
* evaluated on 5 episodes in  165.40s, mean_reward=-940.0, std_reward=120.0
* playing a game (at most 1500 steps)
`after 999 steps played in  35.56s: game.ended=True, day=1:2:4
         total-actions=1143, P1-total-actions=1025
         num-invalid-actions=1000,
         num-valid-actions-not-forced=0
         won=False, defeated=False, end-AIVal=0`

With:
* same as above, except:
  * allowed_actions_per_turn=200
  * train_freq=(100, 'step')
Result:
* train episodes: 52+
* training done in  2514.67s.
* evaluated on 5 episodes in  242.68s, mean_reward=-1400.0, std_reward=551.3619500836089
* playing a game (at most 1500 steps)
`after 1499 steps played in  52.57s: game.ended=False, day=1:2:1
         total-actions=1599, P1-total-actions=1507
         num-invalid-actions=1500,
         num-valid-actions-not-forced=0
         won=False, defeated=False, end-AIVal=2338`

With:
* allowed_actions_per_turn=900 - maximum number of attempted actions per turn (including invalid ones)
* 110 000 total_timesteps
* DQN params:
  * gamma: 0.99
  * tau: 1.0 (hard update)
  * train_freq=(450, 'step')
Result:
* train episodes: 12+
* training done in  2709.98s
* evaluated on 5 episodes in  1422.15s, mean_reward=-8100.0, std_reward=1800.0
* playing a game (at most 9000 steps)
`after 1799 steps played in  60.44s: game.ended=True, day=1:1:2
         total-actions=1874, P1-total-actions=1817
         num-invalid-actions=1800,
         num-valid-actions-not-forced=0
         won=False, defeated=True, end-AIVal=0`

With:
* allowed_actions_per_turn=500 - maximum number of attempted actions per turn (including invalid ones)
* 110 000 total_timesteps
* DQN params:
  * gamma: 0.99
  * tau: 1.0 (hard update)
  * train_freq=(250, 'step')
Result:
* train episodes: 24+
* training done in  2971.55s
* evaluated on 3 episodes in  280.05s, mean_reward=-2500.0, std_reward=408.248290463863
* playing a game (at most 5000 steps)
`after 4999 steps played in  198.91s: game.ended=True, day=1:2:4
         total-actions=5136, P1-total-actions=5010
         num-invalid-actions=5000,
         num-valid-actions-not-forced=0
         won=False, defeated=False, end-AIVal=2006`

With:
* allowed_actions_per_turn=400
* 220 000 total_timesteps
* DQN params:
  * gamma: 0.99
  * tau: 1.0 (hard update)
  * train_freq=(400, 'step')
Result:
* train episodes: 64+
* training done in  6606.76s
* evaluated on 1 episodes in  55.23s, mean_reward=-1600.0, std_reward=0.0
* playing a game (at most 4000 steps)
`after 2399 steps played in  82.93s: game.ended=True, day=1:1:6
         total-actions=2577, P1-total-actions=2438
         num-invalid-actions=2400,
         num-valid-actions-not-forced=0
         won=False, defeated=True, end-AIVal=0`


for this one no eval, sadly :'(

Using cpu device
Wrapping the env with a `Monitor` wrapper
Wrapping the env in a DummyVecEnv.
<class 'stable_baselines3.dqn.dqn.DQN'> training total_timesteps=100000...
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 1.2e+03   |
|    ep_rew_mean      | -6.27e+03 |
|    exploration_rate | 0.909     |
| time/               |           |
|    episodes         | 4         |
|    fps              | 142       |
|    time_elapsed     | 33        |
|    total_timesteps  | 4810      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 938       |
|    ep_rew_mean      | -4.78e+03 |
|    exploration_rate | 0.857     |
| time/               |           |
|    episodes         | 8         |
|    fps              | 146       |
|    time_elapsed     | 51        |
|    total_timesteps  | 7502      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 839       |
|    ep_rew_mean      | -6.78e+04 |
|    exploration_rate | 0.809     |
| time/               |           |
|    episodes         | 12        |
|    fps              | 136       |
|    time_elapsed     | 73        |
|    total_timesteps  | 10070     |
-----------------------------------
----------------------------------
| rollout/            |          |
|    ep_len_mean      | 755      |
|    ep_rew_mean      | -6e+04   |
|    exploration_rate | 0.77     |
| time/               |          |
|    episodes         | 16       |
|    fps              | 139      |
|    time_elapsed     | 86       |
|    total_timesteps  | 12087    |
----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 691       |
|    ep_rew_mean      | -4.92e+04 |
|    exploration_rate | 0.738     |
| time/               |           |
|    episodes         | 20        |
|    fps              | 138       |
|    time_elapsed     | 99        |
|    total_timesteps  | 13811     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 633       |
|    ep_rew_mean      | -4.15e+04 |
|    exploration_rate | 0.711     |
| time/               |           |
|    episodes         | 24        |
|    fps              | 138       |
|    time_elapsed     | 109       |
|    total_timesteps  | 15202     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 590       |
|    ep_rew_mean      | -3.62e+04 |
|    exploration_rate | 0.686     |
| time/               |           |
|    episodes         | 28        |
|    fps              | 138       |
|    time_elapsed     | 119       |
|    total_timesteps  | 16517     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 619       |
|    ep_rew_mean      | -3.91e+05 |
|    exploration_rate | 0.624     |
| time/               |           |
|    episodes         | 32        |
|    fps              | 138       |
|    time_elapsed     | 142       |
|    total_timesteps  | 19810     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 597       |
|    ep_rew_mean      | -3.49e+05 |
|    exploration_rate | 0.592     |
| time/               |           |
|    episodes         | 36        |
|    fps              | 138       |
|    time_elapsed     | 155       |
|    total_timesteps  | 21491     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 580       |
|    ep_rew_mean      | -3.17e+05 |
|    exploration_rate | 0.559     |
| time/               |           |
|    episodes         | 40        |
|    fps              | 137       |
|    time_elapsed     | 168       |
|    total_timesteps  | 23217     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 561       |
|    ep_rew_mean      | -2.89e+05 |
|    exploration_rate | 0.531     |
| time/               |           |
|    episodes         | 44        |
|    fps              | 135       |
|    time_elapsed     | 181       |
|    total_timesteps  | 24672     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 560       |
|    ep_rew_mean      | -2.89e+05 |
|    exploration_rate | 0.489     |
| time/               |           |
|    episodes         | 48        |
|    fps              | 134       |
|    time_elapsed     | 200       |
|    total_timesteps  | 26904     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 555       |
|    ep_rew_mean      | -2.74e+05 |
|    exploration_rate | 0.451     |
| time/               |           |
|    episodes         | 52        |
|    fps              | 134       |
|    time_elapsed     | 215       |
|    total_timesteps  | 28881     |
-----------------------------------
----------------------------------
| rollout/            |          |
|    ep_len_mean      | 568      |
|    ep_rew_mean      | -2.7e+05 |
|    exploration_rate | 0.396    |
| time/               |          |
|    episodes         | 56       |
|    fps              | 135      |
|    time_elapsed     | 234      |
|    total_timesteps  | 31801    |
----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 553       |
|    ep_rew_mean      | -2.53e+05 |
|    exploration_rate | 0.369     |
| time/               |           |
|    episodes         | 60        |
|    fps              | 135       |
|    time_elapsed     | 245       |
|    total_timesteps  | 33186     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 555       |
|    ep_rew_mean      | -2.55e+05 |
|    exploration_rate | 0.326     |
| time/               |           |
|    episodes         | 64        |
|    fps              | 135       |
|    time_elapsed     | 262       |
|    total_timesteps  | 35499     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 586       |
|    ep_rew_mean      | -2.42e+05 |
|    exploration_rate | 0.243     |
| time/               |           |
|    episodes         | 68        |
|    fps              | 138       |
|    time_elapsed     | 288       |
|    total_timesteps  | 39868     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 582       |
|    ep_rew_mean      | -2.28e+05 |
|    exploration_rate | 0.204     |
| time/               |           |
|    episodes         | 72        |
|    fps              | 137       |
|    time_elapsed     | 304       |
|    total_timesteps  | 41898     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 570       |
|    ep_rew_mean      | -2.17e+05 |
|    exploration_rate | 0.177     |
| time/               |           |
|    episodes         | 76        |
|    fps              | 136       |
|    time_elapsed     | 318       |
|    total_timesteps  | 43334     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 562       |
|    ep_rew_mean      | -2.06e+05 |
|    exploration_rate | 0.145     |
| time/               |           |
|    episodes         | 80        |
|    fps              | 135       |
|    time_elapsed     | 331       |
|    total_timesteps  | 44988     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 552       |
|    ep_rew_mean      | -1.96e+05 |
|    exploration_rate | 0.118     |
| time/               |           |
|    episodes         | 84        |
|    fps              | 135       |
|    time_elapsed     | 341       |
|    total_timesteps  | 46403     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 562       |
|    ep_rew_mean      | -1.89e+05 |
|    exploration_rate | 0.0602    |
| time/               |           |
|    episodes         | 88        |
|    fps              | 137       |
|    time_elapsed     | 360       |
|    total_timesteps  | 49464     |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 565       |
|    ep_rew_mean      | -1.81e+05 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 92        |
|    fps              | 71        |
|    time_elapsed     | 725       |
|    total_timesteps  | 52018     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 299       |
|    n_updates        | 504       |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 551       |
|    ep_rew_mean      | -1.74e+05 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 96        |
|    fps              | 60        |
|    time_elapsed     | 879       |
|    total_timesteps  | 52858     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 644       |
|    n_updates        | 714       |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 529       |
|    ep_rew_mean      | -1.71e+05 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 100       |
|    fps              | 59        |
|    time_elapsed     | 887       |
|    total_timesteps  | 52887     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 19.5      |
|    n_updates        | 721       |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 492       |
|    ep_rew_mean      | -1.73e+05 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 104       |
|    fps              | 49        |
|    time_elapsed     | 1093      |
|    total_timesteps  | 54036     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 132       |
|    n_updates        | 1008      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 466       |
|    ep_rew_mean      | -1.74e+05 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 108       |
|    fps              | 48        |
|    time_elapsed     | 1116      |
|    total_timesteps  | 54148     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 327       |
|    n_updates        | 1036      |
-----------------------------------
----------------------------------
| rollout/            |          |
|    ep_len_mean      | 441      |
|    ep_rew_mean      | -1.7e+05 |
|    exploration_rate | 0.05     |
| time/               |          |
|    episodes         | 112      |
|    fps              | 48       |
|    time_elapsed     | 1123     |
|    total_timesteps  | 54172    |
| train/              |          |
|    learning_rate    | 0.01     |
|    loss             | 177      |
|    n_updates        | 1042     |
----------------------------------
----------------------------------
| rollout/            |          |
|    ep_len_mean      | 426      |
|    ep_rew_mean      | -1.7e+05 |
|    exploration_rate | 0.05     |
| time/               |          |
|    episodes         | 116      |
|    fps              | 44       |
|    time_elapsed     | 1222     |
|    total_timesteps  | 54702    |
| train/              |          |
|    learning_rate    | 0.01     |
|    loss             | 24.3     |
|    n_updates        | 1175     |
----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 419       |
|    ep_rew_mean      | -1.73e+05 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 120       |
|    fps              | 39        |
|    time_elapsed     | 1412      |
|    total_timesteps  | 55752     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 310       |
|    n_updates        | 1437      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 419       |
|    ep_rew_mean      | -1.74e+05 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 124       |
|    fps              | 34        |
|    time_elapsed     | 1656      |
|    total_timesteps  | 57102     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 86.6      |
|    n_updates        | 1775      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 423       |
|    ep_rew_mean      | -1.75e+05 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 128       |
|    fps              | 29        |
|    time_elapsed     | 1967      |
|    total_timesteps  | 58830     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 19.8      |
|    n_updates        | 2207      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 645       |
|    ep_rew_mean      | -1.82e+07 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 132       |
|    fps              | 12        |
|    time_elapsed     | 6653      |
|    total_timesteps  | 84315     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 5.79e+04  |
|    n_updates        | 8578      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 641       |
|    ep_rew_mean      | -1.82e+07 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 136       |
|    fps              | 12        |
|    time_elapsed     | 6893      |
|    total_timesteps  | 85615     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 4.31e+04  |
|    n_updates        | 8903      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 639       |
|    ep_rew_mean      | -1.82e+07 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 140       |
|    fps              | 12        |
|    time_elapsed     | 7168      |
|    total_timesteps  | 87116     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 3.58e+04  |
|    n_updates        | 9278      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 642       |
|    ep_rew_mean      | -1.82e+07 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 144       |
|    fps              | 11        |
|    time_elapsed     | 7485      |
|    total_timesteps  | 88866     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 2.4e+04   |
|    n_updates        | 9716      |
-----------------------------------
-----------------------------------
| rollout/            |           |
|    ep_len_mean      | 727       |
|    ep_rew_mean      | -1.82e+07 |
|    exploration_rate | 0.05      |
| time/               |           |
|    episodes         | 148       |
|    fps              | 10        |
|    time_elapsed     | 9395      |
|    total_timesteps  | 99599     |
| train/              |           |
|    learning_rate    | 0.01      |
|    loss             | 3.61e+04  |
|    n_updates        | 12399     |
-----------------------------------
training done in  9467.98s.

