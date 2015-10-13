from __future__ import absolute_import

import unittest
import datetime

from apps.productmanagement.create_archive import *
from lib.python import functions
import os
from database import connectdb


class TestCreate(unittest.TestCase):
    #def setUp(self):
        #setattr(querydb, 'db', connectdb.ConnectDB(use_sqlite=False).db)

    def TestCreateArchive(self):
        product='vgt-ndvi'
        version='spot-v2'
        subproducts='ndv'
        mapset='SPOTV-Africa-1km'
        start_date=datetime.date(2014, 1, 1)
        end_date=datetime.date(2014, 12, 21)
        target_dir='/data/archives/'
        create_archive_eumetcast(product, version, subproducts, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_vgt_ndvi(self):

        base_target_dir='/data/archives/'
        mapset='SPOTV-Africa-1km'
        product='vgt-ndvi'
        version='sv2-pv2.1'
        start_date=datetime.date(2011, 1, 1)
        end_date=None

        # # NDV from sv2-pv2.1: since 01.01.2011 -> real files (not or ) are created !
        subproduct='ndv'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # ndvi_linearx1/2
        subproducts=['ndvi_linearx1','ndvi_linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10day stats
        subproducts=['10davg_linearx2', '10dmin_linearx2','10dmax_linearx2', '10dmed_linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # 10day stats - additional
        subproducts=['year_min_linearx2','year_max_linearx2','absol_min_linearx2','absol_max_linearx2']
        for subproduct in subproducts:
             target_dir = base_target_dir + product + os.path.sep + subproduct
             functions.check_output_dir(target_dir)
             create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # # baresoil mask
        subproducts=['baresoil_linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)
        #
        # # anomalies based on ndv (not filtered) and linearx2 statistics
        subproducts=['diff_linearx2','vci','icn']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)
        #
        # # anomalies based on filtered ndv and statistics
        subproducts=['linearx2diff_linearx2','vci_linearx2','icn_linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 1mon prod and stats
        subproduct='monndvi'
        target_dir = base_target_dir + product + os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # monthly stats
        subproducts=['1monavg', '1monmin','1monmax']
        start_date=None
        end_date=None
        for subproduct in subproducts:

            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def TestCreateArchive_fewsnet_rfe(self):

        base_target_dir='/data/archives/'
        mapset='FEWSNET-Africa-8km'
        product='fewsnet-rfe'
        version='2.0'

        # RFE from 2.0: since 01.01.2011
        subproduct='10d'
        start_date=datetime.date(2011, 1, 1)
        end_date=None
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10day stats
        subproducts=['10davg', '10dmin','10dmax']
        start_date=None
        end_date=None
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # 1mon stats
        subproducts=['1moncum', '1monavg', '1monmin', '1monmax']
        start_date=None
        end_date=None
        for subproduct in subproducts:

            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def TestCreateArchive_tamsat_rfe(self):

        base_target_dir='/data/archives/'
        mapset='TAMSAT-Africa-4km'
        product='tamsat-rfe'
        version='2.0'

        # RFE from 2.0: since 01.01.2011
        subproduct='10d'
        start_date=datetime.date(2011, 1, 1)
        end_date=None
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)


        # 10day stats
        subproducts=['10davg', '10dmin','10dmax']
        start_date=None
        end_date=None
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # 1mon stats
        subproducts=['1moncum', '1monavg', '1monmin', '1monmax']
        start_date=None
        end_date=None
        for subproduct in subproducts:

            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def TestCreateArchive_chirps_dekad(self):

        base_target_dir='/data/archives/'
        mapset='CHIRP-Africa-5km'
        product='chirps-dekad'
        version='2.0'

        # RFE from 2.0: since 01.01.2011
        subproduct='10d'
        start_date=datetime.date(2011, 1, 1)
        end_date=None
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10day stats
        subproducts=['10davg', '10dmin','10dmax']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # 10day anomalies
        subproducts=['10ddiff', '10dperc','10dnp']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 1mon stats
        subproducts=['1moncum', '1monavg', '1monmin', '1monmax']
        for subproduct in subproducts:
            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # 1mon anomalies
        subproducts=['1mondiff', '1monperc', '1monnp']
        for subproduct in subproducts:
            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)
