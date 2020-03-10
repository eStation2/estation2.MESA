from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
_author__ = "Jurriaan van 't Klooster"

import os, time
from config import es_constants
from apps.acquisition import ingestion
from apps.acquisition import acquisition
from lib.python import es_logging as log
logger = log.my_logger(__name__)

# Manual Switch for START/STOP
do_start = True
dry_run  = False
service  = False
only_prod = None    # 'wd-gee'

# service is always False because this module is used by the windows version or for testing
# ToDo: The code under the if statement can be deleted, service_ingestion.py is now used by non windows versions
if service:
    # Make sure the pid dir exists
    if not os.path.isdir(es_constants.pid_file_dir):
        try:
            os.makedirs(es_constants.pid_file_dir)
        except os.error:
            logger.error("Cannot create pid directory")

    # Define pid file and create daemon
    pid_file = es_constants.ingestion_pid_filename
    daemon = acquisition.IngestionDaemon(pid_file, dry_run=dry_run)

    if do_start:
        if daemon.status():
            logger.info('Ingest process is running: Exit')
        else:
            logger.info('Ingest process is NOT running: Start it.')
            daemon.start()
    else:
        if not daemon.status():
            logger.info('Ingest process is NOT running: Exit')

        else:
            logger.info('Ingest process is running: Stop it.')
            daemon.stop()
else:
    if only_prod is not None:
        ingestion.loop_ingestion(dry_run=dry_run,test_one_product=only_prod)
        logger.warning('Ingestion running for a single product: %s', only_prod)
    else:
        ingestion.loop_ingestion(dry_run=dry_run)
