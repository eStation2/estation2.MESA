from apps.acquisition.get_internet import *
from apps.acquisition.get_eumetcast import *

import unittest

class TestGetInternet(unittest.TestCase):

    def TestGetInfo(self):

        eum_id = 'EO:EUM:DAT:MSG:LST-SEVIRI'
        info = get_eumetcast_info(eum_id)

    #   ---------------------------------------------------------------------------
    #   Get contents of a remote MODIS BA  (id: UMD:MCD45A1:TIF:51)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_MCD45A1_TIF(self):
        remote_url='ftp://ba1.geog.umd.edu/Collection51/TIFF/'
        usr_pwd='user:burnt_data'
        full_regex   ='Win11/2011/MCD45monthly.*.burndate.tif.gz'
        file_to_check='Win11/2011/MCD45monthly.A2011001.Win11.051.burndate.tif.gz'


        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
        self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Get contents of a remote MODIS BA  (id: UMD:MCD45A1:HDF:51)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_MCD45A1_HDF(self):
        remote_url='ftp://ba1.geog.umd.edu/Collection51/HDF/'
        usr_pwd='user:burnt_data'
        #full_regex   ='20../.../MCD45A1.A.*.hdf'
        full_regex   ='2011/.../MCD45A1.A.*.hdf'
        file_to_check='2011/001/MCD45A1.A2011001.h05v10.051.2013067232210.hdf'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
        self.assertTrue(file_to_check in list)


    #   ---------------------------------------------------------------------------
    #   Test remote ftp NASA_FIRMS (id: USGS:FIRMS)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_FIRMS_NASA(self):

        # Retrieve a list of MODIS burndate file .. check only one present
        remote_url='ftp://nrt1.modaps.eosdis.nasa.gov/FIRMS/Global'
        usr_pwd='jrcMondeFires:FIRE@data1'
        full_regex   ='Global_MCD14DL_201435..txt'
        file_to_check='Global_MCD14DL_2014350.txt'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)

        self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test iteration on ftp CHIRP (id: UCSB:CHIRP:DEKAD)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_CHIRP(self):
        # Retrieve a list of CHIRP
        remote_url='ftp://chg-ftpout.geog.ucsb.edu/pub/org/chg/products/CHIRP/pentads/'
        usr_pwd='anonymous:anonymous'
        full_regex   ='CHIRP.2014.12.[1-3].tif'
        file_to_check='CHIRP.2014.12.1.tif'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
        self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test iteration on ftp CHIRPS preliminary (id to be assigned)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_CHIRPS(self):
        # Retrieve a list of CHIRP
        remote_url='ftp://chg-ftpout.geog.ucsb.edu/pub/org/chg/products/CHIRPS-latest/prelim/global_pentad/tifs/'
        usr_pwd='anonymous:anonymous'
        full_regex   ='chirps-v1.8.*.tif'
        file_to_check='chirps-v1.8.2014.09.4.tif'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
        self.assertTrue(file_to_check in list)
    #   ---------------------------------------------------------------------------
    #   Test iteration on ftp CHIRPS (id:  UCSB:CHIRPS:DEKAD:2.0)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_CHIRPS_2_0(self):
        # Retrieve a list of CHIRP
        remote_url='ftp://chg-ftpout.geog.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/global_dekad/tifs/'
        usr_pwd='anonymous:anonymous'
        full_regex   ='chirps-v2.0.*.tif'
        file_to_check='chirps-v2.0.2015.02.1.tif.gz'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
        print(list)
        self.assertTrue(file_to_check in list)

     #   ---------------------------------------------------------------------------
    #   Test remote ftp NOAA GSOD (id: NOAA:GSOD)
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_NOAA_GSOD(self):

        # Retrieve a list of MODIS burndate file .. check only one present
        remote_url='ftp://ftp.ncdc.noaa.gov/pub/data/gsod/'
        usr_pwd='anonymous:'
        full_regex   ='2011/997...-99999-2011.op.gz'
        file_to_check='2011/997286-99999-2011.op.gz'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
        print(list)
        self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test remote ftp JRC
    #   ---------------------------------------------------------------------------
    def TestRemoteFtp_JRC(self):

        # Retrieve a list of MODIS burndate file .. check only one present
        remote_url='ftp://h05-ftp.jrc.it/'
        usr_pwd='narmauser:narma11'
        full_regex   ='eumetcast/'
        file_to_check='prod_descr_restore.txt'

        list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)

        self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test iteration on remote ftp (e.g. ARC2)
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_ARC2(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     remote_url='ftp://ftp.cpc.ncep.noaa.gov/fews/fewsdata/africa/arc2/geotiff/'
    #     usr_pwd='anonymous:@'
    #     full_regex   ='africa_arc.2015.....tif.zip'
    #     file_to_check='africa_arc.20150121.tif.zip'
    #
    #     list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
    #
    #     self.assertTrue(file_to_check in list)
    #
    # #   ---------------------------------------------------------------------------
    # #   Test iteration on remote ftp (e.g. CAMS_OPI)
    # #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_CAMS_OPI(self):
    #
    #     # Retrieve a list of CQMS-OPI .. check only one present
    #     remote_url='ftp://ftp.cpc.ncep.noaa.gov/precip/data-req/cams_opi_v0208/'
    #     usr_pwd='anonymous:@'
    #     full_regex   ='africa_arc.2015.....tif.zip'
    #     file_to_check='africa_arc.20150121.tif.zip'
    #
    #     list = get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex)
    #
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test iteration on remote ftp (e.g. VITO GL-GIO products): Obsolete ?
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
    #   Test download of files from GSFC oceandata http site (id:GSFC:OCEAN:MODIS:SST:1D)
    #   ---------------------------------------------------------------------------
    def TestRemoteHttp_MODIS_SST_1DAY(self):

        remote_url='http://oceandata.sci.gsfc.nasa.gov/'
        from_date= datetime.date(2015,1,1)
        to_date= datetime.date(2015,2,1)
        template='%Y/%j/A%Y%j.L3m_DAY_SST_4.bz2'
        usr_pwd='anonymous:anonymous'
        frequency='e1day'

        files_list = build_list_matching_for_http(remote_url, template, from_date, to_date, frequency)
        print(files_list)
        file_to_check='2015/001/A2015001.L3m_DAY_SST_4.bz2'

        self.assertTrue(file_to_check in files_list)

    #   ---------------------------------------------------------------------------
    #   Get list of files from FEWSNET HTTP (id: USGS:EARLWRN:FEWSNET)
    #   ---------------------------------------------------------------------------

    def TestRemoteHttp_FEWSNET(self):

        remote_url='http://earlywarning.usgs.gov/ftp2/raster/rf/a/'
        from_date = datetime.date(2014,1,1)
        to_date = datetime.date(2014,12,31)
        template='%Y/a%y%m%{dkm}rb.zip'         # Where are data for 2015 ??
        frequency = 'e1dekad'

        files_list = build_list_matching_for_http(remote_url, template, from_date, to_date, frequency)

        file_to_check='2014/a14121rb.zip'
        self.assertTrue(file_to_check in files_list)

    #   ---------------------------------------------------------------------------
    #   Test download of 8DAY data from GSFC oceandata http site (id:GSFC:OCEAN:MODIS:SST:1D)
    #   ---------------------------------------------------------------------------
    def TestRemoteHttp_MODIS_SST_1DAY(self):

        remote_url='http://oceandata.sci.gsfc.nasa.gov/MODISA/Mapped/Daily/4km/SST/'
        from_date = datetime.date(2014,1,1)
        to_date = datetime.date(2014,12,31)
        template='%Y/A%Y%j.L3m_DAY_SST_4.bz2'       # introduce non-standard placeholder
        usr_pwd='anonymous:anonymous'
        frequency = 'e1dekad'

        files_list = build_list_matching_for_http(remote_url, template, from_date, to_date, frequency)
        print files_list
        file_to_check='2014/A2014001.L3m_DAY_SST_4.bz2'
        self.assertTrue(file_to_check in files_list)

    #   ---------------------------------------------------------------------------
    #   Test download of Kd daily data from GSFC oceandata http site (id:GSFC:OCEAN:MODIS:KD:1D)
    #   ---------------------------------------------------------------------------
    def TestRemoteHttp_MODIS_KD_1DAY(self):

        remote_url='http://oceandata.sci.gsfc.nasa.gov/MODISA/Mapped/Daily/4km/Kd/'
        from_date = datetime.date(2014,1,1)
        to_date = datetime.date(2014,12,31)
        template='%Y/A%Y%j.L3m_DAY_KD490_Kd_490_4km.bz2'       # introduce non-standard placeholder
        usr_pwd='anonymous:anonymous'
        frequency = 'e1dekad'

        files_list = build_list_matching_for_http(remote_url, template, from_date, to_date, frequency)
        print files_list
        file_to_check='2014/A2014001.L3m_DAY_KD490_Kd_490_4km.bz2'
        self.assertTrue(file_to_check in files_list)

    #   ---------------------------------------------------------------------------
    #   Test download of MOD09 files from USGS http site (id:MOD09GA_Africa)
    #   ---------------------------------------------------------------------------
    def TestRemoteHttp_MOD09_GQ_005(self):

        remote_url='http://e4ftl01.cr.usgs.gov/MOLT/MOD09GQ.005/2000.02.24/'
        remote_url='http://earlywarning.usgs.gov/ftp2/raster/rf/a/2014/'
        usr_pwd='anonymous:anonymous'
        c=pycurl.Curl()
        import StringIO
        import cStringIO
        buffer = StringIO.StringIO()

        c.setopt(c.URL, remote_url)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        print c.getinfo(pycurl.HTTP_CODE)
        html = buffer.getvalue()

        file_to_check='2015/001/A2015001.L3m_DAY_SST_4.bz2'
        #results = re.search(r'(type="hidden" name="([0-9a-f]{32})")', html).group(2)

        #self.assertTrue(file_to_check in results)
