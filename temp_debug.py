from HOMMGymEnv import HOMMGymEnv
import the_env

env:HOMMGymEnv = the_env.env_creator({})

attempts = 100_000
while attempts > 0:
    attempts -= 1
    env.reset()
