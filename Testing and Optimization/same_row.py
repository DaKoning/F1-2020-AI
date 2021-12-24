import numpy as np
import time

Q_table = np.array([[1, 2, 3, 4, 5, 6.0, 7.0, 8.0, 9.0, 10.0], [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]], dtype=object)

state = 2, 4, 6, 8, 10, 12
actions = 14, 16, 18
row = state + actions

time1 = time.time()
same_row_index = np.argwhere(np.all(Q_table[:, :9] == row, axis=1) == True)
time2 = time.time()
print(f"np.all: {time2 - time1}")

time1 = time.time()
same_row_index = np.argwhere((Q_table[:, 0] == row[0]) & (Q_table[:, 1] == row[1]) & (Q_table[:, 2] == row[2]) & (Q_table[:, 3] == row[3]) & (Q_table[:, 4] == row[4]) & (Q_table[:, 5] == row[5]) & (Q_table[:, 6] == row[6]) & (Q_table[:, 7] == row[7]) & (Q_table[:, 8] == row[8]))
time2 = time.time()
print(f"manual: {time2 - time1}")

print(same_row_index)
if same_row_index.size != 0:
    same_row_index = same_row_index[0, 0]
    Q_old = Q_table[same_row_index, 9]
    same_row_exists = True
else:
    Q_old = 0.0
    same_row_exists = False
print(same_row_index)
print(Q_old)