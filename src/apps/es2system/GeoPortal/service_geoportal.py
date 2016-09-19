_author__ = "Marco Clerici"

import sys
from apps.es2system.GeoPortal import system_geoserver
from config import es_constants
from lib.python import es_logging as log

logger = log.my_logger("apps.es2system.GeoPortal.service_geoportal")

try:
    command = str(sys.argv[1])
except: 
    logger.fatal("An argument should be provided: status/start/stop") 
    exit(1)

# Define pid file and create daemon
pid_file = es_constants.system_pid_filename
daemon = system_geoserver.SystemDaemon(pid_file, dry_run=0)

if command == "status":
        status = daemon.status()

        print("Current status of the Service: %s" % status)
    
if command == "start":
        logger.info("Starting System service")
        daemon.start()
        
if command == "stop":
        logger.info("Stopping System service") 
        daemon.stop()
