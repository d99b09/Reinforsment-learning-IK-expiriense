from tkinter import *
import math as m
import random as r
import numpy as np
from time import sleep
import itertools


def coord_to_polar2D(x, y):
    ro = m.sqrt(x ** 2 + y ** 2)
    c = x / ro
    s = y / ro
    if c > 0 and s > 0:
        fi = m.acos(c)

    elif c > 0 and s < 0:
        fi = 2 * m.pi + m.asin(s)

    elif c < 0 and s > 0:
        fi = m.acos(c)

    elif c < 0 and s < 0:
        fi = m.pi - m.asin(s)

    elif c == 0 and s == 1:
        fi = m.pi / 2

    elif c == 0 and s == -1:
        fi = m.pi * 1.5

    elif c == 1 and s == 0:
        fi = 0
    elif c == -1 and s == 0:
        fi = m.pi

    return ro, fi


class env():
    OBSERVATION_SPACE_VALUES = (11,)
    ACTION_SPACE_SIZE = 9

    action_space = None
    observation_space = None

    def __init__(self):

        self.score = 0
        self.num_steps = 0
        self.size_x = 1000
        self.size_y = 650
        self.zero_x = self.size_x / 2
        self.zero_y = self.size_y / 2
        self.a1 = 200
        self.a2 = 100
        self.d_q = m.radians(2)

        self.ball = None
        self.ball_coord_x = None
        self.ball_coord_y = None
        self.ball_coord_text = None

        self.end_ball = None
        self.end_x = None
        self.end_y = None
        self.end_ball_text = None

        self.path = None
        self.path_coord = []

        self.line_1 = None
        self.line_2 = None

        self.root = None
        self.canvas = None

        self.q1 = 0
        self.q2 = 0

        self.dist = None

        self.configurate()




    def step(self, action):

        self.distance()
        start_dist = self.dist
        if action[0] == 2:
            self.q1 += self.d_q
            if self.q1 > m.pi:
                self.q1 = m.pi
        elif action[0] == 1:
            self.q1 -= self.d_q
            if self.q1 < -m.pi:
                self.q1 = -m.pi

        if action[1] == 2:
            self.q2 += self.d_q
            if self.q2 > m.pi/2:
                self.q2 = m.pi/2
        elif action[1] == 1:
            self.q2 -= self.d_q
            if self.q2 < -m.pi/2:
                self.q2 = m.pi/2

        obs = self.get_obs()
        self.distance()

        reward = start_dist - self.dist

        done = False

        self.num_steps += 1

        if self.dist < 10:
            reward += 1000
            done = True

        elif self.num_steps > 250:
            done = True

        self.root.update()

        return obs, reward, done

    def reset(self):

        self.num_steps = 0
        self.create_random_ball()
        self.create_random_q()

        return self.get_obs()

    def configurate(self):
        print('Program started')
        self.root = Tk()
        self.canvas = Canvas(self.root, width=self.size_x, height=self.size_y, bg="white")
        self.canvas.pack()
        self.canvas.create_line(0, self.zero_y, self.size_x, self.zero_y, arrow=LAST)
        self.canvas.create_line(self.zero_x, self.size_y, self.zero_x, 0, arrow=LAST)

    def render(self):
        sleep(0.03)

        self.canvas.delete(self.ball)
        self.canvas.delete(self.ball_coord_text)
        self.canvas.delete(self.end_ball)
        self.canvas.delete(self.end_ball_text)
        self.canvas.delete(self.line_1)
        self.canvas.delete(self.line_2)

        self.ball = self.canvas.create_oval(self.ball_coord_x - 10,
                                            self.ball_coord_y - 10,
                                            self.ball_coord_x + 10,
                                            self.ball_coord_y + 10,
                                            fill='red')
        self.ball_coord_text = self.canvas.create_text(self.ball_coord_x + 15,
                                                       self.ball_coord_y + 15,
                                                       text='{:.0f}'.format(self.ball_coord_x - self.zero_x) + ',' +
                                                            '{:.0f}'.format(self.zero_y - self.ball_coord_y))

        self.line_1 = self.canvas.create_line(self.zero_x, self.zero_y,
                                              self.zero_x + self.a1 * m.cos(-self.q1),
                                              self.zero_y + self.a1 * m.sin(-self.q1), width=5, fill='green')

        self.line_2 = self.canvas.create_line(self.zero_x + self.a1 * m.cos(-self.q1),
                                              self.zero_y + self.a1 * m.sin(-self.q1),
                                              self.zero_x + self.a1 * m.cos(-self.q1) + self.a2 * m.cos(
                                                  -(self.q1 + self.q2)),
                                              self.zero_y + self.a1 * m.sin(-self.q1) + self.a2 * m.sin(
                                                  -(self.q1 + self.q2)),
                                              width=5, fill='green')

        self.end_ball = self.canvas.create_oval(self.end_x - 5,
                                                self.end_y - 5,
                                                self.end_x + 5,
                                                self.end_y + 5,
                                                fill='green')

        self.end_ball_text = self.canvas.create_text(self.end_x + 15,
                                                       self.end_y + 15,
                                                       text='{:.0f}'.format(self.end_x - self.zero_x) + ',' +
                                                            '{:.0f}'.format(self.zero_y - self.end_y))
        self.root.update()

    def close(self):
        print('close me')
        self.root.mainloop()

    def create_random_ball(self):
        q1 = m.radians(r.uniform(-180, 180))
        q2 = m.radians(r.uniform(-90, 90))
        self.ball_coord_x = self.zero_x + self.a1 * m.cos(-q1) + self.a2 * m.cos(-q1 - q2)
        self.ball_coord_y = self.zero_y + self.a1 * m.sin(-q1) + self.a2 * m.sin(-q1 - q2)

    def create_random_q(self):

        self.q1 = r.uniform(-m.pi, m.pi)
        self.q2 = r.uniform(-m.pi/2, m.pi/2)

    def distance(self):
        self.dist = m.sqrt((self.ball_coord_x - self.end_x) ** 2 + (self.ball_coord_y - self.end_y) ** 2)

    def get_obs(self):

        self.end_x = self.zero_x + self.a1 * m.cos(-self.q1) + self.a2 * m.cos(-(self.q1 + self.q2))
        self.end_y = self.zero_y + self.a1 * m.sin(-self.q1) + self.a2 * m.sin(-(self.q1 + self.q2))

        self.distance()

        ro1, alf1 = coord_to_polar2D((self.end_x - self.zero_x), -(self.end_y - self.zero_y))
        ro2, alf2 = coord_to_polar2D((self.ball_coord_x - self.zero_x), -(self.ball_coord_y - self.zero_y))

        result = np.array(
            [self.dist / 600,
             (self.q1 + m.pi) / (2 * m.pi), (self.q2 + m.pi / 2) / m.pi, ((self.end_x - self.zero_x) + 300) / 600,
             (300 - (self.end_y - self.zero_y)) / 600, ro1 / 300, alf1 / 2 * m.pi,
             ((self.ball_coord_x - self.zero_x) + 300) / 600, (300 - (self.ball_coord_y - self.zero_y)) / 600,
             ro2 / 300, alf2 / m.pi])

        return result


''''''

if __name__ == "__main__":
    env = env()

    env.reset()
    env.render()
    ep_rw = 0
    while 1:
        act = input().split()
        for i in (0, 1):
            act[i] = int(act[i])


        obs, reward, done = env.step(act)
        print(obs)
        #obs, reward, done = env.step(r.randint(0, 8))
        # print(reward)
        env.render()

        ep_rw += reward
        if done:
            print(ep_rw)
            ep_rw = 0
            env.reset()
            env.render()

    env.close()



