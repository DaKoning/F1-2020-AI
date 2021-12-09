from numba import jit, cuda, njit
import numpy as np
from timeit import default_timer as timer
# To run on CPU
def func(a):
    for i in range(10000000):
        a[i]+= 1
        
# To run on GPU
@njit
def func2(a, testlist):
    for i in range(10000000):
        a[i]+= 1
    
if __name__=="__main__":
    n = 10000000
    a = np.ones(n, dtype = np.float64)    
    
    start = timer()
    func(a)
    print("without GPU:", timer()-start)    
    
    start = timer()
    func2(a, [1,'a',1])
    # cuda.profile_stop()
    print("with GPU:", timer()-start)
