from math import sqrt
import numpy as np
import random
from os.path import exists
from numpy.lib.function_base import average
from tabulate import tabulate
from multiprocessing import Pool

delete_progress = False

if delete_progress or not exists("Qtable.npy"):
    Q_table = np.array([['speed', 'ray_front', 'ray_right', 'ray_left', 'ray_rightfront', 'ray_leftfront', 'throttle', 'brakes', 'steering', 'Q']], dtype=object)
    Q_table = np.append(Q_table, [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], axis=0)
    np.save("Qtable", Q_table)
else:
    Q_table = np.load("Qtable.npy", allow_pickle=True)

if delete_progress or not exists("epsilon"):
    epsilon = 1.0
    file = open("epsilon", "w")
    file.write(str(epsilon))
    file.close
else:
    file = open("epsilon", "r")
    epsilon = float(file.read())

Q_old = 0
progress_old = 0

alpha = 0.81
gamma = 0.96
epsilon_decay = 0.99999999 # de erpsilon decay kunnen we tweeken voor een betere performance
invalid_punishment = 10 # de straf die de AI moet krijgen wanneer de lap invalid is geworden (door b.v. het aanraken van het gras)

# @jit(forceobj=True)
def Qlearning_algo(data, Q_table, epsilon):
    """
    alpha is the learning rate, which determines how much newly acquired information overrides old information.
    gamma is the discount factor, the weight of future rewards, which determines the importance of the future rewards. The discount factor may be approximated by an artifical neural network, to optimize the ai.
    epsilon is randomness factor, which determines many time a random action should be taken, in state of a calculated one. This is called "exploring".
    Q_0 is the initial condition, which can be set by the first reward (reset of initial conditions). 
    """
    
    # print(data)
    speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, totalDistance, totalDistance_old, currentLapInvalid = data
    state = speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront


    reward = get_reward(data) # reward bepalen
    # print(reward)
    Q_width = Q_table.shape[1] # de breedte van de Q-table (x-as)
    Q_length = Q_table.shape[0] - 1 # de lengte van de Q-table (y-as) zonder de headers
    lowest_average = np.Infinity # we zetten eerst het laagste gemiddelde voor het verschil tussen de state en een state uit de tabel naar oneindig, zodat de eerste sowieso kleiner is

    # vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    Q_table_state = Q_table[1:, :6] # Q_table_state is the state part of the Q-table without the headers 
    state_resized = np.resize(state, (Q_length, 6)) # Make a two dimensional array of the state repeated, where the length is the length of the Q-table, so that we can subtract them
    subtracted_array = np.subtract(Q_table_state, state_resized) # The differences between the states in the Q-table and the current state
    average_array = np.absolute(np.average(subtracted_array, axis=1)) # The averages of the differences per state, in absolutes so that we can determine the lowest average
    best_row_index = np.argmin(average_array) # The index of the row of the Q-table that is most similar to the current state
    lowest_average = average_array[best_row_index] # The value of the lowest average
    # Check whether the same state as the current state already exists in the Q-table, so that we can determine which one to delete
    if lowest_average == 0:
        same_row_index = best_row_index
        same_row_exists = True
    else:
        same_row_exists = False
 
            
    resemblance_state_index = best_row_index # is de rij in de Q-table die het meest lijkt op de huidige state
    future_state_index = resemblance_state_index + 1 # de voorspelling voor de volgende state wordt gelijk gesteld aan de state die volgt op de state die het meest op de huidige state lijkt

    # als de future state van de resemblance state bestaat, nemen we daarvan de Q-waarde, anders nemen we de Q-waarde van de resemblance state zelf
    if 0 <= future_state_index < len(Q_table):
        Q_max = Q_table[future_state_index][Q_width - 1]
    else:
        Q_max = Q_table[resemblance_state_index][Q_width - 1]
    
    Q_old = Q_table.item((Q_length, Q_width - 1)) # de Q-waarde van de vorige tijdsstap is de waarde rechts onderin de tabel
    Q_new = Q_old + alpha * (reward + gamma * Q_max - Q_old) #hier passen we de formule toe die past bij het q-learning algoritme
    #Q_new = 0.5 # ook nog een functie voor maken

    actions, epsilon = determine_action(Q_table,  resemblance_state_index, epsilon)
    throttle, brakes, steering = actions
    
    # als er een rij is met de states die al bestaan, kijk welke een hogere Q-waarde geeft en zet die in de Q-table 
    if same_row_exists:
        if Q_new > Q_table[same_row_index][Q_width - 1]:
            np.delete(Q_table, same_row_index, 0)
            Q_table = np.append(Q_table, [[speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, throttle, brakes, steering, Q_new]], axis=0)
        else:
            pass
    else:
        Q_table = np.append(Q_table, [[speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, throttle, brakes, steering, Q_new]], axis=0)

    # print(tabulate(Q_table))
    # size = Q_table.size / Q_table[0].size - 1 #de size is lengte van de tabel, dus het aantal waarden gedeeld door de breedte - 1 (voor de titelrij)
    # print(f"Q-table size: {size}")

    return [throttle, brakes, steering], Q_table, epsilon

def get_reward(data):
    totalDistance, totalDistance_old, currentLapInvalid = data[6:]
    
    if currentLapInvalid:
        punishment = invalid_punishment
    else:
        punishment = 0
    progress = totalDistance - totalDistance_old # de progress-reward is het verschil tussen de progress op dit moment en op het vorige moment, ofwel de afstand langs de center line die de auto heeft afgelegd
    reward = progress - punishment # de uiteindelijke reward is: de reward van de afstand die is afgelegd - de straf die de AI gekregen heeft voor raken van een grens

    data[7] = totalDistance

    return reward

def determine_action(Q_table, resemblance_state, epsilon):
    epsilon = determine_epsilon(epsilon)
    # print(epsilon)
    r = random.randint(1, 10000) / 10000
    if r <= epsilon:
        # exploration
        throttle = random.randint(0,10)
        brakes = random.randint(0,10)
        steering = random.randint(-10,10)
        actions = [throttle, brakes, steering]
        
    else:
        actions = Q_table[resemblance_state][6:9]
         #  Dit zijn de random acties die de AI eerst moet nemen en daar komt vervolgens een state uit die in de AI wordt gevoed
    return actions, epsilon

def determine_epsilon(epsilon):
    epsilon =  epsilon * epsilon_decay
    
    return epsilon

def run(data, Q_table, epsilon):
    actions, Q_table, epsilon = Qlearning_algo(data, Q_table, epsilon)
    return actions, Q_table, epsilon