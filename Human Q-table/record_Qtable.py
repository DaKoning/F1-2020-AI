import numpy as np
from os.path import exists

delete_progress = False

if delete_progress or not exists("Human Q-table/Qtable.npy"):
    # Q_table = 'speed', 'ray_front', 'ray_right', 'ray_left', 'ray_rightfront', 'ray_leftfront', 'throttle', 'brakes', 'steering', 'Q'
    print("Creating Q-table")
    Q_table = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=object)
    np.save("Human Q-table/Qtable", Q_table)
else:
    print("Loading Q-table")
    Q_table = np.load("Human Q-table/Qtable.npy", allow_pickle=True)

alpha = 0.81
gamma = 0.96
Q_old = 0
invalid_punishment = 1000 # De straf die de AI moet krijgen wanneer de lap invalid is geworden (door b.v. het aanraken van het gras)
no_speed_punishment = 1000 # Des straf die de AI moet krijgen wanneer hij geen snelheid heeft (stilstaan midden op de track of b.v. tegen een muur


def determine_Q(Q_table, data, state_old, actions_old, best_row_index):
    speed = data[0]
    currentLapInvalid = data[8]

    reward = get_reward(data) # Reward bepalen

    speed_old, ray_front_old, ray_right_old, ray_left_old, ray_rightfront_old, ray_leftfront_old = state_old
    throttle_old, brakes_old, steering_old = actions_old
    
    # De voorspelling voor de volgende state van de last state wordt gelijk gesteld aan de state die het meest lijkt op de current state, maar alleen als de lap niet gerestart wordt, dan moet er geen hoge Q_max worden toegewezen
    if best_row_index and speed != 0 and currentLapInvalid != 1:
        Q_max = Q_table[best_row_index, 9]
    else:
        Q_max = 0.0

    # Check whether the same state-action pair as the last state-action pair already exists in the Q-table
    row = list(state_old) + actions_old
    same_row_index = np.argwhere(np.all(Q_table[:, :9] == row, axis=1) == True) # De same_row_index is de index van de rij die precies dezelfde state en actions heeft als de last state en last actions
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
        Q_table = np.append(Q_table, [[speed_old, ray_front_old, ray_right_old, ray_left_old, ray_rightfront_old, ray_leftfront_old, throttle_old, brakes_old, steering_old, Q_new]], axis=0)
    
    # print(f"Q-learning:\tReward: {format(reward, '.16f')},\tQ: {format(Q_new, '.16f')}")

    return Q_table

def get_reward(data):
    # print("Q-learning: Getting reward")
    speed = data[0]
    totalDistance, totalDistance_old, currentLapInvalid = data[6:9]


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
    speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, totalDistance, totalDistance_old, currentLapInvalid, throttle, brakes, steering = data
    state = speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront

    # Vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    same_state_indexes = np.argwhere(np.all(Q_table[:, :6] == state, axis=1) == True) # The indexes of the Q-table where the state is the same as the current state
    # If there is/are same state(s), detemine which has the best Q-value and determine the Q-table index of that row
    if same_state_indexes.size != 0:
        Q_values = Q_table[same_state_indexes, 9]
        best_row_index = same_state_indexes[np.argmax(Q_values)][0]
    # If there is no same state, there is no best_row_index, so the action must be randomly determined
    else:
        best_row_index = None

    return best_row_index



