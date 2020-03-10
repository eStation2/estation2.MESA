from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase

__author__ = "Jurriaan van 't Klooster"

import lib.python.functions as functions
import json


class TestFunctions(TestCase):
    def test_tcp_test(self):
        mesaproc = "139.191.147.79:22"
        mesaproc = 'mesa-proc.ies.jrc.it'
        self.assertTrue(functions.check_connection(mesaproc))
        pc3 = "192.168.0.15:22"
        pc3 = "h05-dev-vm19.ies.jrc.it"
        self.assertTrue(functions.check_connection(pc3))

    def test_get_remote_system_status(self):
        server_address = '10.191.231.90'  # vm19
        server_address = "h05-dev-vm19.ies.jrc.it"
        status_remote_machine = functions.get_remote_system_status(server_address)
        print (status_remote_machine)
        if "mode" in status_remote_machine:
            PC2_mode = status_remote_machine['mode']
            PC2_disk_status = status_remote_machine['disk_status']
            PC2_version = status_remote_machine['active_version']
            PC2_postgresql_status = status_remote_machine['postgresql_status']
            PC2_internet_status = status_remote_machine['internet_connection_status']
            PC2_service_eumetcast = status_remote_machine['get_eumetcast_status']
            PC2_service_internet = status_remote_machine['get_internet_status']
            PC2_service_ingest = status_remote_machine['ingestion_status']
            PC2_service_processing = status_remote_machine['processing_status']
            PC2_service_system = status_remote_machine['system_status']
            PC2_system_execution_time = status_remote_machine['system_execution_time']

        print ("Done")

    def test_get_status_PC1(self):
        status_PC1 = functions.get_status_PC1()
        print (status_PC1)

    def test_internet_connection(self):
        status = functions.internet_on()
        print (status)

    def test_manage_netcdf_scaling(self):

        preproc_file = '/tmp/eStation2/apps.acquisition.ingestion4Losxu_A2016201.L3m_DAY_SST_sst_4km.nc/A2016201.L3m_DAY_SST_sst_4km.nc.geotiff'
        sds          = 'NETCDF:/data/ingest/A2016201.L3m_DAY_SST_sst_4km.nc:sst'
        status = functions.save_netcdf_scaling(sds, preproc_file)
        [fact, off] = functions.read_netcdf_scaling(preproc_file)
        print((fact, off))

    def test_get_status_All_Services(self):
        services_status = functions.getStatusAllServices()
        print (services_status)

