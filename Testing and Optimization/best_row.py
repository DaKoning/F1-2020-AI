import  numpy as np
import time


Q_table = np.load("Qtable.npy", allow_pickle=True)
Q_table_plain = Q_table[1:]


Q_width = int(Q_table_plain[0].size) # de breedte van de Q-table (x-as)
Q_length = int(Q_table_plain.size / Q_width) # de lengte van de Q-table (y-as)
lowest_average = np.Infinity # we zetten eerst het laagste gemiddelde voor het verschil tussen de state en een state uit de tabel naar oneindig, zodat de eerste sowieso kleiner is
state = np.array([200.0, 50.0, 50.0, 50.0, 50.0, 50.0])

new_Q_length = Q_length * 1
Q_table_plain = np.resize(Q_table_plain, (new_Q_length, 10))

print(f"Q_table length: {new_Q_length}")

# Original
time1 = time.time()
# vergelijkt de current state met alle states in de Q-table en berekent de state in de Q-table die het meest op de current state lijkt
for row in range(new_Q_length):
    values = Q_table_plain[row][:6] #hier neemt hij alle data--> speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, van de regel in de Q-tabel die aan de beurt is
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
time2 = time.time()
print(f"Original: {time2 - time1} seconds")


# Optimized
time1 = time.time()
Q_table_state = Q_table_plain[:, :6]
state_resized = np.resize(state, (new_Q_length, 6))
subtracted_array = np.subtract(Q_table_state, state_resized)
average_array = np.average(subtracted_array, axis=1)
average_array_absolute = np.absolute(average_array)
best_row_index = np.argmin(average_array_absolute)
lowest_average = average_array_absolute[best_row_index]
if lowest_average == 0:
    same_row_index = best_row_index
    same_row_exists = True
else:
    same_row_exists = False
time2 = time.time()
print(f"Opitmized: {time2 - time1} seconds")

# implement
Q_table_state = Q_table[1:, :6] # Q_table_state is the state part of the Q-table without the headers 
Q_length = Q_table.shape[0] - 1 # de lengte van de Q-table (y-as)
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
