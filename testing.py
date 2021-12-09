from numba import njit
import numpy as np

@njit
def func(data, Q_table):
    state = data
    print(state)

Q_table = np.array((('speed', 'ray_dis_0', 'ray_dis_45', 'ray_dis_90', 'ray_dis_135', 'ray_dis_180', 'throttle', 'brakes', 'steering', 'Q')), dtype=object)
Q_table = np.append(Q_table, ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0)), axis=0)
func((0.6543, 0.6543653, 'hallo', 68459.6543), Q_table)