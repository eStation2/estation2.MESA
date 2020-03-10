from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
import sys
import argparse
from subprocess import *
from multiprocessing import *


def createSyncJob(args):
    print ("We are in!")
    print (args)
    # argslist = [args.estation_sync_file,
    #             args.jobid,
    #             args.action,
    #             args.datapath,
    #             args.jobspath,
    #             args.requestfile,
    #             args.proxy_host,
    #             args.proxy_port,
    #             args.proxy_user,
    #             args.proxy_userpwd
    #             ]

    argslist = ['/srv/www/eStation2/apps/tools/eStationSync.jar',
                "vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_1monmin_dataset",
                "start",
                "/home/webtklooju/mydata/processing/",
                "/eStation2/requests/requestjobs",
                "/eStation2/requests/vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_1monmin_dataset.req",
                "10.168.209.72",
                "8012"]

    job = Popen(['java', '-jar'] + argslist,
                           # close_fds=True,
                           # shell=True,    # pass args as string
                           stdout=PIPE,
                           stderr=STDOUT)  # .pid
    jobstatus = job.poll()
    answer = job.stdout.readline()
    print (answer)
    return answer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-p0", "--estation_sync_file", help="Location of the eStationSync.jar")
    parser.add_argument("-p1", "--jobid", help="Job ID")
    parser.add_argument("-p2", "--action", help="Action = start")
    parser.add_argument("-p3", "--datapath", help="Data path")
    parser.add_argument("-p4", "--jobspath", help="Jobs directory path")
    parser.add_argument("-p5", "--requestfile", help="Path to the created request file")
    parser.add_argument("-p6", "--proxy_host", help="Proxy host - optional.")
    parser.add_argument("-p7", "--proxy_port", help="Proxy port - optional.")
    parser.add_argument("-p8", "--proxy_user", help="Proxy user - optional.")
    parser.add_argument("-p9", "--proxy_userpwd", help="Proxy user password - optional.")

    # args = parser.parse_args()
    # args = argparse.Namespace()
    # print args
    # argslist = vars(args)
    # print argslist
    # argslist = ' -p0 /srv/www/eStation2/apps/tools/eStationSync.jar -p1 vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_1monmin_dataset -p2 start -p3 /home/webtklooju/mydata/processing/ -p4 "/eStation2/requests/requestjobs" -p5 "/eStation2/requests/vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_1monmin_dataset.req" -p6 "10.168.209.72" -p7 "8012" -p8 "" -p9 ""'

    # print argslist

    argslist = {'proxy_user': '',
                'proxy_userpwd': '',
                'requestfile': '/eStation2/requests/vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_1monmin_dataset.req',
                'proxy_host': '10.168.209.72',
                'datapath': '/home/webtklooju/mydata/processing/',
                'jobid': 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_1monmin_dataset',
                'proxy_port': '8012',
                'jobspath': '/eStation2/requests/requestjobs',
                'action': 'start',
                'estation_sync_file': '/srv/www/eStation2/apps/tools/eStationSync.jar'}
    print (argslist)

    createSyncJob(argslist)

    # results_queue = Queue()
    # # p = Process(target=createSyncJob, args=(results_queue,), kwargs=argslist)
    # p = Process(target=createSyncJob, args=(results_queue,))
    # # p.daemon = True
    # p.start()
    # # proc_lists=results_queue.get()
    # p.join()

    # jobstatus = createSyncJob(argslist)
    # createSyncJob(sys.argv[1:])
