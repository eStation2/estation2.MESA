# -*- coding: utf-8 -*-
from __future__ import absolute_import
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
        pickle_filename=es2system.system_status_filename()

        # Run the method to save status
        result = es2system.save_status_local_machine()

        # Read the .pck
        object=None
        machine_status=functions.restore_obj_from_pickle(object, pickle_filename)

        # Checks
        print('Check psql ON')
        self.assertEquals(machine_status['postgresql_status'], True)

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

    def test_spirits_modify_header(self):

        # Should get here the role of my machine ...
        header_file = '/data/temp/spirits/20100101_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0_SPIRITS.hdr'
        cv.append_to_header_file(header_file, cv.metadata_spirits)

    def test_spirits_convert_1_file(self):

        metadata_spirits= {'prod_values': '{NDVI-toc, -, 0, 250, 0, 250, -0.08, 0.004}',
                           'flags': '{251=missing, 252=cloud, 253=snow, 254=sea, 255=back, 254=back}', \
                           'data_ignore_value':'255', \
                           'days': 10, \
                           'sensor_type':'VEGETATION', \
                           'comment':'My comment',\
                           'sensor_filename_prefix':'vgt', \
                           'frequency_filename_prefix':'10d', \
                           'pa_filename_prefix':'ndv'}

        # Should get here the role of my machine ...
        input_file = '/data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/tif/ndv/20150101_vgt-ndvi_ndv_SPOTV-Africa-1km_sv2-pv2.1.tif'
        output_dir = '/data/temp/spirits/mytest'
        functions.check_output_dir(output_dir)
        cv.convert_geotiff_file(input_file, output_dir, str(20150101), metadata_spirits)
