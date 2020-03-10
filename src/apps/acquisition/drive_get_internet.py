from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
_author__ = "Marco Clerici"

import os, time
from config import es_constants
from apps.acquisition import get_internet
from apps.acquisition import acquisition
from lib.python import es_logging as log
logger = log.my_logger(__name__)

# Manual Switch for START/STOP
do_start = True
dry_run  = False
service  = False
only_source = None  # 'JRC:S3A:WRR'

# service is always False because this module is used by the windows version or for testing
# ToDo: The code under the if statement can be deleted, service_get_internet.py is now used by non windows versions
if service:
    # Make sure the pid dir exists
    if not os.path.isdir(es_constants.pid_file_dir):
        try:
            os.makedirs(es_constants.pid_file_dir)
        except os.error:
            logger.error("Cannot create pid directory")

    # Define pid file and create daemon
    pid_file = es_constants.get_internet_pid_filename
    daemon = acquisition.GetInternetDaemon(pid_file, dry_run=dry_run)

    if do_start:
        if daemon.status():
            logger.info('GetInternet process is running: Exit')
        else:
            logger.info('GetInternet process is NOT running: Start it.')
            daemon.start()
    else:
        if not daemon.status():
            logger.info('GetInternet process is NOT running: Exit')
        else:
            logger.info('GetInternet process is running: Stop it.')
            daemon.stop()
else:   # For windows version and for testing
    if only_source is not None:
        get_internet.loop_get_internet(dry_run=dry_run, test_one_source=only_source)
        logger.warning('Get internet running for a single source: %s', only_source)
    else:
        get_internet.loop_get_internet(dry_run=dry_run)

