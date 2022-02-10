def start():
    current_episode = 0
    Q_table = Qlearning.Q_table
    epsilon = Qlearning.epsilon
    frequency = 2
    period = (1.0/frequency)
    current_run = 1
    
    episodes = 5000000 # Hoe vaak je de AI wilt laten runnen
    max_time = 1000000 # In seconden
    timeToStop = time.time() + max_time

    times_too_late = 0 # The number of times that the AI can't keep up

    lap_restarted = True

    delete_progress = Qlearning.delete_progress

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
        best_row_index = Qlearning.get_best_row(current_data, Q_table)
        # Als de lap niet (opnieuw) gestart is, dan berekenen we de Q-waarde van de vorige state-action pair
        if not lap_restarted:
            Q_table = Qlearning.determine_Q(Q_table, current_data, state_old, actions_old, best_row_index)
        else:
            lap_restarted = False
    
        actions, epsilon = Qlearning.determine_actions(Q_table, epsilon, best_row_index) # data voeden we aan Qlearning en krijgen een return
        # De acties worden alleen uitgevoerd als we het spel willen spelen
        if play_game:
            # print("Main: Executing actions")
            game_input.run(actions)
        
        data[5] = current_data[4] # De nieuwe totalDistance_old wordt de totalDistance, zodat in de volgende tijdsstap de totalDistance_old klopt
        actions_old = actions # We stellen actions_old gelijk aan actions, zodat die in de volgende tijdsstap kunnen worden gebruikt voor het bepalen van de Q-waarde van deze tijdsstap
        state_old = current_data[1:4] # We stellen state_old gelijk aan de state van nu, zodat die in de volgende tijdsstap kan worden gebruikt voor het bepalen van de Q-waarde van deze tijdsstap
        
        # Als het script een exit signaal krijgt, zorgt dit ervoor dat de Q_table en de epsilon worden opgeslagen
        if not delete_progress:
            # print("Main: Registering exit handler")
            atexit.unregister(exit_handler) # de exit_handler van de vorige loop wordt verwijderd
            atexit.register(exit_handler, Q_table, epsilon)
    
        # Als currentLapInvalid == 1 (de lap is invalid), of als er geen snelheid is (bijvoorbeeld wanneer de auto tegen een muur aan staat), dan restarten we de lap. Dit gebeurt na de Qlearning.determine_Q functie, zodat er een straf is bepaald voor de actie die hiertoe heeft geleid
        if current_data[6] == 1 or current_data[1] == 0 or current_data[2] == 0 or current_data[3] == 0:
            print("Main: Lap invalid")
            current_run = restart_lap(current_episode, current_run)
            lap_restarted = True
        elif current_data[0] == 0:
            print("Main: No speed")
            current_run = restart_lap(current_episode, current_run)
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


def exit_handler(Q_table, epsilon):
    print("Main: AI was interrupted!")
    save(Q_table, epsilon)

def save(Q_table, epsilon):        
    print("Main: Saving AI state...")
    np.save("Qtable", Q_table)
    print("Main: Q-table saved!")
    file = open("epsilon", "w")
    file.write(str(epsilon))
    file.close
    print("Main: Epsilon saved!")

def activate_window():
    print(f"Main: Focussing {windowname}")
    win = gw.getWindowsWithTitle(windowname)[0]
    try:
        win.activate()
        print(f"Main: Focussed {windowname}")
    except gw.PyGetWindowException:
        print(f"Main: Could not focus {windowname}")

def restart_lap(current_episode, current_run):
    print("Main: Restarting lap")
    distance = data[4]
    file = open("distance", "a")
    file.write(f"Run {current_run}:     distance: {distance}\n")
    file.close()
    current_run += 1
    game_input.special('start') # Press start to open menu
    time.sleep(0.5)
    game_input.special('A') # Press A to restart lap
    time.sleep(5.75)
    data[6] = 0 # Zet currentLapInvalid == 0, zodat de lap niet meteen nog een keer wordt gerestart
    game_input.special('go_to_location')
    print('Main: Go!')

    return current_run

if __name__ == "__main__":
    from data_collection import run, startDistance, data
    import game_input
    import Qlearning
    from tabulate import tabulate
    import time
    import atexit
    import numpy as np
    import pygetwindow as gw
    from multiprocessing import Process, Array

    starting_time = time.time()

    data = Array('d', data)
    process_1 = Process(target=run, args=(data,))
    process_1.start() # Het maakt niet uit dat we data_collection al starten voordat de game is gestart, want we gebruiken de data toch nog niet, maar dit zorgt er wel voor dat alles al geladen is voordat start() begint

    windowname = 'F1 2020 (DirectX 12)'
    play_game = True # If play_game is true, an F1 2020 time trial must be open, else the script can be run without F1 2020
    if play_game:
        activate_window() # Focus on F1 2020 window
        time.sleep(0.01)
        game_input.special('left_thumb') # Zorgt ervoor dat de controller module geladen is
        time.sleep(0.5)
        game_input.special('left_thumb') # Zorgt ervoor dat de controller module geladen is
        time.sleep(0.5)
        game_input.special('A') # Press A to restart lap
        time.sleep(5.75)
        game_input.special('go_to_location')
        print('Main: Go!')
    start()
    print("Main: Waiting for Data Collection to end")
    process_1.join()
    print("Main: Data Collection has ended")

    # We slaan de totale tijd die de AI runt op
    ending_time = time.time()
    running_time = ending_time - starting_time
    with open("time", "r") as file:
        total_time = float(file.read())
    total_time += running_time
    file = open("time", "w")
    file.write(str(round(total_time)))
    file.close()

    print("Main: Finished")