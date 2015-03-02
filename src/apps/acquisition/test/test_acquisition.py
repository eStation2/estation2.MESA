
import unittest
import os, time
from config import es_constants
from apps.acquisition import acquisition
from lib.python import es_logging as log
logger = log.my_logger(__name__)
#
class TestDaemon(unittest.TestCase):

    #   ---------------------------------------------------------------------------
    #   Test IngestDaemon():
    #   Check the status of the Ingest process:
    #       1. If ON    -> exit with warning
    #       2. If OFF   -> Start in dry_run mode, check status and stop
    #
    #   TODO-M.C.: does the exit(0) in daemon code make the test fail ?
    #   ---------------------------------------------------------------------------
    def TestIngestDaemon(self):

        pid_file = es_constants.ingest_pid_filename
        daemon = acquisition.IngestDaemon(pid_file, dry_run=True)

        # If the daemon is running, do not perform test
        if daemon.status():
            logger.info('Ingest process is running: Exit')
        else:
            logger.info('Ingest process is NOT running: Start it.')
            # here we should catch the 'sys.exit(0)', which otherwise causes nosetest to fail
            # see http://stackoverflow.com/questions/15672151/is-it-possible-for-a-unit-test-to-assert-that-a-method-calls-sys-exit

            with self.assertRaises(SystemExit) as cm:
                daemon.start()
            #self.assertEqual(cm.exception.code, 0)

            time.sleep(1)
            # Check the process has started
            self.assertEqual(daemon.status(), True)
            # Wait 1 second and stop it
            time.sleep(1)
            daemon.stop()
            # Check the process was stopped
            self.assertEqual(daemon.status(), False)

    def TestGetInternetDaemon(self):

        logger.info('Test GetInternet daemon')

        pid_file = es_constants.get_internet_pid_filename
        daemon = acquisition.GetInternetDaemon(pid_file, dry_run=True)

        # If the daemon is running, stop it and check file does not exist
        if os.path.isfile(pid_file):
            logger.info('GetInternet pid file exist: stop daemon')
            try:
                daemon.stop()
            except:
                pass
            self.assertEqual(os.path.isfile(pid_file), 0)
        else:
            logger.info('GetInternet pid file des NOT exist: start daemon')
            try:
                daemon.start()
            except:
                pass
            time.sleep(1)
            self.assertEqual(os.path.isfile(pid_file), 1)
    #
    def TestGetEumetcastDaemon(self):

        logger.info('Test GetEumetcast daemon')

        pid_file = es_constants.get_eumetcast_pid_filename
        daemon = acquisition.GetEumetcastDaemon(pid_file, dry_run=True)

        # If the daemon is running, stop it and check file does not exist
        if os.path.isfile(pid_file):
            logger.info('GetEumetcast pid file exist: stop daemon')
            try:
                daemon.stop()
            except:
                pass
            self.assertEqual(os.path.isfile(pid_file), 0)
        else:
            logger.info('GetEumetcast pid file des NOT exist: start daemon')
            try:
                daemon.start()
            except:
                pass
            time.sleep(1)
            self.assertEqual(os.path.isfile(pid_file), 1)
