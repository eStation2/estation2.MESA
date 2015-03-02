_author__ = "Marco Clerici"

import sys
# import os, time
from config import es_constants
# from apps.acquisition import ingestion
from apps.acquisition import acquisition
from lib.python import es_logging as log
logger = log.my_logger(__name__)

command = str(sys.argv[1])
# Define pid file and create daemon
pid_file = es_constants.ingestion_pid_filename
daemon = acquisition.IngestionDaemon(pid_file, dry_run=0)

if command == "status":
        status = daemon.status()
        print("Current status of the Service: %s" % status)
    
if command == "start":
        daemon.start()
        
if command == "stop":
        daemon.stop()
