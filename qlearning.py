import gym
import numpy as np

env = gym.make("MountainCar-v0")
env.reset()

LEARNING_RATE = 0.1
DISCOUNT      = 0.95
EPISODES      = 50000
#SHOW_EVERY    = 2000

step=[]
prevavg=0
count=0
trained=False
first=1

DISCRETE_OS_SIZE = [20] * len(env.observation_space.high)
discrete_os_win_size= (env.observation_space.high - env.observation_space.low)/DISCRETE_OS_SIZE

epsilon = 0
START_EPSILON_DECAYING = 1
END_EPSILON_DECAYING = EPISODES//2
epsilon_decay_value  = epsilon /(END_EPSILON_DECAYING - START_EPSILON_DECAYING)

q_table = np.random.uniform(low=-2,high=0,size=(DISCRETE_OS_SIZE + [env.action_space.n]))

def get_discrete_state(state):
    discrete_state = (state - env.observation_space.low) / discrete_os_win_size
    return tuple(discrete_state.astype(np.int))

for  episode in range(EPISODES):
    if episode < 2000:
        SHOW_EVERY=100
    elif 2000 <= episode <= 5000:
        SHOW_EVERY=500
    else:
        SHOW_EVERY=2000

    if episode % SHOW_EVERY == 0:
        render = True
        print(f"At episode {episode}:")
        if len(step)>SHOW_EVERY/2:
            if trained:
                print("I'm trained!!! - trying to optimize...")
                trained=0
            elif not trained and first:
                print("We didn't make it yet :(")
            avgstep=sum(step)//len(step)
            if abs(prevavg-avgstep)<=1:
                count+=1
            else:
                count=0
            if count == 3:
                print("Seemed like this is the fastest I can do!!!")
                break
            print(f"Average step={avgstep}")
            step=[]
            prevavg=avgstep

    else:
        render = False
    discrete_state = get_discrete_state(env.reset()) # env.reset() returns intial state

    i=0
    done = False
    while not done:
        i+=1
        if np.random.random() > epsilon:
            action = np.argmax(q_table[discrete_state])
        else:
            action = np.random.randint(0,env.action_space.n)
        new_state, reward, done, _ = env.step(action)
        new_discrete_state = get_discrete_state(new_state)
        if render:
            env.render()
        if not done:
            max_future_q = np.max(q_table[new_discrete_state])
            current_q = q_table[discrete_state + (action, )]
            new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
            q_table[discrete_state+(action, )] = new_q
        elif new_state[0] >= env.goal_position:
            if first:
                trained=True
                first=0
            step.append(i)
            q_table[discrete_state + (action, )] = 0
        discrete_state=new_discrete_state

    if END_EPSILON_DECAYING >= episode >= START_EPSILON_DECAYING:
        epsilon -= epsilon_decay_value

input("Done! Press anywhere to close.")

env.close()
