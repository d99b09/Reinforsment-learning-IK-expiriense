import numpy as np
import keras.backend.tensorflow_backend as backend
from keras.models import Sequential, Model, load_model
from keras.layers import Dense, Activation
from keras.optimizers import Adam
from keras.callbacks import TensorBoard
from keras import Input
import tensorflow as tf
from collections import deque
import time
import random
from tqdm import tqdm

from envernoment import *


DISCOUNT = 0.95
REPLAY_MEMORY_SIZE = 50_000  # How many last steps to keep for model training
MIN_REPLAY_MEMORY_SIZE = 500  # Minimum number of steps in a memory to start training
MINIBATCH_SIZE = 32  # How many steps (samples) to use for training
UPDATE_TARGET_EVERY = 5
MODEL_NAME = 'PXP_kin'
MIN_REWARD = 1 # For model save
MEMORY_FRACTION = 0.20

# Environment settings
EPISODES = 5_000

# Exploration settings
epsilon = 1# not a constant, going to be decayed
EPSILON_DECAY = 0.99
MIN_EPSILON = 0.1

#  Stats settings
AGGREGATE_STATS_EVERY = 25  # episodes
SHOW_PREVIEW = False
LOAD_MODEL = None

env = env([0, 0, 0, 0], [0.1, -0.2, 0.02])


# For stats
ep_rewards = [-200]

# Own Tensorboard class
class ModifiedTensorBoard(TensorBoard):

    # Overriding init to set initial step and writer (we want one log file for all .fit() calls)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.writer = tf.summary.FileWriter(self.log_dir)

    # Overriding this method to stop creating default log writer
    def set_model(self, model):
        pass

    # Overrided, saves logs with our step number
    # (otherwise every .fit() will start writing from 0th step)
    def on_epoch_end(self, epoch, logs=None):
        self.update_stats(**logs)

    # Overrided
    # We train for one batch only, no need to save anything at epoch end
    def on_batch_end(self, batch, logs=None):
        pass

    # Overrided, so won't close writer
    def on_train_end(self, _):
        pass

    # Custom method for saving own metrics
    # Creates writer, writes custom metrics and closes writer
    def update_stats(self, **stats):
        self._write_logs(stats, self.step)

