


#from apps.acquisition.get_internet import *
from apps.acquisition.get_internet import *
from apps.acquisition.get_eumetcast import *

import unittest


class TestGetInternet(unittest.TestCase):

    def TestGetInfo(self):

        eum_id = 'EO:EUM:DAT:MSG:LST-SEVIRI'
        info = get_eumetcast_info(eum_id)

    #   ---------------------------------------------------------------------------
    #   Test iteration on remote ftp (e.g. MODIS)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_MODIS_BA_monthly(self):

        # Retrieve a list of MODIS burndate file .. check only one present
        remote_url='ftp://ba1.geog.umd.edu'
        usr_pwd='user:burnt_data'
        full_regex   ='Collection51/TIFF/Win11/2011/MCD45monthly.A20.*burndate.tif.gz'
        file_to_check='Collection51/TIFF/Win11/2011/MCD45monthly.A2011001.Win11.051.burndate.tif.gz'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)

        self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test iteration on remote ftp (e.g. NASA_FIRMS)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_FIRMS_NASA(self):

        # Retrieve a list of MODIS burndate file .. check only one present
        remote_url='ftp://nrt1.modaps.eosdis.nasa.gov/FIRMS/Global'
        usr_pwd='jrcMondeFires:FIRE@data1'
        full_regex   ='Global_MCD14DL_20142...txt'
        file_to_check='Global_MCD14DL_2014260.txt'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)

        self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test iteration on remote ftp (e.g. VITO GL-GIO products)
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_FTP_VITO(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     remote_url='ftp://catftp.vgt.vito.be/'
    #     usr_pwd='estationJRC:eStation14'
    #     full_regex   ='/^[A-Za-z0-9].*/^g2_BIOPAR_.*zip$'
    #     file_to_check=''
    #
    #     list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
    #
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test iteration on remote ftp (e.g. VITO GL-GIO products)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_CHIRP(self):

        # Retrieve a list of CHIRP
        remote_url='ftp://chg-ftpout.geog.ucsb.edu/pub/org/chg/products/CHIRP/pentads/'
        usr_pwd='anonymous:anonymous'
        full_regex   ='CHIRP.[12][0-9][0-9][0-9].[01][0-9].[1-6].tif$'
        file_to_check='CHIRP.2014.09.3.tif'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)

        self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Get contents of a directory (HTTP)  -> MODIS_SST_8D
    #   An html document is returned
    #   ---------------------------------------------------------------------------
    def TestHttpDir(self):
        filename='modis_sst_8d.txt'
        remote_url='http://oceandata.sci.gsfc.nasa.gov/'
        UserPwd='anonymous:anonymous'
        filepath = get_dir_contents_from_url(remote_url, target_file=filename, userpwd=UserPwd)

        logger.info('File downloaded to: '+filepath)
        self.assertEqual(1,1)

    #   ---------------------------------------------------------------------------
    #   Get contents of a directory (FTP)  -> MCD45A1_TIF_C51
    #   A list of the dir is returned (as form ls -l)
    #   ---------------------------------------------------------------------------
    def TestFtpDir(self):
        filename='mcd45a1.txt'
        remote_url='ftp://ba1.geog.umd.edu/'
        UserPwd='user:burnt_data'
        filepath = get_dir_contents_from_url(remote_url, target_file=filename, userpwd=UserPwd)

        logger.info('File downloaded to: '+filepath)
        self.assertEqual(1,1)

    #   ---------------------------------------------------------------------------
    #   Get a file from HTTP (list_from_template=TRUE, No User/psw) -> FEWSNET
    #   ---------------------------------------------------------------------------
    def TestFewsnetFile(self):
        filename='a14081rb.zip'
        remote_url='http://earlywarning.usgs.gov/ftp2/raster/rf/a/2014/'
        # filepath = get_file_from_url(remote_url+filename, target_file=filename)
        filepath = get_dir_contents_from_url(remote_url, target_file=filename)
        logger.info('File downloaded to: '+filepath)
        self.assertEqual(1,1)

    #   ---------------------------------------------------------------------------
    #   Get a file from FTP (list_from_template=FALSE, User/psw) -> FIRMS_NASA
    #   ---------------------------------------------------------------------------
    def TestFirmsFile(test):
        filename='Global_MCD14DL_2014237.txt'
        remote_url='ftp://nrt1.modaps.eosdis.nasa.gov/FIRMS/Global/'
        Username='jrcMondeFires'
        Password='FIRE@data1'
        UserPwd=Username+':'+Password
        get_file_from_url(remote_url, target_file=filename, userpwd=UserPwd)
