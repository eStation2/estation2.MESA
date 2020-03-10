from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.utils import old_div
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
import shutil, string

# import standard modules
import time, datetime
import tempfile
import glob
import tarfile
import shlex
# import eStation2 modules
from lib.python import functions
from lib.python import es_logging as log
from config import es_constants
from apps.tools import ingest_historical_archives as iha
from apps.es2system import convert_2_spirits as conv
from database import querydb
from apps.productmanagement.products import *
from lib.python.daemon import DaemonDryRunnable

logger = log.my_logger(__name__)
data_dir = es_constants.es2globals['processing_dir']


def get_status_local_machine():
    #   Get info on the status of the local machine
    #

    logger.debug("Entering routine %s" % 'get_status_local_machine')

    # Get the local systems settings
    systemsettings = functions.getSystemSettings()

    # Get status of all services
    status_services = functions.getStatusAllServices()

    get_eumetcast_status = status_services['eumetcast']
    get_internet_status = status_services['internet']
    ingestion_status = status_services['ingest']
    processing_status = status_services['process']
    system_status = status_services['system']

    # Get status of postgresql
    psql_status = functions.getStatusPostgreSQL()

    # Get internet connection
    internet_status = functions.internet_on()

    # ToDo: check disk status!

    status_local_machine = {'get_eumetcast_status': get_eumetcast_status,
                            'get_internet_status': get_internet_status,
                            'ingestion_status': ingestion_status,
                            'processing_status': processing_status,
                            'system_status': system_status,
                            'system_execution_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'postgresql_status': str(psql_status).lower(),
                            'internet_connection_status': str(internet_status).lower(),
                            'active_version': systemsettings['active_version'],
                            'mode': systemsettings['mode'],
                            'disk_status': 'true'}
    return status_local_machine


def save_status_local_machine():
    #   Save a text file containing the status of the local machine
    #

    logger.debug("Entering routine %s " % 'save_status_local_machine')

    # Define .txt filename
    status_system_file=es_constants.es2globals['status_system_file']

    # Get status of all services
    machine_status = get_status_local_machine()

    # Write to file
    fid = open(status_system_file,'w')
    for value in machine_status:
        fid.write('%s = %s \n' % (value, machine_status[value]))
    fid.close()

    return 0


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
    # return
    status = os.system(command)
    if status:
        logger.error("Error in executing %s" % command)
    else:
        return status


def system_bucardo_service(action):
    #   Synchronize database contents from one instance to another (push)
    #   It checks the status of bucardo and updates it according to the required action

    logger.debug("Entering routine %s" % 'system_bucardo_service')

    # Check that bucardo is running
    command = ['bucardo','status']
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    status_on = re.search('PID', out)

    if action == 'start':
        if status_on:
            logger.info('Bucardo already running. Continue')
        else:
            command = ['bucardo','start']
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            logger.info('Bucardo start message: %s' % err)
    if action == 'stop':
        if not status_on:
            logger.info('Bucardo already stopped. Continue')
        else:
            command = ['bucardo','stop']
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()

    # Wait 3 seconds
    time.sleep(3)

    # Check the final status
    command = ['bucardo','status']
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    status_on = re.search('PID', out)

    if action == 'start':
        if status_on:
            logger.info('Bucardo is properly running.')
        else:
            logger.warning('Error in starting Bucardo.')

    if action == 'stop':
        if not status_on:
            logger.info('Bucardo is properly stopped.')
        else:
            logger.warning('Error in stopping Bucardo.')


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
                   ' 1>/dev/null 2>/eStation2/log/system_db_sync_full.log'

    status += os.system(sync_command)

    return status


