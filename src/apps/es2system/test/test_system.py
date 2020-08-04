# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from future import standard_library

import unittest
import os
from config import es_constants
from apps.es2system import es2system
from lib.python import functions

standard_library.install_aliases()


class TestSystem(unittest.TestCase):
    systemsettings = functions.getSystemSettings()
    install_type = systemsettings['type_installation'].lower()

    def test_manage_lock(self):

        # Check the management of the lock files
        lock_id = 'test_operation'
        # Delete all existing locks
        status = es2system.system_manage_lock('All_locks', 'Delete')
        self.assertEquals(status, 0)

        # Check a (not existing) lock
        status = es2system.system_manage_lock(lock_id, 'Check')
        self.assertEquals(status, 0)

        # Create a lock
        status = es2system.system_manage_lock(lock_id, 'Create')
        self.assertEquals(status, 0)

        # Check an (existing) lock
        status = es2system.system_manage_lock(lock_id, 'Check')
        self.assertEquals(status, 1)

    def test_save_status(self):

        # Save machine status in /eStation/system
        status_system_file = es2system.save_status_local_machine()
        self.assertEqual(status_system_file, 0)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_change_ip_addresses_default(self):
        ip_pc1 = '192.168.0.11'
        ip_pc2 = '192.168.0.15'
        ip_pc3 = '192.168.0.16'
        ip_dns = '192.168.0.1'
        gateway = '192.168.0.1'
        ip_lan = '192.168.0.0/24'

        sudo_psw = 'mesadmin'
        command = es_constants.es2globals['base_dir'] + '/apps/es2system/network_config_1.0.sh ' + \
                  ip_pc1 + ' ' + \
                  ip_pc2 + ' ' + \
                  ip_pc3 + ' ' + \
                  ip_dns + ' ' + \
                  gateway + ' ' + \
                  ip_lan
        status = os.system('echo %s | sudo -S %s' % (sudo_psw, command))
        self.assertEqual(status, 0)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_change_ip_addresses_Container(self):

        ip_pc1 = '10.191.231.11'  # the machine does not actually exist ..
        ip_pc2 = '10.191.231.89'
        ip_pc3 = '10.191.231.90'
        ip_dns = '139.191.1.132'  # Only primary ... secondary to be added
        gateway = '10.191.231.1'
        ip_lan = '10.191.231.0/24'  # To be checked (?)

        sudo_psw = 'mesadmin'
        command = es_constants.es2globals['base_dir'] + '/apps/es2system/network_config_1.0.sh ' + \
                  ip_pc1 + ' ' + \
                  ip_pc2 + ' ' + \
                  ip_pc3 + ' ' + \
                  ip_dns + ' ' + \
                  gateway + ' ' + \
                  ip_lan
        status = os.system('echo %s | sudo -S %s' % (sudo_psw, command))
        self.assertEqual(status, 0)

    # The following test enters an infinite loop (?) -> see test_system_loop below with dry_run = True
    # def test_system_service(self):
    #
    #     status = es2system.loop_system(dry_run=False)
    #     self.assertEqual(status, 0)

    @unittest.skipIf(True, "Not working - to be checked")
    def test_system_db_dump_docker(self):

        list_dump = ['products', 'analysis']
        status = es2system.system_db_dump_docker(list_dump)
        self.assertEqual(status, b'')

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_system_db_dump(self):

        list_dump = ['products', 'analysis']
        status = es2system.system_db_dump(list_dump)
        self.assertEqual(status, 0)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_system_manage_dumps(self):

        status = es2system.system_manage_dumps()
        self.assertEqual(status, 0)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_system_data_sync(self):

        source = es_constants.es2globals['processing_dir']
        system_settings = functions.getSystemSettings()
        ip_target = system_settings['ip_pc2']
        target = ip_target + '::products' + es_constants.es2globals['processing_dir']

        status = es2system.system_data_sync(source, target)
        self.assertEqual(status, 0)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_db_sync_full_from_PC2(self):

        list_syncs = ['sync_pc2_products_full', 'sync_pc2_analysis_full']
        status = es2system.system_db_sync(list_syncs)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_db_sync_full_from_PC3(self):

        list_syncs = ['sync_pc3_analysis_full', 'sync_pc3_products_full']
        status = es2system.system_db_sync(list_syncs)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_system_db_sync_full(self):

        # Should get here the role of my machine ...
        status = es2system.system_db_sync_full('pc2')
        self.assertTrue(status)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_system_bucardo_config(self):

        # Should get here the role of my machine ...
        status = es2system.system_bucardo_config()

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_system_status_PC1(self):

        # Should get here the role of my machine ...
        status = es2system.get_status_PC1()

    # @unittest.skipIf(install_type != 'full',"Test only on MESA Station - Full install")
    def test_system_install_report(self):

        # Should get here the role of my machine ...
        repfile = es2system.system_install_report()
        self.assertTrue(os.path.isfile(repfile))

    def test_system_create_report(self):

        # Create the report and check file axists
        repfile = es2system.system_create_report()
        self.assertTrue(os.path.isfile(repfile))

    def test_clean_temp_dir(self):

        # Clean the temp dirs and check the status
        status = es2system.clean_temp_dir()
        self.assertEqual(status, 0)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_bucardo_service(self):

        # Should get here the role of my machine ...
        status = es2system.system_bucardo_service('stop')

    def test_system_loop(self):

        # Call the system loop in dry mode (exits after first iteration)
        status = es2system.loop_system(dry_run=True)
        self.assertEqual(status, 0)

    @unittest.skipIf(install_type != 'server', "Test only on JRC Server Installation")
    def test_push_ftp_aruba(self):

        try:
            import apps.es2system.test.aruba_credentials as ac
        except:
            return 1

        # Masked=FALSE means the masked products are pushed.
        status = es2system.push_data_ftp(url=ac.url, user=ac.user, psw=ac.psw, trg_dir=ac.trg_dir, masked=False)
        self.assertEqual(status, 0)

    @unittest.skipIf(install_type != 'server', "Test only on JRC Server Installation")
    def test_push_ftp_jrc(self):

        # Execute w.o. arguments: they are read from config/server_ftp.py
        # The products/versions considered for sync are: the 'activated' ones - except the ones set as 'EXCLUDE' in server_ftp.py definitions
        # Masked=TRUE means the masked sub-products are not pushed (which is the default)

        status = es2system.push_data_ftp(masked=True)
        self.assertEqual(status, 0)


suite_system = unittest.TestLoader().loadTestsFromTestCase(TestSystem)
if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite_system)
