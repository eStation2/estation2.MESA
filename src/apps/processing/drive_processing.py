from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = "Marco Clerici & Jurriann van't Klooster"

import os, time, sys
from config import es_constants
from lib.python import es_logging as log
logger = log.my_logger(__name__)

from apps.processing import processing
start = time.clock()

# Manual Switch for START/STOP
do_start = True
dry_run = True
service = False
serialize = False                   # for debug
# test_one_product = 62               # MODIS_PP on 8daysavg
# test_one_product =  1               # FEWSNET std_precip
# test_one_product = 51               # VGT-NDVI merge 2.2
test_one_product = None               # VGT-NDVI 2.2 std_ndvi_prods_only

# service is always False because this module is used by the windows version or for testing
# ToDo: The code under the if statement can be deleted, service_processing.py is now used by non windows versions
if service:
    # Make sure the pid dir exists
    if not os.path.isdir(es_constants.es2globals['pid_file_dir']):
        try:
            os.makedirs(es_constants.es2globals['pid_file_dir'])
        except os.error:
            logger.error("Cannot create pid directory")

    # Define pid file and create daemon
    pid_file = es_constants.es2globals['processing_pid_filename']
    daemon = processing.ProcessingDaemon(pid_file, dry_run=dry_run)

    if do_start:
        if daemon.status():
            logger.info('Processing service is running: Exit')
        else:
            logger.info('Processing service is NOT running: Start it.')
            daemon.start()
    else:
        if not daemon.status():
            logger.info('Processing service is NOT running: Exit')
        else:
            logger.info('Processing service is running: Stop it.')
            daemon.stop()
else:
    if sys.platform.startswith('win'):
        # get the root and the path for the python script
        root_dir = es_constants.es2globals['www_root_dir']
        parent_dir = os.path.split(root_dir)[0]
        app_dir = es_constants.es2globals['apps_dir']
        python_script_path = os.path.join(app_dir,'processing\processing.py')
        from subprocess import Popen
        p = Popen(["OSGeo4W_python.bat",python_script_path], cwd=parent_dir, shell=True)
        stdout, stderr = p.communicate()
        # TODO delete the 2 lines below...
        # print 'return code'
        # print p.returncode  # is 0 if success
        if p.returncode == 0:
            logger.info("Processing service is running: Success!!")
        else:
            logger.info("Processing service is NOT running: Failure!!")

    else:
        processing.loop_processing(dry_run=dry_run, serialize=serialize, test_one_product=test_one_product)
