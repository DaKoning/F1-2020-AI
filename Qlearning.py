import numpy as np
import random
from os.path import exists
import tkinter as tk

delete_progress = False

if delete_progress or not exists("Qtable.npy"):
    # Q_table = 'speed', 'ray_front', 'ray_rightfront', 'ray_leftfront', 'steering', 'Q'
    print("Q-learning: Creating Q-table")
    Q_table = np.array([[0, 0, 0, 0, 0]], dtype=object)
    np.save("Qtable", Q_table)
else:
    print("Q-learning: Loading Q-table")
    Q_table = np.load("Qtable.npy", allow_pickle=True)

if delete_progress or not exists("epsilon"):
    print("Q-learning: Creating epsilon")
    epsilon = 0.5
    file = open("epsilon", "w")
    file.write(str(epsilon))
    file.close()
else:
    print("Q-learning: Loading epsilon")
    file = open("epsilon", "r")
    epsilon = float(file.read())

window = tk.Tk()

"""
alpha is the learning rate, which determines how much newly acquired information overrides old information.
gamma is the discount factor, the weight of future rewards, which determines the importance of the future rewards. The discount factor may be approximated by an artifical neural network, to optimize the ai.
epsilon is randomness factor, which determines many time a random action should be taken, in state of a calculated one. This is called "exploring".
Q_0 is the initial condition, which can be set by the first reward (reset of initial conditions). 
"""

alpha = 0.81
gamma = 0.96
epsilon_decay = 1 # De erpsilon decay kunnen we tweeken voor een betere performance
Q_old = 0
invalid_punishment = 1000 # De straf die de AI moet krijgen wanneer de lap invalid is geworden (door b.v. het aanraken van het gras)
no_speed_punishment = 1000 # Des straf die de AI moet krijgen wanneer hij geen snelheid heeft (stilstaan midden op de track of b.v. tegen een muur


def determine_Q(Q_table, data, state_old, actions_old, best_row_index):
    speed = data[0]
    currentLapInvalid = data[6]

    reward = get_reward(data) # Reward bepalen

    ray_front_old, ray_rightfront_old, ray_leftfront_old = state_old
    steering_old = actions_old
    
    # De voorspelling voor de volgende state van de last state wordt gelijk gesteld aan de state die het meest lijkt op de current state, maar alleen als de lap niet gerestart wordt, dan moet er geen hoge Q_max worden toegewezen
    if best_row_index and speed != 0 and currentLapInvalid != 1:
        Q_max = Q_table[best_row_index, 4]
    else:
        Q_max = 0.0

    # Check whether the same state-action pair as the last state-action pair already exists in the Q-table
    row = list(state_old).append(actions_old)
    same_row_index = np.argwhere(np.all(Q_table[:, :4] == row, axis=1) == True) # De same_row_index is de index van de rij die precies dezelfde state en actions heeft als de last state en last actions
    # Als er daadwerkelijk een same_row is, zetten we de Q_old naar de Q-waarde van die row en verwijderen we de row uit de Q-table, zodat hij vervangen kan worden door de nieuwe Q-waarde
    if same_row_index.size != 0:
        same_row_index = same_row_index[0, 0]
        Q_old = Q_table[same_row_index, 4]

        Q_new = Q_old + alpha * (reward + gamma * Q_max - Q_old) # Hier passen we de formule toe die past bij het Q-learning algoritme
        Q_table[same_row_index, 4] = Q_new
    # Als er geen same_row is, wordt Q_old 0.0 (Q_new is dan gewoon de Q bepaald met reward en Q_max), en wordt de nieuwe Q-waarde toegevoegd
    else:
        Q_old = 0.0

        Q_new = Q_old + alpha * (reward + gamma * Q_max - Q_old) # Hier passen we de formule toe die past bij het Q-learning algoritme
        # Voeg de nieuwe row met de state, de actions en de Q-waarde toe aan de Q-table
        Q_table = np.append(Q_table, [[ray_front_old, ray_rightfront_old, ray_leftfront_old, steering_old, Q_new]], axis=0)
    
    # print(f"Q-learning:\tReward: {format(reward, '.16f')},\tQ: {format(Q_new, '.16f')}")

    return Q_table

def get_reward(data):
    # print("Q-learning: Getting reward")
    speed = data[0]
    totalDistance, totalDistance_old, currentLapInvalid = data[4:]


    if currentLapInvalid:
        punishment = invalid_punishment
        reward = 0 - punishment
    elif speed == 0:
        punishment = no_speed_punishment
        reward = 0 - punishment
    else:
        progress = totalDistance - totalDistance_old # De progress is het verschil tussen de progress op dit moment en op het vorige moment, ofwel de afstand langs de center line die de auto heeft afgelegd
        reward = progress ** 3  # De uiteindelijke reward is: de reward van de afstand die is afgelegd

    return reward

def get_best_row(data, Q_table):
    # print("Q-learning: Getting best row")
    speed, ray_front, ray_rightfront, ray_leftfront, totalDistance, totalDistance_old, currentLapInvalid = data
    state = ray_front, ray_rightfront, ray_leftfront


    # Vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    same_state_indexes = np.argwhere(np.all(Q_table[:, :3] == state, axis=1) == True) # The indexes of the Q-table where the state is the same as the current state
    # If there is/are same state(s), detemine which has the best Q-value and determine the Q-table index of that row
    if same_state_indexes.size != 0:
        Q_values = Q_table[same_state_indexes, 4]
        best_row_index = same_state_indexes[np.argmax(Q_values)][0]
    # If there is no same state, there is no best_row_index, so the action must be randomly determined
    else:
        best_row_index = None

    return best_row_index


def determine_actions(Q_table, epsilon, best_row_index):
    # print("Q-learning: Determining actions")
    epsilon = determine_epsilon(epsilon)
    r = random.randint(1, 10000) / 10000
    if r <= epsilon:
        # exploration
        steering = random.randint(-1,1)
        actions = steering
    else:
        # If there is a best row (a row in the Q-table that has the same state, with the highest Q-value), the actions will be the actions of that row
        if best_row_index:
            actions = Q_table[best_row_index, 3]

            Q = Q_table[best_row_index, 4]
            text = tk.Label(text=str(Q))
            text.pack()
        # If there is no same row, determine actions randomly
        else:
            steering = random.randint(-1,1)
            actions = steering
    
    return actions, epsilon

def determine_epsilon(epsilon):
    # print("Q-learning: Determining epsilon")
    epsilon =  epsilon * epsilon_decay
    return epsilon