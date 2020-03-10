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
from apps.acquisition import acquisition
from lib.python import es_logging as log
logger = log.my_logger("apps.acquisition.get_eumetcast")

try:
    command = str(sys.argv[1])
except: 
    logger.fatal("An argument should be provided: status/start/stop") 
    exit(1)

# Define pid file and create daemon
pid_file = es_constants.get_eumetcast_pid_filename
daemon = acquisition.GetEumetcastDaemon(pid_file, dry_run=False)

if command == "status":
        status = daemon.status()
        print ("Current status of the Service: %s" % status)
    
if command == "start":
        logger.info("Starting Get EUMETCast service") 
        daemon.start()
        
if command == "stop":
        logger.info("Stopping Get EUMETCast service") 
        daemon.stop()
