_author__ = "Marco Clerici"
#
#	purpose: Define the system service
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 26.05.2015
#   descr:	 Manage all background operations (db and data sync, check status, db dump)
#	history: 1.0
#

# source eStation2 base definitions
import os, re, subprocess
import shutil
import urllib2

# import standard modules
import time, datetime

# import eStation2 modules
from lib.python import functions
from lib.python import es_logging as log
from config import es_constants
from apps.acquisition import acquisition
from apps.processing import processing

logger = log.my_logger(__name__)
data_dir= es_constants.es2globals['data_dir']

from lib.python.daemon import DaemonDryRunnable

def system_status_filename():

    functions.check_output_dir(es_constants.es2globals['status_system_dir'])
    pickle_filename = es_constants.es2globals['status_system_pickle']
    return pickle_filename

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

def save_status_local_machine():

#   Save a pickle containing info on the status of the local machine
#
    logger.debug("Entering routine %s" % 'save_status_local_machine')

    # Define .pck filename
    pickle_filename=system_status_filename()

    # Get status of get_eumetcast
    pid_file = es_constants.get_eumetcast_pid_filename
    daemon = acquisition.GetEumetcastDaemon(pid_file, dry_run=1)
    get_eumetcast_status = daemon.status()

    # Get status of get_internet
    pid_file = es_constants.get_internet_pid_filename
    daemon = acquisition.GetInternetDaemon(pid_file, dry_run=1)
    get_internet_status = daemon.status()

    # Get status of ingestion
    pid_file = es_constants.ingestion_pid_filename
    daemon = acquisition.IngestionDaemon(pid_file, dry_run=1)
    ingestion_status = daemon.status()

    # Get status of processing
    pid_file = es_constants.processing_pid_filename
    daemon = processing.ProcessingDaemon(pid_file, dry_run=1)
    processing_status = daemon.status()

    # Get status of postgresql
    command=['/etc/init.d/postgresql','status']
    p = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err=p.communicate()
    if re.search('online', out):
        psql_online=True
    else:
        psql_online=False
    # Get internet connection
    internet_status=internet_on()

    # Use rsync.py module
    status_local_machine = {'get_eumetcast_status':get_eumetcast_status,
                            'get_internet_status': get_internet_status,
                            'ingestion_status': ingestion_status,
                            'processing_status': processing_status,
                            'system_execution_time':datetime.datetime.now(),
                            'postgresql_status': psql_online,
                            'internet_connection_status': internet_status,
                            'disk_status': True}
    # Save to pickle
    functions.dump_obj_to_pickle(status_local_machine,pickle_filename)
    return 0

def system_data_sync(source, target):

#   Synchronize data directory from one machine to another (push)
#   It is based on rsync daemon, the correct module should be set in /etc/rsyncd.conf file
#   The rsync daemon should running (permission set in /etc/default/rsync)

    logger.debug("Entering routine %s" % 'system_data_sync')
    command = 'rsync -CavK '+source+' '+target
    logger.debug("Executing %s" % command)
    status = os.system(command)
    if status:
        logger.error("Error in executing %s" % command)

def system_db_sync(list_syncs):

#   Synchronize database contents from one instance to another (push)
#   It checks that: bucardo is installed and running
#                   the list of provided rsync are activated
#                   all other rsyncs are deactivated

    logger.debug("Entering routine %s" % 'system_db_sync')

    # Check that bucardo is running
    command=['bucardo','status']
    p = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err=p.communicate()
    if not re.search('PID',out):
        logger.error("Bucardo is not running - DB sync not possible")
        return 1

    # Get list of active rsyncs
    command=['bucardo','list','sync']
    p = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err=p.communicate()

    list_active_syncs=[]
    # Active rsync are identified as: Sync "sync_pc2_analysis"  Relgroup "rel_analysis"        [Active]
    for line in out.split('\n'):
        found=re.match('Sync\s*\"(.+?)\".*\[Active\]',line)
        if found:
            list_active_syncs.append(found.group(1))

    # Activate the list of passed syncs (if any)
    if len(list_syncs) > 0:
        for sync in list_syncs:
            if sync not in list_active_syncs:
                logger.info("Activating bucardo sync: %s" % sync)
                command=['bucardo','activate',sync]
                p = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                out, err=p.communicate()

                # Check error

    # De-activate the active rsync, not in the passed list
    if len(list_active_syncs) > 0:
        for sync in list_active_syncs:
            if sync not in list_syncs:
                logger.info("De-activating bucardo sync: %s" % sync)
                command=['bucardo','deactivate',sync]
                p = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                out, err=p.communicate()
                # Check error


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
        info = functions.load_obj_from_pickle(operations_info_file)
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