def system_db_dump(list_dump):
    #   Dump the database schemas (for backup)

    logger.debug("Entering routine %s" % 'system_db_dump')
    now = datetime.datetime.now()
    # Use db_dump
    dump_dir = es_constants.es2globals['db_dump_dir']
    db_dump = es_constants.es2globals['db_dump_exec']
    status = False
    if len(list_dump) > 0:
        for dump_schema in list_dump:

            # Check if there is one dump for the current day
            # See Tuleap Ticket #10905 (VGF-MOI-wk1)
            dump_dir = es_constants.es2globals['db_dump_dir']
            existing_dumps = glob.glob(dump_dir + os.path.sep + 'estationdb_' + dump_schema + '_*')
            match_name = '.*estationdb_'+dump_schema+'_'+now.strftime("%Y-%m-%d-")+'.*.sql'
            matches = [ s for s in existing_dumps if re.match(match_name,s)]
            if len(matches) == 0:
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

            # Restart bucardo
            command = 'bucardo restart'
            res_bucardo_config+=os.system(command)

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

    # Create a temp directory
    try:
        tmp_dir = tempfile.mkdtemp(prefix=__name__+'_', suffix='_' + 'system_report',
                                   dir=es_constants.base_tmp_dir)
    except IOError:
        logger.error('Cannot create temporary dir ' + es_constants.base_tmp_dir + '. Exit')
        return 1

    # Use a module (to be identified) for dump
    #target_dir = es_constants.es2globals['status_system_dir']+os.path.sep
    target_dir=tmp_dir
    output_filename = target_dir+os.path.sep+'System_report_'+now.strftime("%Y-%m-%d-%H:%M:%S")+'.tgz'

    # Define List of files to be copied
    report_files= ["/eStation2/log/*",                                  # All log files
                   "/eStation2/get_lists/get_eumetcast/*",              # All get lists
                   "/eStation2/get_lists/get_internet/*",               # All get lists
                   "/eStation2/settings/*",                             # Machine settings (User+System)
                   "/eStation2/system/system_status.txt",               # System status
                   "/etc/passwd",                                       # Users
                   "/etc/hosts",                                        # Hosts
                   "/var/log/eStation2/eStation-Apps_*.log",            # All eStation .deb installation files
                   "/var/lib/pgsql/9.3/data/pg_hba.conf",               # Postgresql config
                   "/var/lib/pgsql/9.3/data/postgresql.conf",           # Postgresql config
                   "/usr/local/src/tas/eStation_wsgi_srv/httpd.conf",
                   "/usr/local/src/tas/anaconda/lib/python2.7/site-packages/eStation.pth",
                   "/etc/rsyncd.conf"]

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

    return output_filename


def system_install_report(target_file=None):
    #   Create a .zip file with the relevant information on the system installation
    #

    # Dump the database schemas (for backup)
    logger.debug("Entering routine %s" % 'system_install_report')
    now = datetime.datetime.now()

    # Create a temp directory
    try:
        tmp_dir = tempfile.mkdtemp(prefix=__name__+'_', suffix='_' + 'install_report',
                                   dir=es_constants.base_tmp_dir)
    except IOError:
        logger.error('Cannot create temporary dir ' + es_constants.base_tmp_dir + '. Exit')
        return 1

    # Use a module (to be identified) for dump
    target_dir = tmp_dir+os.path.sep
    logger.info(target_dir)

    output_filename = target_dir+'Install_report_'+now.strftime("%Y-%m-%d-%H:%M:%S")+'.tgz'

    # Create some tmp files
    cmd = 'rpm -qa | grep -v eStation > '+tmp_dir+os.path.sep+'List_list_noEstation.txt'
    status = os.system(cmd)
    cmd = 'rpm -qa | grep  eStation > '+tmp_dir+os.path.sep+'List_list_Estation.txt'
    status = os.system(cmd)
    cmd = ['pip','freeze']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    pipf = open(tmp_dir+os.path.sep+'List_pip_freeze.txt','w')
    for value in out:
        pipf.write(value)
    pipf.close()


    # Define List of files to be copied
    report_files= [tmp_dir+os.path.sep+"List_list_noEstation.txt",   # All yum module installed, but eStation
                   tmp_dir+os.path.sep+"List_list_Estation.txt",     # All eStation module installed
                   tmp_dir+os.path.sep+"List_pip_freeze.txt"]        # All pip module


    # # Copy all files there -> Not needed: files already there
    # for my_item in report_files:
    #     all_files = glob.glob(my_item)
    #     for element in all_files:
    #         if os.path.isfile(element):
    #             if not os.path.isdir(tmp_dir+os.path.dirname(element)):
    #                 os.makedirs(tmp_dir+os.path.dirname(element))
    #             shutil.copy(element, tmp_dir+os.path.dirname(element))
    #         else:
    #             logger.warning('Will not copy dir ' + element + '. Continue')

    # Create the .tgz and move to target dir
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(tmp_dir, arcname=os.path.basename(tmp_dir))
    tar.close()

    return output_filename


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
            current_delta_minutes = int(old_div(current_delta.seconds,60))
            if current_delta_minutes > float(delay_minutes):
               to_be_executed = True

    elif time is not None:
        # Time to indicate
        if time == '99:99':
            to_be_executed = True
        else:
            now = datetime.datetime.now()
            if now.hour == int(time[0:2]) and now.minute == int(time[3:5]):
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


