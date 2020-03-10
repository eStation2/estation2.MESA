from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import str
_author__ = "Marco Clerici"

import sys
from config import es_constants
from apps.es2system import es2system
from lib.python import es_logging as log
logger = log.my_logger("apps.es2system.es2system")

try:
    command = str(sys.argv[1])
except: 
    logger.fatal("An argument should be provided: status/start/stop") 
    exit(1)

# Define pid file and create daemon
pid_file = es_constants.system_pid_filename
daemon = es2system.SystemDaemon(pid_file, dry_run=0)

if command == "status":
        status = daemon.status()
        print ("Current status of the Service: %s" % status)
    
if command == "start":
        logger.info("Starting System service") 
        daemon.start()
        
if command == "stop":
        logger.info("Stopping System service") 
        daemon.stop()
