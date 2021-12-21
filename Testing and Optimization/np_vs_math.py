import numpy as np
import math
import time


time1 = time.time()
for i in range(10000):  
    print(np.sqrt(i))
time2 = time.time()
delta1 = time2 - time1


time1 = time.time()
for i in range(10000):
    print(math.sqrt(i))
time2 = time.time()
delta2 = time2 - time1


time1 = time.time()
for i in range(10000):
    print(i ** .5)
time2 = time.time()
delta3 = time2 - time1

print(f"numpy: {delta1}")
print(f"math: {delta2}")
print(f"python i**.5: {delta3}")


print(f"fastest: {np.min([delta1, delta2, delta3])}")