def loop_system(dry_run=False):

#    Driver of the system service
#    Reads configuration from the system setting file (system_settings.ini)
#    Perform the needed operations, according to the machine role/mode
#    Arguments: dry_run -> if > 0, only report what has to be done (no actions)
#                       -> if = 0, do operations (default)

    logger.info("Entering routine %s" % 'loop_system')

    # Specific settings for the system operations
    delay_data_sync_minutes = es_constants.es2globals['system_delay_data_sync_min']
    delay_db_sync_minutes = es_constants.es2globals['system_delay_db_sync_min']
    time_for_db_dump = es_constants.es2globals['system_time_db_dump_hhmm']

    # Loop to manage the 'cron-like' operations, i.e.:
    #   a. Data sync
    #   b. DB sync
    #   c. DB dump
    #   d. Save system status

    while True :

        # Read the relevant info from system settings
        system_settings = functions.getSystemSettings()

        # Initialize todo flags
        do_data_sync = False
        schemas_db_sync  = []
        schemas_db_dump  = []

        # Implement the logic of operations based on type/role/mode
        if system_settings['type_installation'] == 'Full':
            if system_settings['role'] == 'PC2':
                ip_target = system_settings['ip_pc3']
                if system_settings['mode'] == 'nominal':
                    do_data_sync = True
                    schemas_db_sync  = ['products']
                    schemas_db_dump  = ['products']

                if system_settings['mode'] == 'recovery':
                    do_data_sync = False
                    schemas_db_sync = []
                    schemas_db_dump = ['products','analysis']

            if system_settings['role'] == 'PC3':

                ip_target = system_settings['ip_pc2']
                if system_settings['mode'] == 'nominal':
                    do_data_sync = False
                    schemas_db_sync = ['analysis']
                    schemas_db_dump = ['analysis']
                if system_settings['mode'] == 'recovery':
                    do_data_sync = False
                    schemas_db_sync = []
                    schemas_db_dump = ['products','analysis']

        if system_settings['type_installation'] == 'SinglePC':
            do_data_sync = False
            schemas_db_sync = []
            schemas_db_dump = ['products','analysis']

        # Check for additional conditions (time delays, locks, connections) for each of the operations.
        # Data sync: note that module [products] is now hard-coded (check wrt /etc/rsyncd.conf)

        # do_data_sync = True     # TEMP !!
        operation = 'data_sync'
        if do_data_sync:
            check_time = check_delay_time(operation,delay_minutes=delay_data_sync_minutes)
            if check_time:
                data_source=es_constants.es2globals['processing_dir']
                data_target=ip_target+'::products'+es_constants.es2globals['processing_dir']
                system_data_sync(data_source, data_target)

        # DB sync
        operation = 'db_sync'
        if len(schemas_db_sync) > 0:
            check_time = check_delay_time(operation,delay_minutes=delay_db_sync_minutes)
            if check_time:
                # Build the list of rsyncs to be activated
                list_rsyncs=[]
                for schema in schemas_db_sync:
                    new_sync='sync_'+system_settings['role'].lower()+'_'+schema
                    list_rsyncs.append(new_sync)
                # Call the function
                system_db_sync(list_rsyncs)

        # DB dump
        operation = 'db_dump'
        if len(schemas_db_dump) > 0:
            check_time = check_delay_time(operation,time=time_for_db_dump)
            if check_time:
                system_db_dump(schemas_db_sync)

        # Save System Status
        operation = 'save_status'

class SystemDaemon(DaemonDryRunnable):
    def run(self):
        loop_system(dry_run=self.dry_run)

