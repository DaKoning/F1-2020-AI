import numpy as np
import time

Q_table = np.load("Qtable.npy", allow_pickle=True)

state = 320, 600, 40, 10, 50, 10
actions = 14, 16, 18
row = state + actions



same_state_indexes = np.argwhere(np.all(Q_table[:, :6] == state, axis=1) == True) # The indexes of the Q-table where the state is the same as the current state

# If there is/are same state(s), detemine which has the best Q-value and determine the Q-table index of that row
if same_state_indexes.size != 0:
    Q_values = Q_table[same_state_indexes, 9]
    best_row_index = same_state_indexes[np.argmax(Q_values)][0]
# If there is no same state, there is no best_row_index, so the action must be randomly determined
else:
    best_row_index = None

if best_row_index:
    print("There is a best row index")
else:
    print("There is no best row index")