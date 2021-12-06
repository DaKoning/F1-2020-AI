import time
start_time = time.time()
import numpy as np

class Q_learning:

        def __init__(self, game):
            
            self.game = game
            
            """
            alpha is the learning rate, which determines how much newly acquired information overrides old information.
            gamma is the discount factor, the weight of future rewards, which determines the importance of the future rewards. The discount factor may be approximated by an artifical neural network, to optimize the ai.
            epsilon is randomness factor, which determines many time a random action should be taken, in state of a calculated one. This is called "exploring".
            Q_0 is the initial condition, which can be set by the first reward (reset of initial conditions). 
            """
            self.alpha = 0.1
            self.gamma = 0.6
            self.epsilon = 0.1

            self.stateSize = 100
            self.actionSize = 100
            Q_table = np.zeros((self.stateSize, self.actionSize))

            episodes = 0
            total_episodes = 100
            reward = 0
            done = False
            
            state = 0
            action = 0
            future_state = 0

            while not done:
                if np.random.uniform(0, 1) < self.epsilon:
                    #action = randomAction()
                    pass
                else:
                    #action = calculatedAction()
                    pass
                
                Q_old = Q_table[state, action]
                Q_max_future = np.max(Q_table[future_state])

                Q_new = Q_old + self.alpha * (reward + self.gamma * Q_max_future - Q_old)
                Q_table[state, action] = Q_new

                print(Q_table[0])

                episodes += 1

                if episodes == total_episodes:
                    done = True
                    print(str(total_episodes) + " episodes finished.")



if __name__ == "__main__":
    Q_learning(0)
    print("--- %s seconds ---" % (time.time() - start_time))