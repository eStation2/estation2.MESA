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

# import standard modules
import time, datetime
import tempfile
import glob
import tarfile

# import eStation2 modules
from lib.python import functions
from lib.python import es_logging as log
from config import es_constants
from apps.acquisition import acquisition
from apps.processing import processing
from apps.es2system import convert_2_spirits as conv

logger = log.my_logger(__name__)
data_dir = es_constants.es2globals['data_dir']

from lib.python.daemon import DaemonDryRunnable

# def get_status_local_machine():
# #   Get info on the status of the local machine
# #
#     logger.debug("Entering routine %s" % 'get_status_local_machine')
#
#     # Get the local systems settings
#     systemsettings = functions.getSystemSettings()
#
#     # Get status of all services
#     status_services = functions.getStatusAllServices()
#
#     get_eumetcast_status = status_services['eumetcast']
#     get_internet_status = status_services['internet']
#     ingestion_status = status_services['ingest']
#     processing_status = status_services['process']
#     system_status = status_services['system']
#
#     # Get status of postgresql
#     psql_status = functions.getStatusPostgreSQL()
#
#     # Get internet connection
#     internet_status = functions.internet_on()
#
#     # ToDo: check disk status!
#
#     status_local_machine = {'get_eumetcast_status': get_eumetcast_status,
#                             'get_internet_status': get_internet_status,
#                             'ingestion_status': ingestion_status,
#                             'processing_status': processing_status,
#                             'system_status': system_status,
#                             'system_execution_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                             'postgresql_status': str(psql_status).lower(),
#                             'internet_connection_status': str(internet_status).lower(),
#                             'active_version': systemsettings['active_version'],
#                             'mode': systemsettings['mode'],
#                             'disk_status': 'true'}
#     return status_local_machine
#
#
# def save_status_local_machine():
# #   Save a pickle containing info on the status of the local machine
# #
#     logger.debug("Entering routine %s" % 'save_status_local_machine')
#
#     # Define .pck filename
#     pickle_filename = functions.system_status_filename()
#
#     # Get the local systems settings
#     systemsettings = functions.getSystemSettings()
#
#     # Get status of all services
#     status_services = functions.getStatusAllServices()
#
#     get_eumetcast_status = status_services['eumetcast']
#     get_internet_status = status_services['internet']
#     ingestion_status = status_services['ingest']
#     processing_status = status_services['process']
#     system_status = status_services['system']
#
#     # Get status of postgresql
#     psql_status = functions.getStatusPostgreSQL()
#
#     # Get internet connection
#     internet_status = functions.internet_on()
#
#     # ToDo: check disk status!
#
#     status_local_machine = {'get_eumetcast_status': get_eumetcast_status,
#                             'get_internet_status': get_internet_status,
#                             'ingestion_status': ingestion_status,
#                             'processing_status': processing_status,
#                             'system_status': system_status,
#                             'system_execution_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                             'postgresql_status': str(psql_status).lower(),
#                             'internet_connection_status': str(internet_status).lower(),
#                             'active_version': systemsettings['active_version'],
#                             'mode': systemsettings['mode'],
#                             'disk_status': 'true'}
#     # Save to pickle
#     functions.dump_obj_to_pickle(status_local_machine, pickle_filename)
#     return 0
#

def system_data_sync(source, target):
#   Synchronize data directory from one machine to another (push)
#   It is based on rsync daemon, the correct module should be set in /etc/rsyncd.conf file
#   The rsync daemon should running (permission set in /etc/default/rsync)

    logfile=es_constants.es2globals['log_dir']+'rsync.log'
    message=time.strftime("%Y-%m-%d %H:%M")+' INFO: Running the data sync now ... \n'
    log_id=open(logfile,'w')
    log_id.write(message)
    log_id.close()
    logger.debug("Entering routine %s" % 'system_data_sync')
    command = 'rsync -CavK '+source+' '+target+ ' >> '+logfile
    logger.debug("Executing %s" % command)
    return
    status = os.system(command)
    if status:
        logger.error("Error in executing %s" % command)
    else:
        return status