def clean_temp_dir():
    #
    # Look into /eStation2/tmp directory and delete directories older than 3 days
    #
    #
    logger.debug("Entering routine %s" % 'clean_temp_dir')

    now = time.time()

    for f in glob.glob(es_constants.es2globals['base_tmp_dir']+os.path.sep+'apps.*'):
        try:
            if os.stat(f).st_mtime < now - 3 * 86400:
                if os.path.isdir(f):
                    logger.info('Deleting directory: %s' % f)
                    shutil.rmtree(f)
        except:
            logger.warning('A directory was deleted by system: %s' % f)
    return 0


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

    try:
        time_for_push_ftp = es_constants.es2globals['system_time_push_ftp']
    except:
        logger.info("Parameter not defined in factory_settings: %s" % 'system_time_push_ftp')
        time_for_push_ftp = '24:01'

    do_bucardo_config = False

    # Restart bucardo
    command = 'bucardo restart'
    res_bucardo_restart=os.system(command)
    if res_bucardo_restart:
        logger.warning("Error in restarting bucardo")
    else:
        logger.info("Bucardo restarted correctly")

    # Loop to manage the 'cron-like' operations, i.e.:

    #   0. Check bucardo config	
    #   a. Data sync (not anymore, done by TPZF)
    #   b. DB sync: bucardo
    #   c. DB dump (create/manage)
    #   d. Spirits conversion
    #   e. Clean Temporary directory

    execute_loop = True
    while execute_loop:

        logger.info("")
        logger.info("Entering the System Service loop")

        # Read the relevant info from system settings
        system_settings = functions.getSystemSettings()
        logger.debug('System Settings Mode: %s ' % system_settings['mode'])

        # Initialize To Do flags
        do_data_sync = False
        schemas_db_sync = []
        schemas_db_dump = []
        do_convert_spirits = False
        do_clean_tmp= True
        do_push_ftp = False

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

            do_bucardo_config = True
            if system_settings['role'] == 'PC2':
                status_otherPC = functions.get_remote_system_status('mesa-pc3')
                if len(status_otherPC) != 0:
                    mode_otherPC = status_otherPC['mode']
                else:
                    mode_otherPC = 'unreachable'

                # ip_target = system_settings['ip_pc3']
                if system_settings['mode'] == 'nominal':
                    if mode_otherPC == 'recovery':
                        do_data_sync = False
                        logger.info("Do not do data_sync because other PC is in Recovery Mode")
                    elif mode_otherPC == 'unreachable':
                        do_data_sync = False
                        logger.info("Do not do data_sync because other PC is not reachable")

                    schemas_db_sync = ['products']
                    schemas_db_dump = ['products', 'analysis']
                    do_convert_spirits = True
                    bucardo_action = 'start'

                if system_settings['mode'] == 'recovery':
                    schemas_db_sync = []
                    schemas_db_dump = ['products', 'analysis']
                    do_convert_spirits = True
                    bucardo_action = 'stop'

                if system_settings['mode'] == 'maintenance':
                    schemas_db_sync = []
                    schemas_db_dump = []
                    bucardo_action = 'stop'

            if system_settings['role'] == 'PC3':
                status_otherPC = functions.get_remote_system_status('mesa-pc2')

                if len(status_otherPC) != 0:
                    mode_otherPC = status_otherPC['mode']
                else:
                    mode_otherPC = 'unreachable'

                # ip_target = system_settings['ip_pc2']
                if system_settings['mode'] == 'nominal':
                    if mode_otherPC == 'recovery':
                        do_data_sync = False
                        logger.info("Do not do data_sync because other PC is in Recovery Mode")
                    elif mode_otherPC == 'unreachable':
                        do_data_sync = False
                        logger.info("Do not do data_sync because other PC is not reachable")

                    schemas_db_sync = ['analysis']
                    schemas_db_dump = ['products', 'analysis']
                    bucardo_action = 'start'

                if system_settings['mode'] == 'recovery':
                    schemas_db_sync = []
                    schemas_db_dump = ['products', 'analysis']
                    bucardo_action = 'stop'

                if system_settings['mode'] == 'maintenance':
                    schemas_db_sync = []
                    schemas_db_dump = []
                    bucardo_action = 'stop'

        if system_settings['type_installation'] == 'SinglePC':
            do_data_sync = False
            schemas_db_sync = []
            schemas_db_dump = ['products', 'analysis']

        if system_settings['type_installation'] == 'Server':
            do_data_sync = False
            do_db_sync = False
            schemas_db_sync = []
            schemas_db_dump = ['products', 'analysis']
            do_convert_spirits = False
            do_push_ftp = True

        if es_constants.es2globals['do_spirits_conversion'] in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            do_convert_spirits = True

        # Report on the actions to be done
        logger.info("")
        logger.info("*   Schedule follows ")
        logger.info("*   Do bucardo config:  " + str(do_bucardo_config))
        logger.info("*   Do data-sync:       " + str(do_data_sync))
        logger.info("*   Do db-sync:         " + str(do_db_sync))
        # logger.info("*   Nr schema to dump:  " + str(len(schemas_db_dump)))
        logger.info("*   Do spirits convers: " + str(do_convert_spirits))
        logger.info("*   Do push to ftp:     " + str(do_push_ftp))
        logger.info("")

        # do_bucardo_config
        if do_bucardo_config:
            system_bucardo_config()

        # do_data_sync
        operation = 'data_sync'
        if do_data_sync:
            check_time = check_delay_time(operation, delay_minutes=delay_data_sync_minutes)
            logger.info("check_time: " + str(check_time))
            if check_time:
                logger.info("Executing data synchronization")
                data_source = es_constants.es2globals['processing_dir']
                # data_target = ip_target+'::products'+es_constants.es2globals['processing_dir']
                data_target = 'PC3::products'
                system_data_sync(data_source, data_target)
                check_delay_time(operation,delay_minutes=delay_data_sync_minutes, write=True)

        # DB sync: execute every cycle if in system_setting (no delay)
        operation = 'db_sync'
        if len(schemas_db_sync) > 0:
            if do_db_sync:
                logger.info("Executing db synchronization")
                # Call the function
                system_bucardo_service(bucardo_action)

        # DB dump
        operation = 'db_dump'
        if len(schemas_db_dump) > 0:
            check_time = check_delay_time(operation, time=time_for_db_dump)
            if check_time:
                # Execute the dump of the schemas active on the machine - Correct Tuleap #10905
                logger.info("Executing db dump")
                system_db_dump(schemas_db_dump)

                # Manage the file dumps (rotation)
                logger.info("Executing manage dumps")
                system_manage_dumps()

        # Convert to spirits format
        operation = 'convert_spirits'
        if do_convert_spirits:
            check_time = check_delay_time(operation, time=time_for_spirits_conv)
            if check_time:
                logger.info("Convert to SPIRITS format")
                output_dir = es_constants.es2globals['spirits_output_dir']
                conv.convert_driver(output_dir)

        # Push data to ftp server
        operation = 'push_to_ftp'
        if do_push_ftp:
            check_time = check_delay_time(operation, time=time_for_push_ftp)
            if check_time:
                logger.info("Push data to remote ftp server")
                status = push_data_ftp()

        # Clean temporary directory
        operation = 'clean_temp'
        if do_clean_tmp:
            logger.info("Cleaning Temporary dirs")
            clean_temp_dir()


        # Exit in case of dry_run
        if dry_run:
            execute_loop=False

        # Sleep some time
        time.sleep(float(es_constants.es2globals['system_sleep_time_sec']))


