import game_input
import data_collection
import Qlearning
from tabulate import tabulate
import time
import atexit
import numpy as np
import pygetwindow as gw

windowname = 'F1 2020 (DirectX 12)'
play_game = False # If play_game is true, an F1 2020 time trial must be open, else the script can be run without F1 2020

def start():
    done = False
    current_episode = 0
    Q_table = Qlearning.Q_table
    epsilon = Qlearning.epsilon
    progress_old = Qlearning.progress_old
    frequency = 5
    period = (1.0/frequency)
    
    episodes = 50000 # hoe vaak je de AI wilt laten runnen
    max_time = 100000 # in seconden
    timeToStop = time.time() + max_time

    delete_progress = Qlearning.delete_progress

    while not done:
        timeToEnd = time.time() + period
        current_episode += 1

        #print(f"Episode: {current_episode}")

        data, progress = data_collection.get_variables() # haalt dat op uit data_collection
        actions, progress_old, Q_table, epsilon = Qlearning.run(data, progress, progress_old, Q_table, epsilon) # data voeden we aan Qlearning en krijgen een return
        if play_game:
            game_input.run(actions)
            if not gw.getActiveWindow().title == windowname:
                done = True
        
        ### dit moet eleganter kunnen
        # als het script een exit signaal krijgt, zorgt dit ervoor dat de Q_table en de epsilon worden opgeslagen
        if not delete_progress:
            atexit.unregister(exit_handler) # de exit_handler van de vorige loop wordt verwijderd
            atexit.register(exit_handler, Q_table, epsilon)

        if current_episode >= episodes or timeToStop <= time.time():
            done = True
            
        if timeToEnd < time.time():
            print(f"Episode: {current_episode}")
            frequency -= 1
            print(f"Frequency: {frequency}")
            period = (1.0/frequency)
            if frequency < 1:
                    print("Can't keep up! Frequency is to high!")
                    break
        while timeToEnd > time.time(): # dit is zodat het proces niet opnieuw start wanneer de periode nog niet is afgerond
            time.sleep(0)
    # print(f"Episode: {current_episode}")


def exit_handler(Q_table, epsilon):
    print('AI was interrupted!')
    save(Q_table, epsilon)


def save(Q_table, epsilon):        
    print("Saving AI state...")
    np.save("Qtable", Q_table)
    print("Q-table saved!")
    file = open("epsilon", "w")
    file.write(str(epsilon))
    file.close
    print("Epsilon saved!")

def activate_window():
    win = gw.getWindowsWithTitle(windowname)[0]
    win.activate()

if __name__ == "__main__":
    if play_game:
        activate_window() # focus on F1 2020 window
        time.sleep(1)
        game_input.special('B') # press B to exit out of pause menu
        time.sleep(0.1)
    start()