def system_db_sync(list_syncs):
#   Synchronize database contents from one instance to another (push)
#   It checks that: bucardo is installed and running
#                   the list of provided rsync are activated
#                   all other rsyncs are deactivated

    logger.debug("Entering routine %s" % 'system_db_sync')

    # Check that bucardo is running
    command = ['bucardo','status']
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if not re.search('PID', out):
        logger.error("Bucardo is not running - DB sync not possible")
        return 1

    # Get list of active rsyncs
    command = ['bucardo', 'list', 'sync']
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    list_active_syncs = []
    # Active rsync are identified as: Sync "sync_pc2_analysis"  Relgroup "rel_analysis"        [Active]
    for line in out.split('\n'):
        found=re.match('Sync\s*\"(.+?)\".*\[Active\]', line)
        if found:
            list_active_syncs.append(found.group(1))

    # Activate the list of passed syncs (if any)
    if len(list_syncs) > 0:
        for sync in list_syncs:
            if sync not in list_active_syncs:
                logger.info("Activating bucardo sync: %s" % sync)
                command = ['bucardo', 'activate', sync]
                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                logger.info("Activating bucardo sync returned: %s" % out)
                # Check error
                if err:
                    logger.warning('Bucardo activation returned err: %s' % err)
                time.sleep(0.5)
    # De-activate the active rsync, not in the passed list
    if len(list_active_syncs) > 0:
        for sync in list_active_syncs:
            if sync not in list_syncs:
                logger.info("De-activating bucardo sync: %s" % sync)
                command = ['bucardo', 'deactivate', sync]
                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err=p.communicate()
                logger.info("De-activating bucardo sync returned: %s" % out)
                # Check error
                if err:
                    logger.warning('Bucardo de-activation returned err: %s' % err)

def system_db_sync_full(pc_role):

#   Manage the transition from Recovery to Nominal, by forcing a full sync of both DB schemas
#   pc_role:    role of my PC (either PC2 or PC3)


    logger.debug("Entering routine %s" % 'system_db_sync_full')

    dump_dir=es_constants.es2globals['db_dump_dir']

    dump_filename=dump_dir+'/dump_data_all_'+datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+'.sql'

    # Create a full dump
    dumpcommand = 'psql -h localhost -p 5432 -U estation -d estationdb -t -A -c "SELECT products.export_all_data()" -o '+\
               dump_filename

    status = os.system(dumpcommand)

    # Wait a second
    time.sleep(1)

    # Check the other computer is ready
    if pc_role == 'PC2':
        other_pc = 'MESA-PC3'
    else:
        other_pc = 'MESA-PC2'

    # Inject the data into the DB of the other PC
    sync_command = 'psql -h '+other_pc+' -p 5432 -U estation -d estationdb -f '+dump_filename+\
                   '1>/dev/null 2>/eStation2/log/system_db_sync_full.log'

    status += os.system(sync_command)

    return status

def system_db_dump(list_dump):
#   Dump the database schemas (for backup)

    logger.debug("Entering routine %s" % 'system_db_dump')
    now = datetime.datetime.now()
    # Use db_dump
    dump_dir = es_constants.es2globals['db_dump_dir']
    db_dump = es_constants.es2globals['db_dump_exec']

    if len(list_dump) > 0:
        for dump_schema in list_dump:
            dump_file = dump_dir+os.path.sep+'estationdb_'+dump_schema+'_'+now.strftime("%Y-%m-%d-%H:%M:%S")+'.sql'
            command = db_dump+ ' -i '+  \
                     ' -h localhost '+\
                     ' -U estation ' +\
                     ' -F p -a --column-inserts ' +\
                     ' -f '+dump_file+ \
                     ' -n '+dump_schema+' estationdb'

            logger.info('Command is: %s' % command)
            status =+ os.system(command)

        return status

def keep_one_for_month(yymm_date, date_list, remove_list, mode='1perM'):

    month_list = []
    # Create the list of files for that yyyy.mm
    # Keep only one file per month
    for my_date in date_list:
        if my_date.month == yymm_date.month and my_date.year == yymm_date.year:
            month_list.append(my_date)
    month_list = sorted(month_list)

    if mode == '1perM':
        # Sort the list, and keep only the last file
        if len(month_list) > 1:
            for mm in month_list[:-1]:
                remove_list.append(mm)
        else:
            pass
    elif mode == '3files':
        # Keep only 3 files: first and last two
        if len(month_list) > 3:
            for mm in month_list[1:-2]:
                remove_list.append(mm)

    return remove_list

