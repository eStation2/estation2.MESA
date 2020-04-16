from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library

import unittest
import time

from lib.python.daemon import DaemonDryRunnable
from apps.acquisition import get_internet
from config import es_constants

standard_library.install_aliases()


class TestGetInternetDaemon(DaemonDryRunnable):
    def run(self):
        get_internet.loop_get_internet(dry_run=self.dry_run)


class TestDeamon(unittest.TestCase):
    def setUp(self):
        self.pid_file = es_constants.get_internet_pid_filename
        self.daemon = TestGetInternetDaemon(self.pid_file, dry_run=True)

    def test_getpid_from_file(self):
        with self.assertRaises(SystemExit) as cm:
            self.daemon.start()

        time.sleep(1)
        status = self.daemon.status()
        self.assertTrue(status)
        pid = self.daemon.getpid_from_file()
        self.assertIsInstance(pid, int)

        self.daemon.stop()
        time.sleep(1)
        status = self.daemon.status()
        self.assertFalse(status)

    def test_restart(self):
        with self.assertRaises(SystemExit) as cm:
            self.daemon.start()

        time.sleep(1)
        status = self.daemon.status()
        self.assertTrue(status)

        with self.assertRaises(SystemExit) as cm:
            self.daemon.restart()

        time.sleep(1)
        status = self.daemon.status()
        self.assertTrue(status)

        time.sleep(1)
        self.daemon.stop()

        time.sleep(1)
        status = self.daemon.status()
        self.assertFalse(status)

    def test_start_status_stop(self):
        # here we should catch the 'sys.exit(0)', which otherwise causes nosetest to fail
        # see http://stackoverflow.com/questions/15672151/is-it-possible-for-a-unit-test-to-assert-that-a-method-calls-sys-exit

        with self.assertRaises(SystemExit) as cm:
            self.daemon.start()
        # self.assertEqual(cm.exception.code, 0)

        time.sleep(1)
        status = self.daemon.status()
        self.assertTrue(status)

        time.sleep(1)
        self.daemon.stop()
        self.assertEqual(self.daemon.status(), False)


suite_deamon = unittest.TestLoader().loadTestsFromTestCase(TestDeamon)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_deamon)
