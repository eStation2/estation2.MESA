from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
from builtins import object
import datetime

from apps.productmanagement.create_archive import *
from lib.python import functions
import os

class Create(object):

    def CreateArchive(self):
        product='vgt-ndvi'
        version='spot-v2'
        subproducts='ndv'
        mapset='SPOTV-Africa-1km'
        start_date=datetime.date(2014, 1, 1)
        end_date=datetime.date(2014, 12, 21)
        target_dir='/data/archives/'
        create_archive_eumetcast(product, version, subproducts, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def CreateArchive_vgt_ndvi(self):

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

        # 10day stats - additional
        subproducts=['year-min-linearx2','year-max-linearx2','absol-min-linearx2','absol-max-linearx2']
        for subproduct in subproducts:
             target_dir = base_target_dir + product + os.path.sep + subproduct
             functions.check_output_dir(target_dir)
             create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

        # # baresoil mask
        subproducts=['baresoil-linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)
        #
        # # anomalies based on ndv (not filtered) and linearx2 statistics
        subproducts=['diff-linearx2','vci','icn']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)
        #
        # # anomalies based on filtered ndv and statistics
        subproducts=['linearx2diff-linearx2','vci-linearx2','icn-linearx2']
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

    def CreateArchive_vgt_fapar(self):

        base_target_dir='/data/archives/'
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

    def CreateArchive_vgt_fcover(self):

        base_target_dir='/data/archives/'
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

    def CreateArchive_vgt_lai(self):

        base_target_dir='/data/archives/'
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

    def CreateArchive_vgt_dmp(self):

        base_target_dir='/data/archives/'
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

    def CreateArchive_fewsnet_rfe(self):

        base_target_dir='/data/archives/'
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

    def CreateArchive_tamsat_rfe(self):

        base_target_dir='/data/archives/'
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

    def CreateArchive_chirps_dekad(self):

        base_target_dir='/data/archives/'
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

    def CreateArchive_modis_firms(self):

        base_target_dir='/data/archives/'
        mapset='SPOTV-Africa-1km'
        product='modis-firms'
        version='v5.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # RFE from 2.0: since 01.01.2011
        subproduct='1day'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def CreateArchive_modis_chla(self):

        base_target_dir='/data/archives/'
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
        subproduct='monclim'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def CreateArchive_modis_sst(self):

        base_target_dir='/data/archives/'
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
        subproduct='monclim'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def CreateArchive_modis_par(self):

        base_target_dir='/data/archives/'
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
        subproduct='monclim'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def CreateArchive_modis_kd490(self):

        base_target_dir='/data/archives/'
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
        subproduct='monclim'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def CreateArchive_wbd_gee(self, overwrite=True):

        base_target_dir='/data/archives/'
        mapset='WD-GEE-ECOWAS-AVG'
        product='wd-gee'
        version='1.0'
        start_date=datetime.date(2014, 1, 1)
        end_date=datetime.date(2018, 6, 1)

        # occurr: since 01.01.2014
        # subproduct='occurr'
        # target_dir = base_target_dir + product+ os.path.sep + subproduct
        # functions.check_output_dir(target_dir)
        # create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir, tgz=True, overwrite=overwrite)

        # LTA
        subproduct='avg'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir, tgz=True, overwrite=overwrite)

    def CreateArchive_all(self):

        self.CreateArchive_vgt_ndvi()
        self.CreateArchive_vgt_fapar()
        self.CreateArchive_vgt_fcover()
        self.CreateArchive_vgt_lai()
        self.CreateArchive_vgt_dmp()
        self.CreateArchive_fewsnet_rfe()
        self.CreateArchive_tamsat_rfe()
        self.CreateArchive_chirps_dekad()
        self.CreateArchive_modis_firms()
        self.CreateArchive_modis_chla()
        self.CreateArchive_modis_sst()
        self.CreateArchive_modis_par()
        self.CreateArchive_modis_kd490()
        self.CreateArchive_wbd_gee()

if __name__=='__main__':

    tc = Create()
    tc.CreateArchive_wbd_gee(overwrite=True)
