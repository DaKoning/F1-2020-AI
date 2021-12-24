import numpy as np
import random
from os.path import exists

delete_progress = False

if delete_progress or not exists("Qtable.npy"):
    # Q_table = 'speed', 'ray_front', 'ray_right', 'ray_left', 'ray_rightfront', 'ray_leftfront', 'throttle', 'brakes', 'steering', 'Q'
    Q_table = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
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
epsilon_decay = 0.999968 # De erpsilon decay kunnen we tweeken voor een betere performance
invalid_punishment = 10 # De straf die de AI moet krijgen wanneer de lap invalid is geworden (door b.v. het aanraken van het gras)

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

    reward = get_reward(data) # Reward bepalen
    # print(reward)
    Q_length = Q_table.shape[0] # De lengte van de Q-table (y-as) zonder de headers

    # Vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    Q_table_state = Q_table[:, :6] # Q_table_state is the state part of the Q-table without the headers 
    state_resized = np.resize(state, (Q_length, 6)) # Make a two dimensional array of the state repeated, where the length is the length of the Q-table, so that we can subtract them
    subtracted_array = np.subtract(Q_table_state, state_resized) # The differences between the states in the Q-table and the current state
    average_array = np.absolute(np.average(subtracted_array, axis=1)) # The averages of the differences per state, in absolutes so that we can determine the lowest average
    Q_array = Q_table[:, 9] # Array of the Q-values of each row in the Q-table
    score_array = np.divide(Q_array, average_array + 1) # Array of the score of each row in the Q-table
    best_row_index = np.argmax(score_array) # The index of the row of the Q-table that has the highest score
            
    future_state_index = best_row_index + 1 # De voorspelling voor de volgende state wordt gelijk gesteld aan de state die volgt op de state die het meest op de huidige state lijkt

    # Als de future state van de best row bestaat, nemen we daarvan de Q-waarde, anders nemen we de Q-waarde van de resemblance state zelf
    if 0 <= future_state_index < Q_length - 1:
        Q_max = Q_table[future_state_index][9]
    else:
        Q_max = Q_table[best_row_index][9]
    
    actions, epsilon = determine_action(Q_table, best_row_index, epsilon)
    throttle, brakes, steering = actions

    # Check whether the same state as the current state already exists in the Q-table
    row = list(state) + actions
    same_row_index = np.argwhere(np.all(Q_table[:, :9] == row, axis=1) == True) # De same_row_index is de index van de rij die precies dezelfde state en actions heeft als de current state en determined actions
    # Als er daadwerkelijk een same_row is, zetten we de Q_old naar de Q-waarde van die row en verwijderen we de row uit de Q-table, zodat hij vervangen kan worden door de nieuwe Q-waarde
    if same_row_index.size != 0:
        same_row_index = same_row_index[0, 0]
        Q_old = Q_table[same_row_index, 9]
        np.delete(Q_table, same_row_index, 0)
        print("Q-learning: Same row exists")
    # Als er geen same_row is, wordt Q_old 0.0 (Q_new is dan gewoon de Q bepaald met reward en Q_max)
    else:
        Q_old = 0.0
    
    Q_new = Q_old + alpha * (reward + gamma * Q_max - Q_old) # Hier passen we de formule toe die past bij het Q-learning algoritme
    
    # Voeg de nieuwe row met de state, de actions en de Q-waarde toe aan de Q-table
    Q_table = np.append(Q_table, [[speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, throttle, brakes, steering, Q_new]], axis=0)

    return [throttle, brakes, steering], Q_table, epsilon

def get_reward(data):
    totalDistance, totalDistance_old, currentLapInvalid = data[6:]
    
    if currentLapInvalid:
        punishment = invalid_punishment
    else:
        punishment = 0
    progress = totalDistance - totalDistance_old # De progress-reward is het verschil tussen de progress op dit moment en op het vorige moment, ofwel de afstand langs de center line die de auto heeft afgelegd
    reward = progress - punishment # De uiteindelijke reward is: de reward van de afstand die is afgelegd - de straf die de AI gekregen heeft voor raken van een grens

    data[7] = totalDistance # De nieuwe totalDistance_old wordt de totalDistance, zodat in de volgende tijdsstap de totalDistance_old klopt

    return reward

def determine_action(Q_table, best_row_index, epsilon):
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
        actions = list(Q_table[best_row_index, 6:9])
         #  Dit zijn de random acties die de AI eerst moet nemen en daar komt vervolgens een state uit die in de AI wordt gevoed
    return actions, epsilon

def determine_epsilon(epsilon):
    epsilon =  epsilon * epsilon_decay
    print(epsilon)
    return epsilon

def run(data, Q_table, epsilon):
    actions, Q_table, epsilon = Qlearning_algo(data, Q_table, epsilon)
    return actions, Q_table, epsilon