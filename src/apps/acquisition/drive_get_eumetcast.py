from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
_author__ = "Marco Clerici"

import sys, os, time
from config import es_constants
from apps.acquisition import get_eumetcast
from apps.acquisition import acquisition
from lib.python import es_logging as log
logger = log.my_logger("apps.acquisition.drive_get_eumetcast")

# Manual Switch for START/STOP
do_start = True
dry_run = False
service  = False
use_ftp  = False

if sys.platform == 'win32':
    use_ftp  = True

# service is always False because this module is used by the windows version or for testing
# ToDo: The code under the if statement can be deleted, service_get_eumetcast.py is now used by non windows versions
if service:
    # Make sure the pid dir exists
    if not os.path.isdir(es_constants.pid_file_dir):
        try:
            os.makedirs(es_constants.pid_file_dir)
        except os.error:
            logger.error("Cannot create pid directory")

    # Define pid file and create daemon
    pid_file = es_constants.get_eumetcast_pid_filename
    daemon = acquisition.GetEumetcastDaemon(pid_file, dry_run=dry_run)

    if do_start:
        if daemon.status():
            logger.info('GetEumetcast process is running: Exit')
        else:
            logger.info('GetEumetcast process is NOT running: Start it.')
            daemon.start()
    else:
        if not daemon.status():
            logger.info('GetEumetcast process is NOT running: Exit')
        else:
            logger.info('GetEumetcast process is running: Stop it.')
            daemon.stop()
else:
    if use_ftp:
        get_eumetcast.loop_eumetcast_ftp(dry_run=dry_run)
    else:
        get_eumetcast.loop_eumetcast(dry_run=dry_run)