# Agent class
class DQNAgent:
    def __init__(self):

        # Main model
        self.model = self.create_model()

        # Target network
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        # An array with last n steps for training
        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

        # Custom tensorboard object
        self.tensorboard = ModifiedTensorBoard(log_dir="logs/{}-{}".format(MODEL_NAME, int(time.time())))

        # Used to count when to update target network with main network's weights
        self.target_update_counter = 0

    def create_model(self):

        if LOAD_MODEL != None:
            model = load_model(LOAD_MODEL)
        else:
            model = Sequential()
            model.add(Dense(32, input_shape=env.OBSERVATION_SPACE_VALUES))
            model.add(Activation('relu'))
            model.add(Dense(32))
            model.add(Activation('relu'))
            model.add(Dense(32))
            model.add(Activation('relu'))
            model.add(Dense(12))
            model.add(Activation('linear'))


            model.compile(loss='mse', optimizer=Adam(lr=0.001), metrics=['accuracy'])

        return model

    # Adds step's data to a memory replay array
    # (observation space, action, reward, new observation space, done)
    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    # Trains main network every step during episode
    def train(self, terminal_state, step):

        # Start training only if certain number of samples is already saved
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)

        # Get current states from minibatch, then query NN model for Q values
        current_states = np.array([transition[0] for transition in minibatch])
        current_qs_list = self.model.predict(current_states)

        # Get future states from minibatch, then query NN model for Q values
        # When using target network, query it, otherwise main network should be queried
        new_current_states = np.array([transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(new_current_states)

        X = []
        y = []

        # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            # If not a terminal state, get new q from future states, otherwise set it to 0
            # almost like with Q Learning, but we use just part of equation here
            if not done:
                max_future_q = [np.max(future_qs_list[index][:3]), np.max(future_qs_list[index][3:6]),
                                np.max(future_qs_list[index][6:9]), np.max(future_qs_list[index][9:])]
                new_q = [reward + DISCOUNT * max_future_q[0], reward + DISCOUNT * max_future_q[1],
                         reward + DISCOUNT * max_future_q[2], reward + DISCOUNT * max_future_q[3]]
            else:
                new_q = [reward, reward, reward, reward]

            # Update Q value for given state
            current_qs = current_qs_list[index]

            current_qs_1 = current_qs[:3]
            current_qs_2 = current_qs[3:6]
            current_qs_3 = current_qs[6:9]
            current_qs_4 = current_qs[9:]

            current_qs_1[action[0]] = new_q[0]
            current_qs_2[action[1]] = new_q[1]
            current_qs_3[action[2]] = new_q[2]
            current_qs_4[action[3]] = new_q[3]

            current_qs = np.hstack((current_qs_1, current_qs_2, current_qs_3, current_qs_4))




            # And append to our training data
            X.append(current_state)
            y.append(current_qs)



        # Fit on all samples as one batch, log only on terminal state
        self.model.fit(np.array(X), np.array(y), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False,
                       callbacks=[self.tensorboard] if terminal_state else None)

        # Update target network counter every episode
        if terminal_state:
            self.target_update_counter += 1

        # If counter reaches set value, update target network with weights of main network
        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

    # Queries main network for Q values given current observation space (environment state)
    def get_qs_return(self, state):
        qs = self.model.predict(np.array([state]))[0]
        qs1 = qs[:3]
        qs2 = qs[3:6]
        qs3 = qs[6:9]
        qs4 = qs[9:]
        return [np.argmax(qs1), np.argmax(qs2), np.argmax(qs3), np.argmax(qs4)]


if __name__ == '__main__':
    agent = DQNAgent()

    # Iterate over episodes
    for episode in tqdm(range(1, EPISODES + 1), ascii=True, unit='episodes'):

        # Update tensorboard step every episode
        agent.tensorboard.step = episode

        # Restarting episode - reset episode reward and step number
        episode_reward = 0
        step = 1

        # Reset environment and get initial state
        current_state = env.reset()

        # Reset flag and start iterating until episode ends
        done = False
        while not done:

            # This part stays mostly the same, the change is to query a model for Q values
            if np.random.random() > epsilon:
                # Get action from Q table
                action = agent.get_qs_return(current_state)
                # print(action)
            else:
                # Get random action
                action = [np.random.randint(0, 3), np.random.randint(0, 3), np.random.randint(0, 3),
                          np.random.randint(0, 3)]

            new_state, reward, done = env.step(action)

            # Transform new continous state to new discrete state and count reward
            episode_reward += reward

            if SHOW_PREVIEW:  # and not episode % AGGREGATE_STATS_EVERY:
                env.render()

            # Every step we update replay memory and train main network
            agent.update_replay_memory((current_state, action, reward, new_state, done))
            agent.train(done, step)

            current_state = new_state
            step += 1

        # Append episode reward to a list and log stats (every given number of episodes)
        ep_rewards.append(episode_reward)
        if not episode % AGGREGATE_STATS_EVERY or episode == 1:
            average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:]) / len(ep_rewards[-AGGREGATE_STATS_EVERY:])
            min_reward = min(ep_rewards[-AGGREGATE_STATS_EVERY:])
            max_reward = max(ep_rewards[-AGGREGATE_STATS_EVERY:])
            agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward,
                                           epsilon=epsilon)
            ''''''
            # Save model, but only when min reward is greater or equal a set value
            if min_reward >= MIN_REWARD:
                agent.model.save(
                    f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

        # Decay epsilon
        if epsilon > MIN_EPSILON:
            epsilon *= EPSILON_DECAY
            epsilon = max(MIN_EPSILON, epsilon)