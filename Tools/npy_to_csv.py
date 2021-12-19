import numpy as np

npy = "Qtable.npy"
csv = "Qtable.csv"

np_array = np.load(npy, allow_pickle=True)
array = np.asarray(np_array)
print(array)
np.savetxt(csv, array, delimiter=',', fmt='%s')