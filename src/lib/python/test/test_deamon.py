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


#   TODO-JUR: Unittesting does not work for methods that are in a continues loop and do not return a value!
#             Static state methods naturally make themselves fairly untestable.
#             We have to be pragmatic about our work and don't write tests in the mere effort to
#             -----------
#             Of the 3 tests below 2 are working when running individually.
#             The test_restart does not work because it first stops the daemon which makes the test wait and blocks.
#             When running the suite all tests fail because the daemon.start gives a sys.exit(0),
#             which makes the test fail.

class TestRunDaemon(DaemonDryRunnable):
    def run(self):
        return True


class TestDeamon(unittest.TestCase):
    def setUp(self):
        self.pid_file = es_constants.get_internet_pid_filename
        self.daemon = TestRunDaemon(self.pid_file, dry_run=True)

    def tearDown(self):
        self.daemon.stop()

    def test_start_status(self):
        with self.assertRaises(SystemExit) as cm:
            self.daemon.start()
        self.assertEqual(cm.exception.code, 0)
        time.sleep(1)
        status = self.daemon.status()
        self.assertTrue(status)
        # self.daemon.stop()
        # self.assertEqual(self.daemon.status(), False)

    def test_getpid_from_file(self):
        self.daemon.start()
        time.sleep(1)
        status = self.daemon.status()
        self.assertTrue(status)
        pid = self.daemon.getpid_from_file()
        self.assertIsInstance(pid, int)

    def test_restart(self):
        self.skipTest("Restart calls deamon.stop() which kills the deamon pid and returns nothing so test blocks!")
        self.daemon.start()

        status = self.daemon.status()
        self.assertTrue(status)

        self.daemon.restart()

        status = self.daemon.status()
        self.assertTrue(status)


suite_deamon = unittest.TestLoader().loadTestsFromTestCase(TestDeamon)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_deamon)