def system_manage_dumps():
#   Manage the dump files (house-keeping)

    status = 0

    logger.debug("Entering routine %s" % 'system_manage_dumps')

    for schema in ('products','analysis'):

        # Initialize lists
        date_list = []
        yyyymm_list = []
        remove_list = []

        # Get a list of the existing dump files
        dump_dir = es_constants.es2globals['db_dump_dir']
        existing_dumps = glob.glob(dump_dir+os.path.sep+'estationdb_'+schema+'_*')

        # Extract list of ALL dates, and yyyymm dates (1 per month)
        for file_full in existing_dumps:
            file=os.path.basename(file_full)
            date_list.append(datetime.date(int(file.split('_')[2].split('-')[0]),int(file.split('_')[2].split('-')[1]),int(file.split('_')[2].split('-')[2])))
            yyyymm_list.append(datetime.date(int(file.split('_')[2].split('-')[0]),int(file.split('_')[2].split('-')[1]),1))

        # Sort month list
        yyyymm_list=set(yyyymm_list)
        yyyymm_list=sorted(list(yyyymm_list))

        today = datetime.date.today()

        # Loop over all months, and build the list of files to be deleted
        for yymm_date in yyyymm_list:

            # For all months but current, keep only 1 files
            if today.month != yymm_date.month or today.year != yymm_date.year:
                remove_list = keep_one_for_month(yymm_date,date_list, remove_list)
                logger.debug('Remove list length %i: ' % len(remove_list))
            else:
                # For the current month
                remove_list = keep_one_for_month(yymm_date,date_list, remove_list, mode='3files')
                logger.debug('Remove list length %i: ' % len(remove_list))

        # Remove files strftime('We are the %d, %b %Y')
        for deldate in remove_list:
            date_string = deldate.strftime('%Y-%m-%d')
            delfiles = glob.glob(dump_dir+os.path.sep+'estationdb_'+schema+'_'+date_string+'*')
            try:
                for delfile in delfiles:
                    os.remove(delfile)
                    logger.info('Deleted file %s' % delfile)
            except:
                logger.error('Error in deleting file %s' % delfile)
                status = 1
    # Exit
    return status

def system_bucardo_config():
#   Check if bucardo has been already configured, and if there are conditions to do so

    res_bucardo_config = 0

    logger.debug("Entering routine %s" % 'system_bucardo_config')

    # Returns 0 if no any sync exists
    res_list_sync=os.system('bucardo list sync | grep "No syncs found" 1>/dev/null')

    # If no any sync exists, bucardo still to be configured
    if not res_list_sync:

        # Get relevant variables
        sysSettings = functions.getSystemSettings()
        role = sysSettings['role']

        # Check the other computer is ready
        if role == 'PC2':
            other_pc = 'MESA-PC3'
        else:
            other_pc = 'MESA-PC2'

        command = '/usr/pgsql-9.3/bin/pg_isready -h '+other_pc
        other_pc_not_ready = os.system(command)

        if not other_pc_not_ready:

            # Execute the configuration
            command = '/var/www/eStation2/config/install/bucardo_config.sh '+ role.lower() +\
                      ' 1>/var/log/bucardo/bucardo_config.log'+ ' 2>/var/log/bucardo/bucardo_config.err'

            res_bucardo_config=os.system(command)
        else:
            logger.error('The other computer '+other_pc+' is not ready. Exit.')

    # Exit
    return res_bucardo_config

