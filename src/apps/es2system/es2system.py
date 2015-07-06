_author__ = "Marco Clerici"
#
#	purpose: Define the system service
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 26.05.2015
#   descr:	 Manage all background operations (db and data sync, check status, db dump)
#	history: 1.0
#

# source eStation2 base definitions
import os, re
import shutil

# import standard modules
import time, datetime

# import eStation2 modules
from database import querydb
from lib.python import functions
from lib.python import es_logging as log
from config import es_constants

logger = log.my_logger(__name__)
data_dir= es_constants.es2globals['data_dir']

from lib.python.daemon import DaemonDryRunnable

def system_data_sync(source, target):

#   Synchronize data directory from one machine to another (push)
#
    logger.debug("Entering routine %s" % 'system_data_sync')
    # Use rsync.py module


def system_db_sync(source, target, schemas):

#   Synchronize database contents from one instance to another (push)
#
    logger.debug("Entering routine %s" % 'system_db_sync')
    # Use a module (to be identified)

def system_db_dump():

#   Dump the database schemas (for backup)
#
    logger.debug("Entering routine %s" % 'system_db_dump')
    # Use a module (to be identified) for dump

#
# def system_create_report():
#
# #   Create a .zip file with the relevant information to be sent as for diagnostic
# #
#
# def system_recovery_mode():
# #   Manage the transition to/from nominal/recovery mode on a machine
# #
#
def check_delay_time(operation, delay_minutes=None, time=None):

# For a given operation, check if the delay has passed, or if it is time to execute it
#
# Input arguments: operation= is one of the foreseen operations ('sync_data', 'sync_db')
#                  delay= is the delay - in minutes - between two executions
#                  time= is the time (hh:mm) of the day for the execution
#
    logger.debug("Entering routine %s" % 'check_delay_time')

    to_be_executed = False
    # Distinguish between delay/time
    if delay_minutes is not None:
        dir_info=es_constants.pid_file_dir
        operations_info_file=dir_info+os.path.sep+operation+'_execution.info'

        # Read info from the pickle object
        info = functions.load_obj_from_pickle()
        if info is None:
           logger.debug("Operation %s not yet executed: execute it." % operation)
           to_be_executed=True
        else:
            time_latest_execution = info.latest_exec_time
            current_delta=datetime.datetime.now()-time_latest_execution
            current_delta_minutes=int(current_delta.seconds/60)
            if current_delta_minutes > delay_minutes:
               to_be_executed=True

    elif time is not None:
        now=datetime.datetime.now()
        if now.minute==int(time[3:5]) and now.minute==int(time[3:5]):
           to_be_executed=True
    else:
       logger.warning("Either delay_minutes or time has to be defined!")

    return to_be_executed

def system_manage_lock(lock_id, action):

# Manage the lock file for an action
#
# lock_id is whatever string (but 'All_locks' which is reserved)
#
# action can be: check  -> check if it exist
#                   create -> write the file
#                   delete -> remove the file

    logger.debug("Entering routine %s" % 'system_manage_lock')
    # Get variables
    dir_lock=es_constants.pid_file_dir
    status = 0

    if lock_id == 'All_locks':
        if action == 'Delete':
            for f in os.listdir(dir_lock):
              if re.search('action*.lock',f):
                status = os.remove(os.path.join(dir_lock,f))
        else:
            logger.warning("Only delete action is defined for all locks")
    else:
        lock_file=dir_lock+os.path.sep+'action_'+lock_id+'.lock'
        if action == 'Check':
            status = os.path.exists(lock_file)

        if action == 'Delete':
            if os.path.exists(lock_file):
                status = os.path.remove(lock_file)
            else:
                logger.warning("Lock file does not exist: %s" % lock_file)
                status = 1
        if action == 'Create':
            # Touch the file
            with open(lock_file,'a'):
                os.utime(lock_file,None)
    return status

class SystemDaemon(DaemonDryRunnable):
    def run(self):
        loop_system(dry_run=self.dry_run)

def loop_system(dry_run=False):

#    Driver of the system service
#    Reads configuration from the system setting file (system_settings.ini)
#    Calls the active pipelines with the relevant argument
#    Arguments: dry_run -> if > 0, it triggers pipeline_printout() rather than pipeline_run()
#                       -> if < 0, it triggers pipeline_printout_graph() rather than pipeline_run()


    logger.info("Entering routine %s" % 'loop_system')

    # Specific settings for the system operations (to move to user settings)

    delay_data_sync_minutes = 30
    delay_db_sync_minutes   = 30
    time_for_db_dump        = '00:00'

    # Loop to manage the 'cron-like' operations, i.e.:
    #   a. Data sync
    #   b. DB sync
    #   c. DB dump
    while True :

        # Read the relevant info from system settings
        system_settings = {'type_installation': 'Full',
                           'role':'PC2',
                           'mode':'Nominal'}

        # Initialize todo flags
        do_data_sync = False
        schemas_db_sync  = []
        schemas_db_dump  = []

        # Implement the logic of operations based on type/role/mode
        if system_settings['type_installation'] == 'Full':
            if system_settings['role'] == 'PC2':

                if system_settings['mode'] == 'Nominal':
                    do_data_sync = True
                    schemas_db_sync  = ['products']
                    schemas_db_dump  = ['products']
                if system_settings['mode'] == 'Recovery':
                    do_data_sync = False
                    schemas_db_sync  = []
                    schemas_db_dump  = ['products','analysis']

            if system_settings['role'] == 'PC3':

                if system_settings['mode'] == 'Nominal':
                    do_data_sync = False
                    schemas_db_sync   = ['analysis']
                    schemas_db_dump  = ['analysis']
                if system_settings['mode'] == 'Recovery':
                    do_data_sync = False
                    schemas_db_sync  = []
                    schemas_db_dump  = ['products','analysis']

        if system_settings['type_installation'] == 'SinglePC':
            do_data_sync = False
            do_db_sync   = []
            schemas_db_dump  = ['products','analysis']

        # Check for additional conditions (time delays, locks, connections) for each of the operations.
        # Data sync
        operation = 'data_sync'
        if do_data_sync:
            check_time = check_delay_time(operation,delay_minutes=delay_data_sync_minutes)
            if check_time:
                data_source='local_disk'
                data_target='remote_disk'
                system_data_sync(data_source, data_target)

        # DB sync
        operation = 'db_sync'
        if len(schemas_db_sync) > 0:
            check_time = check_delay_time(operation,delay_minutes=delay_db_sync_minutes)
            if check_time:
                data_source='local_db'
                data_target='remote_db'
                system_data_sync(data_source, data_target, schemas_db_sync)

        # DB dump
        operation = 'db_dump'
        if len(schemas_db_dump) > 0:
            check_time = check_delay_time(operation,time=time_for_db_dump)
            if check_time:
                system_db_dump(schemas_db_sync)


class SystemDaemon(DaemonDryRunnable):
    def run(self):
        loop_system(dry_run=self.dry_run)

