import numpy as np
import random
from os.path import exists

delete_progress = False

if delete_progress or not exists("Qtable.npy"):
    # Q_table = 'speed', 'ray_front', 'ray_right', 'ray_left', 'ray_rightfront', 'ray_leftfront', 'throttle', 'brakes', 'steering', 'Q'
    print("Q-learning: Creating Q-table")
    Q_table = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=object) 
    np.save("Qtable", Q_table)
else:
    print("Q-learning: Loading Q-table")
    Q_table = np.load("Qtable.npy", allow_pickle=True)

if delete_progress or not exists("epsilon"):
    print("Q-learning: Creating epsilon")
    epsilon = 0.75
    file = open("epsilon", "w")
    file.write(str(epsilon))
    file.close
else:
    print("Q-learning: Loading epsilon")
    file = open("epsilon", "r")
    epsilon = float(file.read())

Q_old = 0

alpha = 0.81
gamma = 0.96
epsilon_decay = 1 # De erpsilon decay kunnen we tweeken voor een betere performance
invalid_punishment = 100 # De straf die de AI moet krijgen wanneer de lap invalid is geworden (door b.v. het aanraken van het gras)
no_speed_punishment = 100 # Des straf die de AI moet krijgen wanneer hij geen snelheid heeft (stilstaan midden op de track of b.v. tegen een muur)

def Qlearning_algo(data, Q_table, epsilon):
    """
    alpha is the learning rate, which determines how much newly acquired information overrides old information.
    gamma is the discount factor, the weight of future rewards, which determines the importance of the future rewards. The discount factor may be approximated by an artifical neural network, to optimize the ai.
    epsilon is randomness factor, which determines many time a random action should be taken, in state of a calculated one. This is called "exploring".
    Q_0 is the initial condition, which can be set by the first reward (reset of initial conditions). 
    """
    
    speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, totalDistance, totalDistance_old, currentLapInvalid = data
    state = speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront

    reward = get_reward(data) # Reward bepalen
    Q_length = Q_table.shape[0] # De lengte van de Q-table (y-as) zonder de headers

    # Vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    same_state_indexes = np.argwhere(np.all(Q_table[:, :6] == state, axis=1) == True) # The indexes of the Q-table where the state is the same as the current state
    # If there is/are same state(s), detemine which has the best Q-value and determine the Q-table index of that row
    if same_state_indexes.size != 0:
        Q_values = Q_table[same_state_indexes, 9]
        best_row_index = same_state_indexes[np.argmax(Q_values)][0]

        # De voorspelling voor de volgende state wordt gelijk gesteld aan de state die volgt op de state uit de best row
        future_state_index = best_row_index + 1 # De voorspelling voor de volgende state
    # If there is no same state, there is no best_row_index, so the action must be randomly determined
    else:
        best_row_index = None
        
        # De voorspelling voor de volgende state wordt gelijk gesteld aan de state die volgt op de state die het meest op de huidige state lijkt, maar alleen als de lap niet opnieuw wordt gestart
        if speed != 0 and currentLapInvalid != 1:
            Q_table_state = Q_table[:, :6] # Q_table_state is the state part of the Q-table without the headers 
            state_resized = np.resize(state, (Q_length, 6)) # Make a two dimensional array of the state repeated, where the length is the length of the Q-table, so that we can subtract them
            subtracted_array = np.subtract(Q_table_state, state_resized) # The differences between the states in the Q-table and the current state
            average_array = np.absolute(np.average(subtracted_array, axis=1)) # The averages of the differences per state, in absolutes so that we can determine the lowest average
            most_similar_state_index = np.argmin(average_array) # The index of the row of the Q-table that is most similar to the current state
            future_state_index = most_similar_state_index + 1 # De voorspelling voor de volgende state
        # Als de lap wel opnieuw wordt gestart, wordt de future state Q-waarde 0 (bij Q-table index van 0)
        else:
            future_state_index = 0
    
    # Als de future state van de best row in de Q-table bestaat, nemen we daarvan de Q-waarde, anders nemen we de Q-waarde van de beste row zelf, en als dat niet kan, nemen we de Q-waarde van de state die er het meest op lijkt
    if 0 <= future_state_index < Q_length - 1:
        Q_max = Q_table[future_state_index, 9]
    elif best_row_index:
        Q_max = Q_table[best_row_index, 9]
    else:
        Q_max = Q_table[most_similar_state_index, 9]
    
    
    actions, epsilon = determine_action(Q_table, best_row_index, epsilon)
    throttle, brakes, steering = actions

    # Check whether the same state-action pair as the current state-action pair already exists in the Q-table
    row = list(state) + actions
    same_row_index = np.argwhere(np.all(Q_table[:, :9] == row, axis=1) == True) # De same_row_index is de index van de rij die precies dezelfde state en actions heeft als de current state en determined actions
    # Als er daadwerkelijk een same_row is, zetten we de Q_old naar de Q-waarde van die row en verwijderen we de row uit de Q-table, zodat hij vervangen kan worden door de nieuwe Q-waarde
    if same_row_index.size != 0:
        same_row_index = same_row_index[0, 0]
        Q_old = Q_table[same_row_index, 9]

        Q_new = Q_old + alpha * (reward + gamma * Q_max - Q_old) # Hier passen we de formule toe die past bij het Q-learning algoritme
        Q_table[same_row_index, 9] = Q_new
    # Als er geen same_row is, wordt Q_old 0.0 (Q_new is dan gewoon de Q bepaald met reward en Q_max), en wordt de nieuwe Q-waarde toegevoegd
    else:
        Q_old = 0.0

        Q_new = Q_old + alpha * (reward + gamma * Q_max - Q_old) # Hier passen we de formule toe die past bij het Q-learning algoritme
        # Voeg de nieuwe row met de state, de actions en de Q-waarde toe aan de Q-table
        Q_table = np.append(Q_table, [[speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, throttle, brakes, steering, Q_new]], axis=0)
    
    return [throttle, brakes, steering], Q_table, epsilon