def cmd(acmd):
    try:
        logger.info(acmd)
        logger.info(shlex.split(acmd))
        return subprocess.check_output(shlex.split(acmd))
    except subprocess.CalledProcessError as pe:
        logger.error(pe)
    return None


def get_status_PC1():
    #   Get info on the status of the services on PC1:
    #   DVB
    #   Tellicast
    #   FTS

    status_PC1 = {'dvb_status': -1,
                  'tellicast_status': -1,
                  'fts_status': -1}
    err = ''
    try:
        # Check the final status
        # command = [es_constants.es2globals['apps_dir']+'/tools/test_services_pc1.sh', ' 1>/dev/null' ]
        command = es_constants.es2globals['apps_dir']+'/tools/test_services_pc1.sh'

        #logger.info(command)
        # p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # out, err = p.communicate()
        out = cmd(command)
        logger.info(out)
        tokens=string.split(out)

        logger.info(tokens[0])
        logger.info(tokens[1])
        logger.info(tokens[2])

        dvb_status=string.split(tokens[0],'=')[1]
        tellicast_status=string.split(tokens[1],'=')[1]
        fts_status=string.split(tokens[2],'=')[1]

        logger.info(dvb_status)
        logger.info(tellicast_status)
        logger.info(fts_status)


    except:
        logger.error('Error in checking PC1: %s' % err)
        return status_PC1

    status_PC1 = {'dvb_status': dvb_status,
                  'tellicast_status': tellicast_status,
                  'fts_status': fts_status}

    return status_PC1


