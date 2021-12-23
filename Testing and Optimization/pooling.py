import multiprocessing
import numpy as np
import time
import concurrent.futures
import threading
from joblib import Parallel, delayed
import asyncio
from ray._private.parameter import RayParams
from ray.util.multiprocessing import Pool

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped

Q_table = np.load("Qtable.npy", allow_pickle=True)
Q_table = Q_table[1:]
Q_table = np.append(Q_table, Q_table, axis = 0)

def calculate_best_row_once(Q_table_row):

    state = 200.0, 50.0, 50.0, 50.0, 50.0, 50.0
    # vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    values = Q_table_row[:6] # hier neemt hij alle data--> speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, van de regel in de Q-tabel die aan de beurt is
    average_array = np.subtract(state, values) # hier neemt hij de huidige data en trekt hiervan de regel uit de Q-tabel die aan de beurt is af
    average = np.average(average_array) # bereken het gemiddelde van de verschillen tussen de arrays
    return average

def calculate_best_row_once_append(Q_table_row, averages, i):

    state = 200.0, 50.0, 50.0, 50.0, 50.0, 50.0
    # vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    values = Q_table_row[:6] # hier neemt hij alle data--> speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, van de regel in de Q-tabel die aan de beurt is
    average_array = np.subtract(state, values) # hier neemt hij de huidige data en trekt hiervan de regel uit de Q-tabel die aan de beurt is af
    average = np.average(average_array) # bereken het gemiddelde van de verschillen tussen de arrays
    averages[i] = average

def calculate_best_row():
    Q_width = int(Q_table[0].size) # de breedte van de Q-table (x-as)
    Q_length = int(Q_table.size / Q_width)
    averages = []
    state = 200.0, 50.0, 50.0, 50.0, 50.0, 50.0
    
    for row_index in range(Q_length):
        values = Q_table[row_index][:6] #hier neemt hij alle data--> speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, van de regel in de Q-tabel die aan de beurt is
        average_array = np.subtract(state, values) #hier neemt hij de huidige data en trekt hiervan de regel uit de Q-tabel die aan de beurt is af
        average = np.average(average_array) # bereken het gemiddelde van de verschillen tussen de array
        averages.append(average)
    
    # # sla het kleinste verschil en het rijnummer met het kleinste verschil op
    # same_row_exists = False
    # lowest_average = np.Infinity
    # for average_index in range(averages2):
    #     average = averages2[average_index]
    #     if average <= lowest_average:
    #         lowest_average = average
    #         best_state_row = average_index
    #     if average == 0:
    #         same_row = average_index
    #         same_row_exists = True
    
    # print(lowest_average)
    # print(best_state_row)
    
    return averages

@background
def calculate_best_row_once_append_asynio(Q_table_row, averages, i):

    state = 200.0, 50.0, 50.0, 50.0, 50.0, 50.0
    # vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
    values = Q_table_row[:6] # hier neemt hij alle data--> speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, van de regel in de Q-tabel die aan de beurt is
    average_array = np.subtract(state, values) # hier neemt hij de huidige data en trekt hiervan de regel uit de Q-tabel die aan de beurt is af
    average = np.average(average_array) # bereken het gemiddelde van de verschillen tussen de arrays
    averages[i] = average


if __name__ == '__main__':
    
    time1 = time.time()
    averages = calculate_best_row()
    time2 = time.time()
    print(f"Original: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    with multiprocessing.pool.ThreadPool() as threadpool:
        averages = threadpool.map(calculate_best_row_once, Q_table)
    time2 = time.time()
    print(f"With ThreadPool: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    with multiprocessing.pool.ThreadPool() as threadpool:
        averages = threadpool.map(calculate_best_row_once, Q_table, 5000)
    time2 = time.time()
    print(f"With ThreadPool and custom chunksize: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    averages = []
    with multiprocessing.pool.ThreadPool() as threadpool:
        for i in threadpool.imap_unordered(calculate_best_row_once, Q_table):
            averages.append(i)
    time2 = time.time()
    print(f"With ThreadPool and imap: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    averages = []
    with multiprocessing.pool.ThreadPool() as threadpool:
        for i in threadpool.imap_unordered(calculate_best_row_once, Q_table, 1000):
            averages.append(i)
    time2 = time.time()
    print(f"With ThreadPool and imap and custom chunksize: {time2 - time1} seconds")
    print(len(averages), "rows")

    # time1 = time.time()
    # with Pool() as raypool:
    #     averages = raypool.map(calculate_best_row_once, Q_table)
    # time2 = time.time()
    # print(f"With RayPool: {time2 - time1} seconds")
    # print(len(averages), "rows")

    time1 = time.time()
    averages = Parallel(n_jobs=2, batch_size=6072)(delayed(calculate_best_row_once)(Q_table_row) for Q_table_row in Q_table)
    time2 = time.time()
    print(f"With joblib: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    averages = []
    for Q_table_row in Q_table:
        average = calculate_best_row_once_append_asynio(Q_table_row)
        averages.append(average)
    time2 = time.time()
    print(f"With asyncio: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    with multiprocessing.Pool() as processpool:
        averages = processpool.map(calculate_best_row_once, Q_table)
    time2 = time.time()
    print(f"With Pool: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        averages = [executor.submit(calculate_best_row_once, Q_table_row) for Q_table_row in Q_table]
        concurrent.futures.wait(averages)
    time2 = time.time()
    print(f"With ThreadPoolExecutor: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        averages = [executor.submit(calculate_best_row_once, Q_table_row) for Q_table_row in Q_table]
        concurrent.futures.wait(averages)
    time2 = time.time()
    print(f"With ProcessPoolExecutor: {time2 - time1} seconds")
    print(len(averages), "rows")

    time1 = time.time()
    threads = []
    Q_width = int(Q_table[0].size) # de breedte van de Q-table (x-as)
    Q_length = int(Q_table.size / Q_width)
    averages = [None] * Q_length
    for i in range(Q_length):
        thread = threading.Thread(target=calculate_best_row_once_append, args=(Q_table[i], averages, i))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    time2 = time.time()
    print(f"Manual multithreading: {time2 - time1} seconds")
    print(len(averages), "rows")

    