def system_create_report(target_file=None):
#   Create a .zip file with the relevant information to be sent as for diagnostic
#

    # Dump the database schemas (for backup)
    logger.debug("Entering routine %s" % 'system_create_report')
    now = datetime.datetime.now()

    # Use a module (to be identified) for dump
    target_dir = es_constants.es2globals['status_system_dir']+os.path.sep

    output_filename = target_dir+'System_report_'+now.strftime("%Y-%m-%d-%H:%M:%S")+'.tgz'

    # Define List of files to be copied
    report_files= ["/eStation2/log/*",                          # All log files
                   "/eStation2/system/system_status.pkl",       # System Status pickle
                   "/eStation2/get_lists/get_eumetcast/*",      # All get lists
                   "/eStation2/get_lists/get_internet/*",       # All get lists
                   "/eStation2/settings/*",                     # Machine settings (User+System)
                  # "/eStation2/db_dump/*",                     # All dumps -> only latest
                   "/etc/passwd",                               # Users
                   "/etc/hosts",                                # Hosts
                   "/var/log/eStation2/eStation-Apps_*.log",    # All eStation .deb installation files
                  # "/etc/postgresql/9.3/main/pg_hba.conf",     # No permissions !!
                   "/etc/apache2/sites-available/000-default.conf",
                   "/usr/local/lib/python2.7/dist-packages/eStation2.pth",
                   "/etc/default/rsync",
                   "/etc/rsyncd.conf"]

    # Create a temp directory
    try:
        tmp_dir = tempfile.mkdtemp(prefix=__name__+'_', suffix='_' + 'system_report',
                                   dir=es_constants.base_tmp_dir)
    except IOError:
        logger.error('Cannot create temporary dir ' + es_constants.base_tmp_dir + '. Exit')
        return 1

    # Copy all files there
    for my_item in report_files:
        all_files = glob.glob(my_item)
        for element in all_files:
            if os.path.isfile(element):
                if not os.path.isdir(tmp_dir+os.path.dirname(element)):
                    os.makedirs(tmp_dir+os.path.dirname(element))
                shutil.copy(element, tmp_dir+os.path.dirname(element))
            else:
                logger.warning('Will not copy dir ' + element + '. Continue')

    # Create the .tgz and move to target dir
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(tmp_dir, arcname=os.path.basename(tmp_dir))
    tar.close()

    # Remove temporary dir
    shutil.rmtree(tmp_dir)


def check_delay_time(operation, delay_minutes=None, time=None, write=False):
#
# For a given operation, check if the delay has passed, or if it is time to execute it
#
# Input arguments: operation= is one of the foreseen operations ('sync_data', 'sync_db')
#                  delay= is the delay - in minutes - between two executions
#                  time= is the time (hh:mm) of the day for the execution
#
#                  write: if set, does write the ,info file
#
    logger.debug("Entering routine %s" % 'check_delay_time')

    to_be_executed = False
    dir_info = es_constants.pid_file_dir
    operations_info_file = dir_info+os.path.sep+operation+'_execution.info'

    # If write option set, write the info and exit
    if write:
        info = {'latest_exec_time': datetime.datetime.now()}
        functions.dump_obj_to_pickle(info, operations_info_file)

    # Distinguish between delay/time
    if delay_minutes is not None:

        # Read info from the pickle object
        info = functions.load_obj_from_pickle(operations_info_file)
        if info is None:
            logger.debug("Operation %s not yet executed: execute it." % operation)
            to_be_executed = True
        else:
            time_latest_execution = info['latest_exec_time']
            current_delta=datetime.datetime.now()-time_latest_execution
            current_delta_minutes = int(current_delta.seconds/60)
            if current_delta_minutes > float(delay_minutes):
               to_be_executed = True

    elif time is not None:
        now = datetime.datetime.now()
        if now.minute == int(time[3:5]) and now.minute == int(time[3:5]):
            to_be_executed = True
    else:
        logger.warning("Either delay_minutes or time has to be defined!")

    return to_be_executed


