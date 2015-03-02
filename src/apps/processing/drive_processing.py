__author__ = "Marco Clerici & Jurriann van't Klooster"

import os, time
from config import es_constants
from lib.python import es_logging as log
logger = log.my_logger(__name__)

from apps.processing import processing
start = time.clock()

# Manual Switch for START/STOP
do_start = False
dry_run = False
service = False

if service:
    # Make sure the pid dir exists
    if not os.path.isdir(es_constants.es2globals['pid_file_dir']):
        try:
            os.makedirs(es_constants.es2globals['pid_file_dir'])
        except os.error:
            logger.error("Cannot create pid directory")

    # Define pid file and create daemon
    pid_file = es_constants.es2globals['get_eumetcast_pid_filename']
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
    processing.loop_processing(dry_run=dry_run)
