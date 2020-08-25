from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import unittest
import datetime

from apps.productmanagement.create_archive import *
from lib.python import functions
import os
from database import connectdb


class TestCreate(unittest.TestCase):

    target_dir = '/spatial_data/archives/'

    def TestCreateArchive(self):
        product='vgt-ndvi'
        version='spot-v2'
        subproducts='ndv'
        mapset='SPOTV-Africa-1km'
        start_date=datetime.date(2014, 1, 1)
        end_date=datetime.date(2014, 12, 21)
        create_archive_eumetcast(product, version, subproducts, mapset, start_date=start_date, end_date=end_date, target_dir=self.target_dir)

    def TestCreateArchive_vgt_ndvi(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-ndvi'
        version='sv2-pv2.2'
        start_date=datetime.date(2011, 1, 1)
        end_date=None

        # # NDV from sv2-pv2.2: since 02.05.2017 -> real files (not or ) are created !
        subproduct='ndv'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # ndvi_linearx1/2
        subproducts=['ndvi-linearx1','ndvi-linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10day stats
        subproducts=['10davg-linearx2', '10dmin-linearx2','10dmax-linearx2', '10dmed-linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # # 10day stats - additional
        # subproducts=['year-min-linearx2','year-max-linearx2','absol-min-linearx2','absol-max-linearx2']
        # for subproduct in subproducts:
        #      target_dir = base_target_dir + product + os.path.sep + subproduct
        #      functions.check_output_dir(target_dir)
        #      create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)
        #
        # # # baresoil mask
        # subproducts=['baresoil-linearx2']
        # for subproduct in subproducts:
        #     target_dir = base_target_dir + product + os.path.sep + subproduct
        #     functions.check_output_dir(target_dir)
        #     create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)
        # #
        # # # anomalies based on ndv (not filtered) and linearx2 statistics
        # subproducts=['diff-linearx2','vci','icn']
        # for subproduct in subproducts:
        #     target_dir = base_target_dir + product + os.path.sep + subproduct
        #     functions.check_output_dir(target_dir)
        #     create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)
        # #
        # # # anomalies based on filtered ndv and statistics
        # subproducts=['linearx2diff-linearx2','vci-linearx2','icn-linearx2']
        # for subproduct in subproducts:
        #     target_dir = base_target_dir + product + os.path.sep + subproduct
        #     functions.check_output_dir(target_dir)
        #     create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)
        #
        # # 1mon prod and stats
        subproduct='monndvi'
        target_dir = base_target_dir + product + os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)
        #
        # monthly stats
        subproducts=['1monavg', '1monmin','1monmax']
        start_date=None
        end_date=None
        for subproduct in subproducts:

            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def TestCreateArchive_vgt_fapar(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-fapar'
        version='V1.4'
        start_date=datetime.date(2015, 5, 11)
        end_date=None

        # Only fapar subproduct
        subproduct='fapar'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_vgt_fcover(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-fcover'
        version='V1.4'
        start_date=datetime.date(2014, 5, 21)
        end_date=None

        # Only fapar subproduct
        subproduct='fcover'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_vgt_lai(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-lai'
        version='V1.4'
        start_date=datetime.date(2014, 5, 21)
        end_date=None

        # Only fapar subproduct
        subproduct='lai'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_vgt_dmp(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-dmp'
        version='V1.0'
        start_date=datetime.date(2014, 6, 1)
        end_date=None

        # Only dmp subproduct
        subproduct='dmp'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_fewsnet_rfe(self):

        base_target_dir=self.target_dir
        mapset='FEWSNET-Africa-8km'
        product='fewsnet-rfe'
        version='2.0'
        start_date=datetime.date(2011, 1, 1)
        end_date=None

        # RFE from 2.0: since 01.01.2011
        subproduct='10d'
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

        # 1 mon cum: since 01.01.2011
        subproduct='1moncum'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 1mon stats
        subproducts=['1monavg', '1monmin', '1monmax']
        for subproduct in subproducts:

            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # 1mon anomalies
        subproducts=['1mondiff', '1monperc', '1monnp']
        for subproduct in subproducts:
            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_tamsat_rfe(self):

        base_target_dir=self.target_dir
        mapset='TAMSAT-Africa-4km'
        product='tamsat-rfe'
        version='2.0'
        start_date=datetime.date(2011, 1, 1)
        end_date=None

        # RFE from 2.0: since 01.01.2011
        subproduct='10d'
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

        # 1 mon cum: since 01.01.2011
        subproduct='1moncum'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 1mon stats
        subproducts=['1monavg', '1monmin', '1monmax']
        for subproduct in subproducts:

            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # 1mon anomalies
        subproducts=['1mondiff', '1monperc', '1monnp']
        for subproduct in subproducts:
            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_chirps_dekad(self):

        base_target_dir=self.target_dir
        mapset='CHIRP-Africa-5km'
        product='chirps-dekad'
        version='2.0'
        start_date=datetime.date(2011, 1, 1)
        end_date=None

        # RFE from 2.0: since 01.01.2011
        subproduct='10d'
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

        # 1 mon cum: since 01.01.2011
        subproduct='1moncum'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 1mon stats
        subproducts=['1monavg', '1monmin', '1monmax']
        for subproduct in subproducts:

            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # 1mon anomalies
        subproducts=['1mondiff', '1monperc', '1monnp']
        for subproduct in subproducts:
            target_dir = base_target_dir+ product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_modis_chla(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-chla'
        version='v2013.1'
        start_date=datetime.date(2014, 1, 1)
        end_date=None

        # MODIS Chla: since 01.01.2014
        subproducts=['chla-day','monavg','monanom']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # MODIS Chla stats
        # subproduct='monclim'
        # target_dir = base_target_dir + product+ os.path.sep + subproduct
        # functions.check_output_dir(target_dir)
        # create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def TestCreateArchive_modis_sst(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-sst'
        version='v2013.1'
        start_date=datetime.date(2014, 1, 1)
        end_date=None

        # MODIS SST: since 01.01.2014
        subproducts=['sst-day','monavg','monanom']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # MODIS SST stats
        # subproduct='monclim'
        # target_dir = base_target_dir + product+ os.path.sep + subproduct
        # functions.check_output_dir(target_dir)
        # create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def TestCreateArchive_modis_par(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-par'
        version='v2012.0'
        start_date=datetime.date(2014, 1, 1)
        end_date=None

        # MODIS PAR: since 01.01.2014
        subproducts=['par-day','monavg','monanom']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # MODIS PAR stats
        # subproduct='monclim'
        # target_dir = base_target_dir + product+ os.path.sep + subproduct
        # functions.check_output_dir(target_dir)
        # create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def TestCreateArchive_modis_kd490(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-kd490'
        version='v2012.0'
        start_date=datetime.date(2014, 1, 1)
        end_date=None

        # MODIS KD490: since 01.01.2014
        subproducts=['kd490-day','monavg','monanom']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # MODIS KD490 stats
        # subproduct='monclim'
        # target_dir = base_target_dir + product+ os.path.sep + subproduct
        # functions.check_output_dir(target_dir)
        # create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def TestCreateArchive_modis_firms(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='modis-firms'
        version='v6.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # FIRMS for version 6.0: since 01.01.2015
        subproduct='1day'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # derived products 1km
        subproducts=['10dcount', '10dcountdiff']
        for subproduct in subproducts:

            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # stats products 1km
        subproducts=['10dcountavg', '10dcountmin','10dcountmax']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        mapset='SPOTV-Africa-10km'
        # derived products 10km
        subproducts=['10dcount10k', '10dcount10kdiff', '10dcount10kperc', '10dcount10kratio']
        for subproduct in subproducts:

            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # stats products 1km
        subproducts=['10dcount10kavg', '10dcount10kmin','10dcount10kmax']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)


    def TestCreateArchive_vgt_ndvi_2_2(self):

        base_target_dir='/data/archives/vgt-ndvi-2.2/'
        mapset='SPOTV-ECOWAS-1km'
        product='vgt-ndvi'
        version='sv2-pv2.2'
        start_date=datetime.date(2011, 1, 1)
        end_date=datetime.date(2011, 12, 31)

        subproduct='ndv'
        target_dir = base_target_dir + mapset+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_olci_wrr(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='olci-wrr'
        version='V02.0'
        start_date=datetime.date(2018, 3, 1)
        end_date=None

        # Only chl-oc4me subproduct
        subproduct='chl-oc4me'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_slstr_sst(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='slstr-sst'
        version='1.0'
        start_date=datetime.date(2018, 3, 1)
        end_date=None

        # Only wst subproduct
        subproduct='wst'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_pml_modis_sst(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-IOC-1km'
        product='pml-modis-sst'
        version='3.0'
        start_date=datetime.date(2015, 4, 18)
        end_date=None

        subproducts= ['sst-3day','sst-fronts']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def TestCreateArchive_pml_modis_chl(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-IOC-1km'
        product='pml-modis-chl'
        version='3.0'
        start_date=datetime.date(2015, 4, 18)
        end_date=None

        # Only chl-3day subproduct
        subproduct= 'chl-3day'
        target_dir = base_target_dir + product + os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date,
                                 target_dir=target_dir)


    def TestCreateArchive_modis_pp(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-pp'
        version='v2013.1'
        start_date=datetime.date(2002, 7, 1)
        end_date=None

        subproducts= ['monavg','8daysavg']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)


        subproducts=['1monclim', '1monmax','1monmin']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)


    def TestCreateArchive_all(self):

        self.TestCreateArchive_vgt_ndvi()
        self.TestCreateArchive_vgt_fapar()
        self.TestCreateArchive_vgt_fcover()
        self.TestCreateArchive_vgt_lai()
        self.TestCreateArchive_vgt_dmp()
        self.TestCreateArchive_chirps_dekad()
        self.TestCreateArchive_fewsnet_rfe()
        self.TestCreateArchive_tamsat_rfe()
        self.TestCreateArchive_modis_chla()
        self.TestCreateArchive_modis_sst()
        self.TestCreateArchive_modis_par()
        self.TestCreateArchive_modis_kd490()
        self.TestCreateArchive_modis_firms()
        self.TestCreateArchive_olci_wrr()
        self.TestCreateArchive_pml_modis_sst()
        #self.TestCreateArchive_slstr_sst()
        self.TestCreateArchive_pml_modis_chl()
        self.TestCreateArchive_modis_pp()