def get_reward(data):
    speed = data[0]
    totalDistance, totalDistance_old, currentLapInvalid = data[6:]

    if currentLapInvalid:
        punishment = invalid_punishment
    elif speed == 0:
        punishment = no_speed_punishment
    else:
        punishment = 0
    progress = totalDistance - totalDistance_old # De progress is het verschil tussen de progress op dit moment en op het vorige moment, ofwel de afstand langs de center line die de auto heeft afgelegd
    reward = progress ** 2 - punishment # De uiteindelijke reward is: de reward van de afstand die is afgelegd - de straf die de AI gekregen heeft voor raken van een grens
    print(f"Q-learning: Reward: {reward}")
    data[7] = totalDistance # De nieuwe totalDistance_old wordt de totalDistance, zodat in de volgende tijdsstap de totalDistance_old klopt

    return reward

def determine_action(Q_table, best_row_index, epsilon):
    epsilon = determine_epsilon(epsilon)
    r = random.randint(1, 10000) / 10000
    if r <= epsilon:
        # exploration
        throttle = random.randint(0,10)
        brakes = random.randint(0,10)
        steering = random.randint(-10,10)
        actions = [throttle, brakes, steering] 
    else:
        # If there is a best row (a row in the Q-table that has the same state, with the highest Q-value), the actions will be the actions of that row
        if best_row_index:
            actions = list(Q_table[best_row_index, 6:9])
        # If there is no same row, determine actions randomly
        else:
            throttle = random.randint(0,10)
            brakes = random.randint(0,10)
            steering = random.randint(-10,10)
            actions = [throttle, brakes, steering] 
    return actions, epsilon

def determine_epsilon(epsilon):
    epsilon =  epsilon * epsilon_decay
    return epsilon

def run(data, Q_table, epsilon):
    actions, Q_table, epsilon = Qlearning_algo(data, Q_table, epsilon)
    return actions, Q_table, epsilon