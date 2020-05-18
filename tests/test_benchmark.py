import os
import timeit

dev_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stmt = "ping3.ping('127.0.0.1')"
setup = "import sys; sys.path.insert(0, '{}'); import ping3; print('ping3 version:', ping3.__version__)".format(dev_dir)
num = 10000
duration = timeit.timeit(stmt, setup=setup, number=num)
print("The duration of {num} times `{stmt}` is {drtn:.3f} seconds.".format(stmt=stmt, num=num, drtn=duration))
