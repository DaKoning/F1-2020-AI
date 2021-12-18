from math import sqrt
import numpy as np
import random
from os.path import exists
from numpy.lib.function_base import average
from tabulate import tabulate
import data_collection

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
    Q_width = int(Q_table[0].size) # de breedte van de Q-table (x-as)
    Q_length = int(Q_table.size / Q_width) # de lengte van de Q-table (y-as)
    lowest_average = np.Infinity # we zetten eerst het laagste gemiddelde voor het verschil tussen de state en een state uit de tabel naar oneindig, zodat de eerste sowieso kleiner is
    
    # vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    for row in range(Q_length)[1:]:
        values = Q_table[row][:6] #hier neemt hij alle data--> speed, ray_dis_0, ray_dis_45, ray_dis_90, ray_dis_135, ray_dis_180 van de regel in de Q-tabel die aan de beurt is
        average_array = np.subtract(state, values) #hier neemt hij de huidige data en trekt hiervan de regel uit de Q-tabel die aan de beurt is af
        average = np.average(average_array) # bereken het gemiddelde van de verschillen tussen de arrays
        # sla het kleinste verschil en het rijnummer met het kleinste verschil op
        same_row_exists = False
        if average <= lowest_average:
            lowest_average = average
            best_state_row = row
        if average == 0:
            same_row = row
            same_row_exists = True
 
            
    resemblance_state = best_state_row # is de rij in de Q-table die het meest lijkt op de huidige state
    future_state = resemblance_state + 1 # de voorspelling voor de volgende state wordt gelijk gesteld aan de state die volgt op de state die het meest op de huidige state lijkt

    # als de future state van de resemblance state bestaat, nemen we daarvan de Q-waarde, anders nemen we de Q-waarde van de resemblance state zelf
    if 0 <= future_state < len(Q_table):
        Q_max = Q_table[future_state][Q_width - 1]
    else:
        Q_max = Q_table[resemblance_state][Q_width - 1]
    
    Q_old = Q_table.item((Q_length - 1, Q_width - 1)) # de Q-waarde van de vorige tijdsstap is de waarde rechts onderin de tabel
    Q_new = Q_old + alpha * (reward + gamma * Q_max - Q_old) #hier passen we de formule toe die past bij het q-learning algoritme
    #Q_new = 0.5 # ook nog een functie voor maken

    actions, epsilon = determine_action(Q_table,  resemblance_state, epsilon)
    throttle, brakes, steering = actions
    
    # als er een rij is met de states die al bestaan, kijk welke een hogere Q-waarde geeft en zet die in de Q-table 
    if same_row_exists:
        if Q_new > Q_table[same_row][Q_width - 1]:
            np.delete(Q_table, same_row, 0)
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
    totalDistance = data[6]
    totalDistance_old = data[7]
    currentLapInvalid = data[8]
    
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