def start(Q_table):
    current_episode = 0
    frequency = 10
    period = (1.0/frequency)
    
    episodes = 5000000 # Hoe vaak je de AI wilt laten runnen
    max_time = 1000000 # In seconden
    timeToStop = time.time() + max_time

    lap_restarted = True
    
    times_too_late = 0 # The number of times that the AI can't keep up


    while True:
        timeToEnd = time.time() + period
        current_episode += 1
        # print(f"Main: Episode: {current_episode}")
        if play_game:
            if not gw.getActiveWindow().title == windowname:
                    print("Main: F1 2020 window not focussed")
                    break

        current_data = data # We zetten data vast in current_data, zodat alle functies hierna dezelfde data gebruiken
        # We bepalen de index van de rij die het meest lijkt op de current state, deze hebben we nodig om de Q-waarde van de vorige state te bepalen, maar ook om te bepalen wat nu de beste actie is
        best_row_index = get_best_row(current_data, Q_table)
        # Als de lap niet (opnieuw) gestart is, dan berekenen we de Q-waarde van de vorige state-action pair
        
        if not lap_restarted:
            Q_table = determine_Q(Q_table, current_data, state_old, actions_old, best_row_index)
        else:
            lap_restarted = False
        
        actions = current_data[9:]
        
        data[7] = current_data[6] # De nieuwe totalDistance_old wordt de totalDistance, zodat in de volgende tijdsstap de totalDistance_old klopt
        actions_old = actions # We stellen actions_old gelijk aan actions, zodat die in de volgende tijdsstap kunnen worden gebruikt voor het bepalen van de Q-waarde van deze tijdsstap
        state_old = current_data[:6] # We stellen state_old gelijk aan de state van nu, zodat die in de volgende tijdsstap kan worden gebruikt voor het bepalen van de Q-waarde van deze tijdsstap
        
        # Als het script een exit signaal krijgt, zorgt dit ervoor dat de Q_table en de epsilon worden opgeslagen
        if not delete_progress:
            # print("Main: Registering exit handler")
            atexit.unregister(exit_handler) # de exit_handler van de vorige loop wordt verwijderd
            atexit.register(exit_handler, Q_table)
    
        # Als currentLapInvalid == 1 (de lap is invalid), of als er geen snelheid is (bijvoorbeeld wanneer de auto tegen een muur aan staat), dan restarten we de lap. Dit gebeurt na de Qlearning.determine_Q functie, zodat er een straf is bepaald voor de actie die hiertoe heeft geleid
        if current_data[8] == 1:
            print("Main: Lap invalid")
            restart_lap()
            lap_restarted = True
        elif current_data[0] == 0:
            print("Main: No speed")
            restart_lap()
            lap_restarted = True
        else: # Als de lap invalid is en dus opnieuw op moet worden gestart, moet er niet gecheckt worden of de fuctie te traag is, omdat het opnieuw opstarten 6 seconden duurt
            if timeToEnd < time.time():
                print("Main: Can't keep up! Frequency is too high!")
                print(f"Main: Episode: {current_episode}")
                times_too_late += 1
                if times_too_late >= 2:
                    break
            # Als de maximale hoeveelheid episodes of tijd verstreken is, stopt de loop
            if current_episode >= episodes or timeToStop <= time.time():
                print("Main: It's time to stop")
                print(f"Main: Episode: {current_episode}")
                break
            while timeToEnd > time.time(): # Dit is zodat het proces niet opnieuw start wanneer de periode nog niet is afgerond
                time.sleep(0)
    game_input.special('start') # Press start to open menu, so that data_collection stops
    print("Main: start() has stopped")


def restart_lap():
    print("Main: Restarting lap")
    game_input.special('start') # Press start to open menu
    time.sleep(0.5)
    game_input.special('A') # Press A to restart lap
    time.sleep(5.75)
    data[7] = startDistance # De oude distance moet weer beginnen op de startDistance, zodat de rewardbepaling bij de eerste episode klopt
    data[8] = 0 # Zet currentLapInvalid == 0, zodat de lap niet meteen nog een keer wordt gerestart

def exit_handler(Q_table):
    print("Main: AI was interrupted!")
    save(Q_table)

def save(Q_table):        
    print("Main: Saving AI state...")
    np.save("Human Q-table/Qtable", Q_table)
    print("Main: Q-table saved!")


def activate_window():
    print(f"Main: Focussing {windowname}")
    win = gw.getWindowsWithTitle(windowname)[0]
    try:
        win.activate()
        print(f"Main: Focussed {windowname}")
    except gw.PyGetWindowException:
        print(f"Main: Could not focus {windowname}")

if __name__ == "__main__":
    from action_collection import run, startDistance, data
    import game_input
    import time
    import atexit
    import numpy as np
    import pygetwindow as gw
    from multiprocessing import Process, Array


    data = Array('d', data)
    process_1 = Process(target=run, args=(data,))
    process_1.start() # Het maakt niet uit dat we data_collection al starten voordat de game is gestart, want we gebruiken de data toch nog niet, maar dit zorgt er wel voor dat alles al geladen is voordat start() begint

    windowname = 'F1 2020 (DirectX 12)'
    play_game = False # If play_game is true, an F1 2020 time trial must be open, else the script can be run without F1 2020

    activate_window() # Focus on F1 2020 window
    time.sleep(0.01)
    game_input.special('left_thumb') # Zorgt ervoor dat de controller module geladen is
    time.sleep(0.5)
    game_input.special('left_thumb') # Zorgt ervoor dat de controller module geladen is
    time.sleep(0.5)
    game_input.special('A') # Press A to restart lap
    time.sleep(5.75)
    start(Q_table)
    print("Main: Waiting for Data Collection to end")
    process_1.join()
    print("Main: Data Collection has ended")

    print("Main: Finished")