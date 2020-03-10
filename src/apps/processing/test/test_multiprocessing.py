from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import range
from multiprocessing import Pool
import time

# def f(x):
#     time.sleep(1)
#     return x*x
#
# if __name__ == '__main__':
#     pool = Pool(processes=2)              # start 4 worker processes
#     for var in range(10):
#         print var
#         pool.apply_async(f, [var])    # evaluate "f(10)" asynchronously
#         #print result.get()
#         #print result
#
#     #print pool.map(f, range(10))          # prints "[0, 1, 4,..., 81]"
#

# from multiprocessing import Process, Manager
# def f(d, l):
#     d[1] = '1'
#     d['2'] = 2
#     d[0.25] = None
#     l.reverse()
#
# if __name__ == '__main__':
#     manager = Manager()
#
#     d = manager.dict()
#     l = manager.list(range(10))
#
#     p = Process(target=f, args=(d, l))
#     p.start()
#     p.join()
#
#     print d
#     print l

import time

from multiprocessing import Process, Queue
from apps.processing import processing_std_precip


if __name__ == '__main__':
    logfile='test-multiprocessing'
    result_queue = Queue()
    # Prepare arguments
    args = {'pipeline_run_level':1, \
            'pipeline_printout_level':0,\
            'prod': 'chirps-dekad',\
            'starting_sprod':'10d',\
            'starting_dates': None,\
            'mapset': 'CHIRP-Africa-5km',\
            'version':'2.0', \
            'logfile':logfile}

    for var in range(1):
        p = Process(target=processing_std_precip.processing_std_precip,  args=(result_queue,), kwargs=args)
        p.start()
        proc_list = result_queue.get()

        for spg in proc_list.list_subprod_groups:
            print (spg.group)
    p.join()

