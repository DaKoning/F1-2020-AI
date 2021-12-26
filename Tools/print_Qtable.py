import numpy as np
from tabulate import tabulate

Q_table = np.load("Qtable.npy", allow_pickle=True)
print(tabulate(Q_table))
size = round(Q_table.size / Q_table[0].size) #de size is lengte van de tabel, dus het aantal waarden gedeeld door de breedte
print(f"Q-table size: {size}")