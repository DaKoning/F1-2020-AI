import numpy as np
from tabulate import tabulate

Q_table = np.load("Qtable.npy", allow_pickle=True)
print(tabulate(Q_table))
size = Q_table.size / Q_table[0].size - 1 #de size is lengte van de tabel, dus het aantal waarden gedeeld door de breedte - 1 (voor de titelrij)
print(f"Q-table size: {size}")