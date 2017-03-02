_author__ = "Marco Clerici"

import sys
from config import es_constants
from apps.es2system import es2system
from lib.python import es_logging as log
logger = log.my_logger("apps.es2system.ingest_archive")

try:
    command = str(sys.argv[1])
except: 
    logger.fatal("An argument should be provided: status/start/stop") 
    exit(1)

# Define pid file and create daemon
pid_file = es_constants.ingest_archive_pid_filename
daemon = es2system.IngestArchiveDaemon(pid_file, dry_run=1)

if command == "status":
        status = daemon.status()
        print("Current status of the IngestArchive Service: %s" % status)
    
if command == "start":
        logger.info("Starting IngestArchive service")
        daemon.start()
        
if command == "stop":
        logger.info("Stopping IngestArchive service")
        daemon.stop()
