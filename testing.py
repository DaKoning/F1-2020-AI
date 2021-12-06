import numpy as np
import random
# Q_table = np.array([[0,0,0]])
# Q_table = np.append(Q_table, [[1,1,1]], axis=0)
# Q_table = np.append(Q_table, [[2,2,2]], axis=0)
# Q_table = np.append(Q_table, [[3,3,3]], axis=0)
# Q_table = np.append(Q_table, [[4,4,4]], axis=0)
# print(Q_table)

# Q_table = np.delete(Q_table, 2, 0)
# print(Q_table)
r = random.randint(0,1)
if r == 0:
    same_row = 0


if 'same_row' in locals():
    print("hello")
else:
    print("joe")