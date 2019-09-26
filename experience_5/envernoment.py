import vrep
from coord_to_polar import *
import sys
import random as r
import math as m
from time import sleep
import numpy as np
from time import sleep

class env():
    OBSERVATION_SPACE_VALUES = (17,)
    ACTION_SPACE_SIZE = 12

    #action_space = None
    #observation_space = None

    def __init__(self, sours_q=[], target_position=[]):

        self.sours_q = sours_q
        self.target_position = target_position

        self.num_steps = 0

        self.d_q = m.radians(2)

        self.clientID = None
        self.handle_joint_1 = None
        self.handle_joint_2 = None
        self.handle_joint_3 = None
        self.handle_joint_4 = None
        self.handle_end_pincher = None
        self.handle_ball = None
        self.handle_end_tester = None
        self.q1 = 0
        self.q2 = 0
        self.q3 = 0
        self.q4 = 0
        self.ball_coord = None
        self.ball_coord_x = None
        self.ball_coord_y = None
        self.ball_coord_z = None
        self.end_coord = None
        self.end_coord_x = None
        self.end_coord_y = None
        self.end_coord_z = None
        self.obs = None
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
            if self.q2 > m.radians(135):
                self.q2 = m.radians(135)
        elif action[1] == 1:
            self.q2 -= self.d_q
            if self.q2 < -m.radians(135):
                self.q2 = -m.radians(135)

        if action[2] == 2:
            self.q3 += self.d_q
            if self.q3 > m.radians(135):
                self.q3 = m.radians(135)
        elif action[2] == 1:
            self.q3 -= self.d_q
            if self.q3 < -m.radians(135):
                self.q3 = -m.radians(135)

        if action[3] == 2:
            self.q4 += self.d_q
            if self.q4 > m.radians(135):
                self.q3 = m.radians(135)
        elif action[3] == 1:
            self.q4 -= self.d_q
            if self.q4 < 0:
                self.q4 = 0

        self.setJoint_PXP()
        self.get_end_coord()
        obs = self.get_obs()
        d_dist = start_dist - self.dist
        reward = d_dist / 2

        done = False

        self.num_steps += 1

        if self.dist < 0.05:
            reward += 1
            done = True
        elif self.num_steps > 100:
            done = True

        return obs, reward, done

    def reset(self):

        self.num_steps = 0

        self.set_randomJoint_PXP()

        self.create_random_ball()

        return self.get_obs()

    def configurate(self):
        print('Program started')

        vrep.simxFinish(-1)

        self.clientID = vrep.simxStart('127.0.0.1', 19999, True, True, 5000, 5)

        if self.clientID != -1:
            print("Connected to remote server")
        else:
            print('Connection not successful')
            sys.exit('Could not connect')
        errorCode, self.handle_joint_1 = vrep.simxGetObjectHandle(self.clientID,
                                                                  'PhantomXPincher_joint1',
                                                                  vrep.simx_opmode_oneshot_wait)
        errorCode, self.handle_joint_2 = vrep.simxGetObjectHandle(self.clientID,
                                                                  'PhantomXPincher_joint2',
                                                                  vrep.simx_opmode_oneshot_wait)
        errorCode, self.handle_joint_3 = vrep.simxGetObjectHandle(self.clientID,
                                                                  'PhantomXPincher_joint3',
                                                                  vrep.simx_opmode_oneshot_wait)
        errorCode, self.handle_joint_4 = vrep.simxGetObjectHandle(self.clientID,
                                                                  'PhantomXPincher_joint4',
                                                                  vrep.simx_opmode_oneshot_wait)

        errorCode, self.handle_end_pincher = vrep.simxGetObjectHandle(self.clientID,
                                                                      'PhantomXPincher_gripperCenter_joint',
                                                                      vrep.simx_opmode_oneshot_wait)
        errorCode, self.handle_ball = vrep.simxGetObjectHandle(self.clientID,
                                                               'Dummy',
                                                               vrep.simx_opmode_oneshot_wait)
        errorCode, self.handle_end_tester = vrep.simxGetObjectHandle(self.clientID,
                                                               'Dummy0',
                                                               vrep.simx_opmode_oneshot_wait)

        print('Configuration ended')

    def render(self):
        pass

    def close(self):

        print('close me')

    def setJoint_PXP(self):
        vrep.simxSetJointTargetPosition(self.clientID, self.handle_joint_1, self.q1, vrep.simx_opmode_oneshot_wait)
        vrep.simxSetJointTargetPosition(self.clientID, self.handle_joint_2, self.q2, vrep.simx_opmode_oneshot_wait)
        vrep.simxSetJointTargetPosition(self.clientID, self.handle_joint_3, self.q3, vrep.simx_opmode_oneshot_wait)
        vrep.simxSetJointTargetPosition(self.clientID, self.handle_joint_4, self.q4, vrep.simx_opmode_oneshot_wait)

    def set_randomJoint_PXP(self):
        if len(self.sours_q) == 0:
            self.q1 = m.radians(r.randrange(-180, 180, 2))
            self.q2 = m.radians(r.randrange(-90, 90, 2))
            self.q3 = m.radians(r.randrange(-90, 90, 2))
            self.q4 = m.radians(r.randrange(0, 90, 2))
        else:
            self.q1 = m.radians(self.sours_q[0])
            self.q2 = m.radians(self.sours_q[1])
            self.q3 = m.radians(self.sours_q[2])
            self.q4 = m.radians(self.sours_q[3])

        vrep.simxSetJointTargetPosition(self.clientID, self.handle_joint_1, self.q1, vrep.simx_opmode_oneshot_wait)
        vrep.simxSetJointTargetPosition(self.clientID, self.handle_joint_2, self.q2, vrep.simx_opmode_oneshot_wait)
        vrep.simxSetJointTargetPosition(self.clientID, self.handle_joint_3, self.q3, vrep.simx_opmode_oneshot_wait)
        vrep.simxSetJointTargetPosition(self.clientID, self.handle_joint_4, self.q4, vrep.simx_opmode_oneshot_wait)
        self.get_end_coord()

    def create_random_ball(self):
        if len(self.target_position) == 0:
            ro = r.uniform(0.1357, 0.31061)
            alf = r.uniform(0, 2 * m.pi)
            fi = r.uniform(0, 2 * m.pi)

            self.ball_coord_z = 1.2892e-01 + ro * m.sin(alf)

            while self.ball_coord_z < 0:
                ro = r.uniform(0.1357, 0.31061)
                alf = r.uniform(0, 2 * m.pi)
                fi = r.uniform(0, 2 * m.pi)
                self.ball_coord_z = 1.2892e-01 + ro * m.sin(alf)
            self.ball_coord_x = ro * m.cos(alf) * m.cos(fi)
            self.ball_coord_y = ro * m.cos(alf) * m.sin(fi)
        else:
            self.ball_coord_x = self.target_position[0]
            self.ball_coord_y = self.target_position[1]
            self.ball_coord_z = self.target_position[2]

        self.ball_coord = [self.ball_coord_x, self.ball_coord_y, self.ball_coord_z]

        vrep.simxSetObjectPosition(self.clientID, self.handle_ball, -1, self.ball_coord, vrep.simx_opmode_oneshot_wait)

    def get_end_coord(self):
        #sleep(0.15)
        errorCode, end_coord = vrep.simxGetObjectPosition(self.clientID, self.handle_end_pincher, -1,
                                                               vrep.simx_opmode_oneshot_wait)
        self.end_coord = list(end_coord)
        self.end_coord_x = self.end_coord[0]
        self.end_coord_y = self.end_coord[1]
        self.end_coord_z = self.end_coord[2]
        vrep.simxSetObjectPosition(self.clientID, self.handle_end_tester, -1, self.end_coord,
                                   vrep.simx_opmode_oneshot_wait)


    def distance(self):

        x1 = self.end_coord_x
        y1 = self.end_coord_y
        z1 = self.end_coord_z
        x2 = self.ball_coord_x
        y2 = self.ball_coord_y
        z2 = self.ball_coord_z

        self.dist = m.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)

    def get_obs(self):
        self.distance()

        ro1, fi1, teta1 = coord_to_polar(self.end_coord_x, self.end_coord_y, self.end_coord_z)
        ro2, fi2, teta2 = coord_to_polar(self.ball_coord_x, self.ball_coord_y, self.ball_coord_z)

        result = np.array(
            [self.dist,
             (self.q1 + m.pi) / (2 * m.pi), (self.q2 + m.radians(135)) / m.radians(270),
             (self.q3 + m.radians(135)) / m.radians(270), 2 * self.q4 / m.radians(135),
             (self.end_coord_x + 0.35) / 0.7, (self.end_coord_y + 0.35) / 0.7, self.end_coord_z / 0.45,
             ro1 / 0.45, fi1 / (2*m.pi), 2 * teta1 / m.pi,
             (self.ball_coord_x + 0.35) / 0.7, (self.ball_coord_y + 0.35) / 0.7, self.ball_coord_z / 0.45,
             ro2 / 0.45, fi2 / (2 * m.pi), 2 * teta2 / m.pi])

        return result

if __name__ == '__main__':
    env = env([0, 0, 0, 0], [0.1, -0.2, 0.02])
    env.configurate()
    print(env.reset())

    while 1:
        act = input().split()
        for i in (0, 1, 2, 3):
            act[i] = int(act[i])

        print(act)

        obs, reward, done = env.step(act)
        print(obs)

        print(reward)

        if done:
            env.reset()


