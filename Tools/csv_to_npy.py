import numpy as np

npy = 'Qtable.npy'
csv = 'Qtable.csv'

array = np.genfromtxt(csv, delimiter=",")
print(array)
np.save(npy, array)