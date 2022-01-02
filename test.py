import numpy as np
from tabulate import tabulate

Q_table = np.load("Qtable.npy", allow_pickle=True)
Q_table = np.delete(Q_table, 2, 1)
Q_table = np.delete(Q_table, 3, 1)

print(tabulate(Q_table))
size = round(Q_table.size / Q_table[0].size) #de size is lengte van de tabel, dus het aantal waarden gedeeld door de breedte
print(f"Q-table size: {size}")