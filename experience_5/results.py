import numpy as np
from keras.models import load_model
from dqn_agent import *
from envernoment import *
import matplotlib.pyplot as plt

LOAD_MODEL = 'PXP_kin_____1.21max____1.21avg____1.20min__1569417073.model'

env = env([0, 0, 0, 0], [0.1, -0.2, 0.02])

class result_agent(DQNAgent):
    def __init__(self):
        super().__init__()
        self.x_list = []
        self.y_list = []
        self.z_list = []
        self.q1_list = []
        self.q2_list = []
        self.q3_list = []
        self.q4_list = []
        self.step_list = []


    def update_lists(self):
        x = env.end_coord_x
        y = env.end_coord_y
        z = env.end_coord_z
        q1 = env.q1
        q2 = env.q2
        q3 = env.q3
        q4 = env.q4
        step = env.num_steps
        self.x_list.append(x)
        self.y_list.append(y)
        self.z_list.append(z)
        self.q1_list.append(q1)
        self.q2_list.append(q2)
        self.q3_list.append(q3)
        self.q4_list.append(q4)
        self.step_list.append(step)

    def get_qs_return(self, state):
        self.update_lists()
        result = super().get_qs_return(state)
        return result

    def show_result(self):
        plt.plot(self.step_list, self.q1_list, label='q1')
        plt.plot(self.step_list, self.q2_list, label='q2')
        plt.plot(self.step_list, self.q3_list, label='q3')
        plt.plot(self.step_list, self.q4_list, label='q4')
        plt.xlabel('Step')
        plt.ylabel('joint valve')
        plt.legend()
        plt.show()




if __name__ == '__main__':
    agent = result_agent()

    state = env.reset()

    done = False
    while not done:
        episode_reward = 0
        step = 1
        action = agent.get_qs_return(state)
        state, reward, done = env.step(action)
        episode_reward += reward
    print(episode_reward)
    agent.show_result()