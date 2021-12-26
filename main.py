def start():
    current_episode = 0
    Q_table = Qlearning.Q_table
    epsilon = Qlearning.epsilon
    frequency = 10
    period = (1.0/frequency)
    
    episodes = 5000000 # Hoe vaak je de AI wilt laten runnen
    max_time = 1000000 # In seconden
    timeToStop = time.time() + max_time

    delete_progress = Qlearning.delete_progress

    while True:
        timeToEnd = time.time() + period
        current_episode += 1
        # print(f"Main: Episode: {current_episode}")

        current_data = data # We zetten data vast in current_data, zodat beide functies hierna dezelfde data gebruiken

        if current_episode != 1:
            Q_table = Qlearning.determine_Q(Q_table, current_data, state_old, actions_old)        
        actions, epsilon = Qlearning.determine_actions(current_data, Q_table, epsilon) # data voeden we aan Qlearning en krijgen een return

        if play_game:
            game_input.run(actions)
            if not gw.getActiveWindow().title == windowname:
                print("Main: F1 2020 window not focussed")
                break
        
        data[7] = current_data[6] # De nieuwe totalDistance_old wordt de totalDistance, zodat in de volgende tijdsstap de totalDistance_old klopt
        actions_old = actions # We stellen actions_old gelijk aan actions, zodat die in de volgende tijdsstap kunnen worden gebruikt voor het bepalen van de Q-waarde van deze tijdsstap
        state_old = current_data[:6] # We stellen state_old gelijk aan de state van nu, zodat die in de volgende tijdsstap kan worden gebruikt voor het bepalen van de Q-waarde van deze tijdsstap

        # Als het script een exit signaal krijgt, zorgt dit ervoor dat de Q_table en de epsilon worden opgeslagen
        if not delete_progress:
            atexit.unregister(exit_handler) # de exit_handler van de vorige loop wordt verwijderd
            atexit.register(exit_handler, Q_table, epsilon)

        
        # print(f"Main: data: {data[:]}")
        # Als currentLapInvalid == 1, dus de lap is invalid, dan restarten we de lap. Dit gebeurt na de Qlearning.run functie, zodat er een straf is bepaald voor de actie die hiertoe heeft geleid
        if data[8] == 1:
            print("Main: Lap invalid")
            restart_lap() # restart de lap
        # Als er geen snelheid is , restarten we de lap, bijvoorbeeld wanneer de auto tegen een muur aan staat
        elif data[0] == 0:
            print("Main: No speed")
            restart_lap()
        else: # Als de lap invalid is en dus opnieuw op moet worden gestart, moet er niet gecheckt worden of de fuctie te traag is, omdat het opnieuw opstarten 6 seconden duurt
            if timeToEnd < time.time():
                print("Main: Can't keep up! Frequency is to high!")
                print(f"Main: Episode: {current_episode}")
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
    win = gw.getWindowsWithTitle(windowname)[0]
    win.activate()
    print(f"Main: Focussed {windowname}")

def restart_lap():
    print("Main: Restarting lap")
    game_input.special('start') # Press start to open menu
    time.sleep(0.5)
    game_input.special('A') # Press A to restart lap
    time.sleep(5.75)
    data[7] = startDistance # De oude distance moet weer beginnen op de startDistance, zodat de rewardbepaling bij de eerste episode klopt

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
        game_input.special('A') # Press A to restart lap
        time.sleep(5.75)
    start()
    print("Main: Waiting for Data Collection to end")
    process_1.join()
    print("Main: Data Collection has ended")