def system_manage_lock(lock_id, action):
#
# Manage the lock file for an action
#
# lock_id is whatever string (but 'All_locks' which is reserved)
#
# action can be: check  -> check if it exist
#                   create -> write the file
#                   delete -> remove the file

    logger.debug("Entering routine %s" % 'system_manage_lock')
    # Get variables
    dir_lock = es_constants.pid_file_dir
    status = 0

    if lock_id == 'All_locks':
        if action == 'Delete':
            for f in os.listdir(dir_lock):
                if re.search('action*.lock', f):
                    status = os.remove(os.path.join(dir_lock,f))
        else:
            logger.warning("Only delete action is defined for all locks")
    else:
        lock_file = dir_lock+os.path.sep+'action_'+lock_id+'.lock'
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
            with open(lock_file, 'a'):
                os.utime(lock_file, None)
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
    time_for_db_dump = es_constants.es2globals['system_time_db_dump_hhmm']
    time_for_spirits_conv = es_constants.es2globals['system_time_spirits_conv']

    # Loop to manage the 'cron-like' operations, i.e.:
    #   a. Data sync
    #   b. DB sync
    #   c. DB dumpd (create/manage)
    #   d. Spirits conversion
    #

    while True:

        # Read the relevant info from system settings
        system_settings = functions.getSystemSettings()

        logger.info('System Settings Mode: %s ' % system_settings['mode'])

        # Initialize To Do flags
        do_data_sync = False
        schemas_db_sync = []
        schemas_db_dump = []
        #do_save_system = True
        do_convert_spirits = False

        logger.info("Starting the System Service loop")

        if system_settings['data_sync'] in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            do_data_sync = True
        else:
            do_data_sync = False

        if system_settings['db_sync'] in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            do_db_sync = True
        else:
            do_db_sync = False

        # Implement the logic of operations based on type/role/mode
        if system_settings['type_installation'] == 'Full':

            if system_settings['role'] == 'PC2':
                ip_target = system_settings['ip_pc3']
                if system_settings['mode'] == 'nominal':
                    schemas_db_sync = ['products']
                    schemas_db_dump = ['products', 'analysis']
                    do_convert_spirits = True

                if system_settings['mode'] == 'recovery':
                    schemas_db_sync = []
                    schemas_db_dump = ['products', 'analysis']
                    do_convert_spirits = True

                if system_settings['mode'] == 'maintenance':
                    schemas_db_sync = []
                    schemas_db_dump = []

            if system_settings['role'] == 'PC3':

                ip_target = system_settings['ip_pc2']
                if system_settings['mode'] == 'nominal':
                    schemas_db_sync = ['analysis']
                    schemas_db_dump = ['products', 'analysis']

                if system_settings['mode'] == 'recovery':
                    schemas_db_sync = []
                    schemas_db_dump = ['products', 'analysis']

                if system_settings['mode'] == 'maintenance':
                    schemas_db_sync = []
                    schemas_db_dump = []

        if system_settings['type_installation'] == 'SinglePC':
            do_data_sync = False
            schemas_db_sync = []
            schemas_db_dump = ['products', 'analysis']

        # Check for additional conditions (time delays, locks, connections) for each of the operations.
        # Data sync: note that module [products] is now hard-coded (check wrt /etc/rsyncd.conf)

        # do_data_sync
        operation = 'data_sync'
        if do_data_sync:
            check_time = check_delay_time(operation, delay_minutes=delay_data_sync_minutes)
            if check_time:
                logger.info("Executing data synchronization")
                data_source = es_constants.es2globals['processing_dir']
                data_target = ip_target+'::products'+es_constants.es2globals['processing_dir']
                system_data_sync(data_source, data_target)
                check_delay_time(operation,delay_minutes=delay_data_sync_minutes, write=True)

        # DB sync: execute every cycle if in system_setting (no delay)
        operation = 'db_sync'
        if len(schemas_db_sync) > 0:
            #check_time = check_delay_time(operation, delay_minutes=delay_db_sync_minutes)
            if do_db_sync:
                logger.info("Executing db synchronization")
                # Build the list of rsyncs to be activated
                list_rsyncs = []
                for schema in schemas_db_sync:
                    new_sync = 'sync_'+system_settings['role'].lower()+'_'+schema
                    list_rsyncs.append(new_sync)
                # Call the function
                system_db_sync(list_rsyncs)
                # check_delay_time(operation, delay_minutes=delay_db_sync_minutes, write=True)

        # De-activate all syncs
        if (len(schemas_db_sync) > 0) or not do_db_sync:
            system_db_sync([])

        # DB dump
        operation = 'db_dump'
        if len(schemas_db_dump) > 0:
            check_time = check_delay_time(operation, time=time_for_db_dump)
            if check_time:
                # Execute the dump of the schemas active on the machine
                logger.info("Executing db dump")
                system_db_dump(schemas_db_sync)

                # Manage the file dumps (rotation)
                logger.info("Executing manage dumps")
                system_manage_dumps()

        # Save System Status
        # operation = 'save_status'
        # if do_save_system:
        #     logger.info("Saving the status of the machine")
        #     save_status_local_machine()

        # Convert to spirits format
        operation = 'convert_spirits'
        if do_convert_spirits:
            check_time = check_delay_time(operation, time=time_for_spirits_conv)
            if check_time:
                logger.info("Saving the status of the machine")
                output_dir = es_constants.es2globals['spirits_output_dir']
                conv.convert_driver(output_dir)

        # Sleep some time
        time.sleep(float(es_constants.es2globals['system_sleep_time_sec']))

class SystemDaemon(DaemonDryRunnable):
    def run(self):
        loop_system(dry_run=self.dry_run)