def push_data_ftp(dry_run=False, user=None, psw=None, url=None, trg_dir=None, masked=True):
    #   Synchronized data towards an ftp server (only for JRC)
    #   It replaces, since the new srv-ies-ftp.jrc.it ftp is set, the bash script: mirror_to_ftp.sh
    #   Configuration:  it looks at all 'non-masked' products and pushes them
    #                   For the mapsets, find what is in the filesystem, and pushes only the 'largest'
    #   It uses a command like:
    #       lftp -e "mirror -RLe /data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/10dmax-linearx2/
    #                            /narma/eStation_2.0/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/10dmax-linearx2/;exit"
    #                            -u narma:JRCVRw2960 sftp://srv-ies-ftp.jrc.it"" >> /eStation2/log/push_data_ftp.log
    #

    spec_logger = log.my_logger('apps.es2system.push_data_ftp')

    try:
        from config import server_ftp
    except:
        logger.warning('Configuration file for ftp sync not found. Exit')
        return 1

    if user is None:
        user = server_ftp.server['user']
    if psw is None:
        psw  = server_ftp.server['psw']
    if url is None:
        url=server_ftp.server['url']
    if trg_dir is None:
        trg_dir=server_ftp.server['data_dir']

    # Create an ad-hoc file for the lftp command output (beside the standard logger)
    logfile=es_constants.es2globals['log_dir']+'push_data_ftp.log'
    message=time.strftime("%Y-%m-%d %H:%M")+' INFO: Running the ftp sync now ... \n'

    logger.debug("Entering routine %s" % 'push_data_ftp')

    # Loop over 'not-masked' products
    products = querydb.get_products(activated=True)
    # produts=products[21:23]               # test a subset
    for row in products:

        prod_dict = functions.row2dict(row)
        productcode = prod_dict['productcode']
        version = prod_dict['version']

        # TEMP - For testing only
        # if productcode!='vgt-ndvi' or version !='sv2-pv2.2':
        #     continue

        # Check it if is in the list of 'exclusions' defined in ./config/server_ftp.py
        key ='{}/{}'.format(productcode,version)
        skip = False
        if key in server_ftp.exclusions:
            skip = True
            logger.debug('Do not sync for {}/{}'.format(productcode,version))

        p = Product(product_code=productcode, version=version)

        all_prod_mapsets = p.mapsets
        all_prod_subproducts = p.subproducts

        # Check there is at least one mapset and one subproduct
        if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0 and not skip:

            spec_logger.info('Working on product {}/{}'.format(productcode, version))
            # In case of several mapsets, check if there is a 'larger' one
            if len(all_prod_mapsets) > 1:
                mapset_to_use = []
                for my_mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=my_mapset, allrecs=False)
                    if hasattr(mapset_info, "mapsetcode"):
                        my_mapobj = MapSet()
                        my_mapobj.assigndb(my_mapset)

                        larger_mapset = my_mapobj.get_larger_mapset()
                        if larger_mapset is not None:
                            if larger_mapset not in mapset_to_use:
                                mapset_to_use.append(larger_mapset)
                        else:
                            if my_mapset not in mapset_to_use:
                                mapset_to_use.append(my_mapset)
            else:
                mapset_to_use=all_prod_mapsets
            # Loop over existing mapset
            for mapset in mapset_to_use:
                all_mapset_datasets = p.get_subproducts(mapset=mapset)

                # Loop over existing subproducts
                for subproductcode in all_mapset_datasets:
                    # Get info - and ONLY for NOT masked products
                    dataset_info = querydb.get_subproduct(productcode=productcode,
                                                          version=version,
                                                          subproductcode=subproductcode,
                                                          masked=masked)  # -> TRUE means only NOT masked sprods

                    if dataset_info is not None:
                        dataset_dict = functions.row2dict(dataset_info)
                        dataset_dict['mapsetcode'] = mapset

                        logger.debug('Working on {}/{}/{}/{}'.format(productcode,version,mapset,subproductcode))

                        subdir = functions.set_path_sub_directory(productcode, subproductcode,  dataset_dict['product_type'], version, mapset)
                        source = data_dir+subdir
                        target = trg_dir + subdir

                        command = 'lftp -e "mirror -RLe {} {};exit" -u {}:{} {}"" >> {}'.format(source,target,user,psw,url,logfile)
                        # command = 'lftp -e "mirror -RLe {} {};exit" -u {}:{} {}"" >> /dev/null'.format(source,target,user,psw,url)
                        logger.debug("Executing %s" % command)
                        spec_logger.info('Working on mapset/subproduct {}/{} \n'.format(mapset, subproductcode))

                        # return
                        try:
                            status = os.system(command)
                            if status:
                                logger.error("Error in executing %s" % command)
                                spec_logger.error("Error in executing %s" % command)
                        except:
                            logger.error('Error in executing command: {}'.format(command))
                            spec_logger.error('Error in executing command: {}'.format(command))


class SystemDaemon(DaemonDryRunnable):
    def run(self):
        loop_system(dry_run=self.dry_run)


class IngestArchiveDaemon(DaemonDryRunnable):
    def run(self):
        iha.ingest_historical_archives(input_dir=None, dry_run=self.dry_run)


