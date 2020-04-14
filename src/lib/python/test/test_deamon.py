from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library

import unittest

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
        self.daemon.start()
        status = self.daemon.status()
        self.assertTrue(status)
        pid = self.daemon.getpid_from_file()
        self.assertIsInstance(pid, int)
        self.daemon.stop()
        status = self.daemon.status()
        self.assertFalse(status)

    def test_restart(self):
        self.daemon.start()
        status = self.daemon.status()
        self.assertTrue(status)
        self.daemon.restart()
        status = self.daemon.status()
        self.assertTrue(status)
        self.daemon.stop()
        status = self.daemon.status()
        self.assertFalse(status)

    def test_start(self):
        self.daemon.start()
        status = self.daemon.status()
        self.assertTrue(status)

    def test_status(self):
        self.daemon.start()
        status = self.daemon.status()
        self.assertTrue(status)
        self.daemon.stop()
        status = self.daemon.status()
        self.assertFalse(status)

    def test_stop(self):
        self.daemon.stop()
        status = self.daemon.status()
        self.assertFalse(status)


suite_deamon = unittest.TestLoader().loadTestsFromTestCase(TestDeamon)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_deamon)
