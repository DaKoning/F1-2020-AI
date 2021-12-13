def start():
    current_episode = 0
    Q_table = Qlearning.Q_table
    epsilon = Qlearning.epsilon
    progress_old = Qlearning.progress_old
    frequency = 1
    period = (1.0/frequency)
    
    episodes = 5000 # hoe vaak je de AI wilt laten runnen
    max_time = 1000000 # in seconden
    timeToStop = time.time() + max_time

    delete_progress = Qlearning.delete_progress

    while True:
        timeToEnd = time.time() + period
        current_episode += 1


        # data = data_collection.data # Dit is niet meer nodig, want we halen de data nu direct uit data_collection in Qlearning
        actions, Q_table, epsilon = Qlearning.run(Q_table, epsilon) # data voeden we aan Qlearning en krijgen een return

        if play_game:
            game_input.run(actions)
            if not gw.getActiveWindow().title == windowname:
                print("Main: F1 2020 window not focussed")
                break
                
        ### dit moet eleganter kunnen
        # als het script een exit signaal krijgt, zorgt dit ervoor dat de Q_table en de epsilon worden opgeslagen
        if not delete_progress:
            atexit.unregister(exit_handler) # de exit_handler van de vorige loop wordt verwijderd
            atexit.register(exit_handler, Q_table, epsilon)

        if current_episode >= episodes or timeToStop <= time.time():
            break
            
        if timeToEnd < time.time():
            print(f"Main: Episode: {current_episode}")
            frequency -= 1
            print(f"Main: Frequency: {frequency}")
            period = (1.0/frequency)
            if frequency < 1:
                    print("Main: Can't keep up! Frequency is to high!")
                    break
        while timeToEnd > time.time(): # dit is zodat het proces niet opnieuw start wanneer de periode nog niet is afgerond
            time.sleep(0)
        print(f"Main: Episode: {current_episode}")
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



if __name__ == "__main__":
    from data_collection import run_data_collection
    import game_input
    import Qlearning
    from tabulate import tabulate
    import time
    import atexit
    import numpy as np
    import pygetwindow as gw
    import multiprocessing

    process_1 = multiprocessing.Process(target=run_data_collection)
    process_1.start() # het maakt niet uit dat we data_collection al starten voordat de game is gestart, want we gebruiken de data toch nog niet, maar dit zorgt er wel voor dat alles al geladen is voordat start() begint

    windowname = 'F1 2020 (DirectX 12)'
    play_game = True # If play_game is true, an F1 2020 time trial must be open, else the script can be run without F1 2020
    if play_game:
        activate_window() # focus on F1 2020 window
        time.sleep(0.01)
        game_input.special('A') # press B to exit out of pause menu
        time.sleep(5.75)
    start()
    print("Main: Waiting for Data Collection to end")
    process_1.join()
    print("Main: Data Collection has ended")