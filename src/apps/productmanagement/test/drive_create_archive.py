from __future__ import absolute_import

import datetime

from apps.productmanagement.create_archive import *
from lib.python import functions
import os
from database import connectdb


class drive_Create():

    target_dir = '/spatial_mesa/archives/'

    #   NOTE (Oct 2020): products are sorted in they same order they appear in the eStation Product Navigator,
    #                    and the online version is taken as reference for identifying all prod/sprod to archive
    #                    See also ES2-611
    #                    Start date of the timeseries is:
    #                       - 2015/01/01 as default
    #                       - 2018/01/01 for the PML daily prods
    #                       - 2019/01/01 for the S3 marine prods

    # -------------------------- VEGETATION ------------------------------------------------------

    def drive_CreateArchive_wsi_hp(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='wsi-hp'
        version='V1.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # crop/pasture
        subproducts=['crop','pasture']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def drive_CreateArchive_modis_fapar(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-1-1km'
        product='modis-fapar'
        version='1.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # fapar and anomalies
        subproducts=['fapar','10dzscore']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10day stats
        subproducts=['10davg', '10dmin','10dmax']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_modis_ndvi(self):

        print('MODIS-NVDI from Boku University will NOT be delivered to Users')

    def drive_CreateArchive_vgt_dmp(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-dmp'
        version='V2.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # 10d prods
        subproducts=['dmp','10ddiff', '10dperc']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10d stats (no-date)
        subproducts=['10davg', '10dmin','10dmax']
        for subproduct in subproducts:

            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_vgt_fcover(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-fcover'
        version='V2.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

    def drive_CreateArchive_vgt_lai(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-lai'
        version='V2.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # 10d prods
        subproducts=['lai','10ddiff', '10dperc', '10dna', '10dzscore']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10d stats (no-date)
        subproducts=['10davg', '10dmin','10dmax', '10dstd']
        for subproduct in subproducts:

            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_vgt_ndvi(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-ndvi'
        version='sv2-pv2.2'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # 10d prods
        subproducts=['ndvi-linearx1','ndvi-linearx2','linearx2diff-linearx2','10dperc-linearx2','vci-linearx2',
                     'ngi-linearx2','10dsndvi-linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10d stats (no-date)
        subproducts=['10davg-linearx2', '10dmin-linearx2','10dmax-linearx2', '10dstd-linearx2']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_vgt_fapar(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='vgt-fapar'
        version='V2.0'
        start_date=datetime.date(2015, 5, 11)
        end_date=None

        # 10d prods
        subproducts=['fapar','10ddiff', '10dperc', '10dna', '10dzscore']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # 10d stats (no-date)
        subproducts=['10davg', '10dmin','10dmax', '10dstd']
        for subproduct in subproducts:

            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    # -------------------------- RAINFALL ------------------------------------------------------

    def drive_CreateArchive_arc2_rain(self):

        base_target_dir=self.target_dir
        mapset='ARC2-Africa-11km/'
        product='arc2-rain'
        version='2.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

       # All products - from 1d to 1year
        subproducts=['1day', '10d','1mon','3mon','6mon','1year']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_chirps_dekad(self):

        base_target_dir=self.target_dir
        mapset='CHIRP-Africa-5km'
        product='chirps-dekad'
        version='2.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Products
        subproducts=['10d', '10ddiff', '10dperc','10dnp','1moncum','1mondiff','1monperc','1monnp']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # Stats
        subproducts=['10davg', '10dmin','10dmax', '1monavg', '1monmin', '1monmax']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_fewsnet_rfe(self):

        base_target_dir=self.target_dir
        mapset='FEWSNET-Africa-8km'
        product='fewsnet-rfe'
        version='2.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Products
        subproducts=['10d', '10ddiff', '10dperc','10dnp','1moncum','1mondiff','1monperc','1monnp']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # Stats
        subproducts=['10davg', '10dmin','10dmax', '1monavg', '1monmin', '1monmax']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_rain_spi(self):

        base_target_dir=self.target_dir
        mapset='CHIRP-Africa-5km'
        product='rain-spi'
        version='V1.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # crop/pasture
        subproducts=['spi-1mon','spi-3mon']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def drive_CreateArchive_tamsat_rfe(self, version=None):

        if version is None:
            version = '3.1'
        base_target_dir=self.target_dir
        mapset='TAMSAT-Africa-4km'
        product='tamsat-rfe'

        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Products
        subproducts=['10d', '10ddiff', '10dperc','10dnp','1moncum','1mondiff','1monperc','1monnp']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # Stats
        subproducts=['10davg', '10dmin','10dmax', '1monavg', '1monmin', '1monmax']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    # -------------------------- INLAND WATER --------------------------------------------------

    def drive_CreateArchive_wd_gee(self):

        mapsets = ['WD-GEE-CENTRALAFRICA-AVG' ,
                   'WD-GEE-ECOWAS-AVG',
                   'WD-GEE-IGAD-AVG',                   # Why not EASTAfrica ??
                   'WD-GEE-NORTHAFRICA-AVG',
                   'WD-GEE-SOUTHAFRICA-AVG',
                   'WD-GEE-WESTAFRICA-AVG']             # WESTAFRICA w.r.t ECOWAS ??

        # Only ECOWAS FTTB
        # for mapset in mapsets[1]:
        mapset='WD-GEE-WESTAFRICA-AVG'
        base_target_dir=self.target_dir
        product='wd-gee'
        version='1.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Occurancies
        subproduct='occurr'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # stats products 1km
        subproduct='avg'
        target_dir = base_target_dir + product + os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    # -------------------------- FIRE     ------------------------------------------------------
    def drive_CreateArchive_modis_firms(self):

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

    # -------------------------- OCEANOGRAPHY --------------------------------------------------

    def drive_CreateArchive_modis_chla(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-chla'
        version='v2013.1'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Products
        subproducts=['8daysavg','opfish','gradient','monavg','monanom']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # MODIS Chla stats
        subproduct='monclim'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_modis_kd490(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-kd490'
        version='v2012.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Products
        subproducts=['8daysavg','monavg','monanom']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # Stats
        subproduct='monclim'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_modis_par(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-par'
        version='v2012.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Products
        subproducts=['8daysavg','monavg','monanom']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # Stats
        subproduct='monclim'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_modis_pp(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-pp'
        version='v2013.1'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Products
        subproducts= ['8daysavg','monavg']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)


        # Stats
        subproducts=['8daysclim', '8daysmax','8daysmin','1monclim', '1monmax','1monmin']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_modis_sst(self):

        base_target_dir=self.target_dir
        mapset='MODIS-Africa-4km'
        product='modis-sst'
        version='v2013.1'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # Products
        subproducts=['8daysavg', 'monavg','monanom']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        # Stats
        subproduct='monclim'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=-1, end_date=-1, target_dir=target_dir)

    def drive_CreateArchive_pml_modis_chl(self):

        base_target_dir=self.target_dir
        product='pml-modis-chl'
        version='3.0'
        start_date=datetime.date(2018, 1, 1)
        end_date=None
        subproduct= 'chl-3day'
        target_dir = base_target_dir + product + os.path.sep + subproduct

        # Only chl-3day subproduct
        mapset='SPOTV-IOC-1km'
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date,
                                 target_dir=target_dir)

        # Only chl-3day subproduct
        mapset='SPOTV-UoG-1km'
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date,
                                 target_dir=target_dir)

    def drive_CreateArchive_pml_modis_sst(self):

        base_target_dir=self.target_dir
        product='pml-modis-sst'
        version='3.0'
        start_date=datetime.date(2018, 1, 1)
        end_date=None

        mapset='SPOTV-IOC-1km'
        subproducts = ['sst-3day', 'sst-fronts']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

        mapset='SPOTV-UoG-1km'
        subproducts = ['sst-3day', 'sst-fronts']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def drive_CreateArchive_olci_wrr(self):

        base_target_dir=self.target_dir
        mapset='SENTINEL-Africa-1km'
        product='olci-wrr'
        version='V02.0'
        start_date=datetime.date(2019, 1, 1)
        end_date=None

        # Only chl-oc4me subproduct
        subproducts=['chl-oc4me','monchla']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def drive_CreateArchive_slstr_sst(self):

        base_target_dir=self.target_dir
        mapset='SENTINEL-Africa-1km'
        product='slstr-sst'
        version='1.0'
        start_date=datetime.date(2019, 1, 1)
        end_date=None

        # Only wst subproduct
        subproducts=['wst','sst-fronts']
        for subproduct in subproducts:
            target_dir = base_target_dir + product + os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    # -------------------------- MISCELLANEOUS --------------------------------------------------

    def drive_CreateArchive_ascat_swi(self):

        base_target_dir=self.target_dir
        mapset='ASCAT-Africa-12-5km'
        product='ascat-swi'
        version='V3.1'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # SWI
        subproduct='swi'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def drive_CreateArchive_cpc_sm(self):

        base_target_dir=self.target_dir
        mapset='CPC-Africa-50km'
        product='cpc-sm'
        version='1.0'
        start_date=datetime.date(2015, 1, 1)
        end_date=None

        # SM
        subproduct='sm'
        target_dir = base_target_dir + product+ os.path.sep + subproduct
        functions.check_output_dir(target_dir)
        create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def drive_CreateArchive_lsasaf_et(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='lsasaf-et'
        version='undefined'
        start_date=datetime.date(2016, 1, 1)
        end_date=None

        # SM
        subproducts= ['10dcum','1moncum']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    def drive_CreateArchive_lsasaf_lst(self):

        base_target_dir=self.target_dir
        mapset='SPOTV-Africa-1km'
        product='lsasaf-lst'
        version='undefined'
        start_date=datetime.date(2018, 1, 1)
        end_date=None

        # SM
        subproducts= ['10dmax','10dmax', '10dmin']
        for subproduct in subproducts:
            target_dir = base_target_dir + product+ os.path.sep + subproduct
            functions.check_output_dir(target_dir)
            create_archive_eumetcast(product, version, subproduct, mapset, start_date=start_date, end_date=end_date, target_dir=target_dir)

    # -------------------------- ALL --------------------------------------------------

    def drive_CreateArchive_all(self):

        # Vegetation (30.10.20 -> done)
        self.drive_CreateArchive_wsi_hp()
        self.drive_CreateArchive_modis_fapar()
        self.drive_CreateArchive_modis_ndvi()
        self.drive_CreateArchive_vgt_dmp()
        self.drive_CreateArchive_vgt_fcover()
        self.drive_CreateArchive_vgt_lai()
        self.drive_CreateArchive_vgt_ndvi()
        self.drive_CreateArchive_vgt_fapar()

        # # Rainfall (30.10.20 -> done) (rain-spi and tamsat-3.1 added on 10.2.2021)
        self.drive_CreateArchive_arc2_rain()
        self.drive_CreateArchive_chirps_dekad()
        self.drive_CreateArchive_fewsnet_rfe()
        self.drive_CreateArchive_rain_spi()
        self.drive_CreateArchive_tamsat_rfe(version='3.0')
        self.drive_CreateArchive_tamsat_rfe(version='3.1')

        # # Fire (30.10.20 -> done)
        self.drive_CreateArchive_modis_firms()

        # Inland Water (see ES2-638)
        # self.drive_CreateArchive_wd_gee()

        # Oceanography (30.10.20 -> done)
        self.drive_CreateArchive_modis_chla()
        self.drive_CreateArchive_modis_kd490()
        self.drive_CreateArchive_modis_par()
        self.drive_CreateArchive_modis_pp()
        self.drive_CreateArchive_modis_sst()

        self.drive_CreateArchive_pml_modis_chl()
        self.drive_CreateArchive_pml_modis_sst()

        self.drive_CreateArchive_olci_wrr()
        self.drive_CreateArchive_slstr_sst()

        # Miscellaneous [lsasaf added on 10.2.2021]
        self.drive_CreateArchive_ascat_swi()
        self.drive_CreateArchive_cpc_sm()
        self.drive_CreateArchive_lsasaf_et()
        self.drive_CreateArchive_lsasaf_lst()

if __name__ == '__main__':

    driver = drive_Create()
    driver.drive_CreateArchive_all()

