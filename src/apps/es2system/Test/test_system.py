# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from future import standard_library
standard_library.install_aliases()
import unittest
from lib.python import functions
import unittest
import os
from config import es_constants

__author__ = "Jurriaan van 't Klooster"

from apps.es2system import es2system
import apps.es2system.convert_2_spirits  as cv


class TestSystem(unittest.TestCase):
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

        # Define .pck filename
        status_system_file=es2system.save_status_local_machine()


    def test_change_ip_addresses_default(self):

        ip_pc1='192.168.0.11'
        ip_pc2='192.168.0.15'
        ip_pc3='192.168.0.16'
        ip_dns='192.168.0.1'
        gateway='192.168.0.1'
        ip_lan='192.168.0.0/24'

        sudo_psw='mesadmin'
        command=es_constants.es2globals['base_dir']+'/apps/es2system/network_config_1.0.sh '+ \
                ip_pc1+' '+ \
                ip_pc2+' '+ \
                ip_pc3+' '+ \
                ip_dns+' '+ \
                gateway+' '+ \
                ip_lan
        status = os.system('echo %s | sudo -S %s' % (sudo_psw,command))
        self.assertEquals(status, 0)

    def test_change_ip_addresses_Container(self):

        ip_pc1='10.191.231.11'              # the machine does not actually exist ..
        ip_pc2='10.191.231.89'
        ip_pc3='10.191.231.90'
        ip_dns='139.191.1.132'              # Only primary ... secondary to be added
        gateway='10.191.231.1'
        ip_lan='10.191.231.0/24'            # To be checked (?)

        sudo_psw='mesadmin'
        command=es_constants.es2globals['base_dir']+'/apps/es2system/network_config_1.0.sh '+ \
        ip_pc1+' '+ \
        ip_pc2+' '+ \
        ip_pc3+' '+ \
        ip_dns+' '+ \
        gateway+' '+ \
        ip_lan
        status = os.system('echo %s | sudo -S %s' % (sudo_psw,command))
        self.assertEquals(status, 0)

    def test_system_service(self):

        status = es2system.loop_system(dry_run=False)
        self.assertEquals(status, 0)

    def test_system_db_dump(self):

        list_dump = ['products','analysis']
        status = es2system.system_db_dump(list_dump)
        self.assertEquals(status, 0)

    def test_system_manage_dumps(self):

        status = es2system.system_manage_dumps()
        self.assertEquals(status, 0)

    def test_system_data_sync(self):

        source = es_constants.es2globals['processing_dir']
        system_settings = functions.getSystemSettings()
        ip_target = system_settings['ip_pc2']
        target = ip_target+'::products'+es_constants.es2globals['processing_dir']

        status = es2system.system_data_sync(source, target)
        self.assertEquals(status, 0)

    def test_db_sync_full_from_PC2(self):

        list_syncs = ['sync_pc2_products_full','sync_pc2_analysis_full']
        status = es2system.system_db_sync(list_syncs)

    def test_db_sync_full_from_PC3(self):

        list_syncs = ['sync_pc3_analysis_full','sync_pc3_products_full']
        status = es2system.system_db_sync(list_syncs)

    def test_system_db_sync_full(self):

        # Should get here the role of my machine ...
        status = es2system.system_db_sync_full('pc2')

    def test_system_bucardo_config(self):

        # Should get here the role of my machine ...
        status = es2system.system_bucardo_config()

    def test_system_status_PC1(self):

        # Should get here the role of my machine ...
        status = es2system.get_status_PC1()

    def test_system_install_report(self):

        # Should get here the role of my machine ...
        status = es2system.system_install_report()

    def test_system_create_report(self):

        # Should get here the role of my machine ...
        status = es2system.system_create_report()

    def test_clean_temp_dir(self):

        # Should get here the role of my machine ...
        status = es2system.clean_temp_dir()

    def test_bucardo_service(self):

        # Should get here the role of my machine ...
        status = es2system.system_bucardo_service('stop')

    def test_system_loop(self):

        # Should get here the role of my machine ...
        status = es2system.loop_system(dry_run=True)

    def test_status_PC1(self):

        # Should get here the role of my machine ...
        status = es2system.get_status_PC1()
        print (status)

    def test_push_ftp_aruba(self):

        try:
            import apps.es2system.Test.aruba_credentials as ac
        except:
            return 1

        # Should get here the role of my machine ...
        # Masked=FALSE means the masked products are pushed.
        status = es2system.push_data_ftp(url=ac.url, user=ac.user, psw=ac.psw, trg_dir=ac.trg_dir, masked=False)

    def test_push_ftp_jrc(self):

        # Execute w.o. arguments: they are read from config/server_ftp.py
        # The products/versions considered for sync are: the 'activated' ones - except the ones set as 'EXCLUDE' in server_ftp.py definitions
        # Masked=TRUE means the masked sub-products are not pushed (which is the default)

        status = es2system.push_data_ftp(masked=True)
