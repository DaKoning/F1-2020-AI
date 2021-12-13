print('running script')

def func():
    print("process 2")


if __name__ == '__main__':
    import Qlearning
    import multiprocessing

    p2 = multiprocessing.Process(target=func)
    p2.start()

    p2.join()