#
#	purpose: Test the ingest module
#	author:  M. Clerici
#	date:	 26.02.2014
#	history: 1.0
#
#   TODO-M.C.: replace 'native' everywhere with the mapset name (?!)

import shutil
import filecmp
#from nose import *  -> not working on Mac .. put on es2, anyhow

from config.es2 import *
from apps.acquisition import ingestion


class TestIngestion():

        # Definitions
        def __init__(self):
            pass

        def my_setup_function(self):
            pass

        def my_teardown_function(self):
            pass

        #@with_setup(my_setup_function, my_teardown_function)

        def test_ingest_vgt_ndvi_africa(self):

            # Definitions
            inputFiles = test_data_dir_in + 'V2KRNS10__20130701_NDVI__Africa.ZIP'

            out_file1 = test_data_dir_out + '20130701_VGT_NDVI_NDV_WGS84_Africa_1km.tif'
            ref_file1 = test_data_dir_ref + '20130701_VGT_NDVI_NDV_WGS84_Africa_1km_ref.tif'
            out_file2 = test_data_dir_out + '20130701_VGT_NDVI_SM_WGS84_Africa_1km.tif'
            ref_file2 = test_data_dir_ref + '20130701_VGT_NDVI_SM_WGS84_Africa_1km_ref.tif'

            # Dummy Definitions
            product = 'vgt_ndvi'
            sprod1 = {'subproduct': 'ndv', 're_extract': 'NDV', 're_process': 'NDV'}
            sprod2 = {'subproduct': 'sm', 're_extract': 'SM', 're_process': 'SM'}

            subproducts = (sprod1, sprod2, 0)

            # Target mapset -> should come from ingestion
            mapset = MapSet()
            mapset.assign_vgt4africa()
            # Get datasource_descr from db (returns eum_filter + dsd)
            for ds_filter, datasource_descr in queryDB.get_datasource_descr(echo=0, source_type='EUMETCAST', source_id='EO:EUM:DAT:SPOT:S10NDVI'):
                # Call ingestion routine (out_file to be removed ?)
                ingestion.ingestion(inputFiles, product, subproducts, mapset, datasource_descr, out_file1)

            # Compare output file1 (NDV)
            #assert filecmp.cmp(out_file1, ref_file1)

        def test_ingest_msg_mpe_native(self):

            # Definitions
            inputFiles=(test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000001___-201309040800-__',
            test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000002___-201309040800-__',
            test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000003___-201309040800-__',
            test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000004___-201309040800-__',
            test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-PRO______-201309040800-__')

            out_filename = '201309040800_MSG_MPE_MPE_native.tif'
            ref_filename = '201309040800_MSG_MPE_MPE_native_ref.tif'

            out_file = test_data_dir_out + out_filename
            ref_file = test_data_dir_ref + ref_filename

            # Dummy Definitions
            product = 'MSG_MPE'
            sprod1 = {'subproduct': 'MPE', 're_process':'', 're_expr': ''}

            subproducts = (sprod1, 0)

            # Target mapset -> should come from ingestion
            mapset = ''
            #mapset.assign_vgt4africa()
            # Get datasource_descr from db (returns eum_filter + dsd)
            for filter, datasource_descr in queryDB.get_datasource_descr(echo=1, source_type='EUMETCAST', source_id='EO:EUM:DAT:MSG:MPE-GRIB'):
                # Call ingestion routine (out_file to be removed ?)
                ingestion.ingestion(inputFiles, product, subproducts, mapset, datasource_descr, out_file)

            # Compare output file
            #assert filecmp.cmp(out_file, ref_file)

        def test_ingest_fewsnet_rfe_africa(self):

            # Definitions
            inputFiles=test_data_dir_in+'a10011rb.zip'

            out_filename = '20100101_FEWSNET_RFE_RFE_native.tif'
            ref_filename = '20100101_FEWSNET_RFE_RFE_native_ref.tif'

            out_file = test_data_dir_out + out_filename
            ref_file = test_data_dir_ref + ref_filename

            # Definitions for extracting products
            product = 'FEWSNET_RFE'
            sprod1 = {'subproduct': 'RFE', 're_process':'bil', 're_extract': 'rf'}

            subproducts = (sprod1, 0)
            target_mapset = MapSet()
            target_mapset.assign_vgt4africa()

            #for filter, datasource_descr in queryDB.get_datasource_descr(echo=1, source_type='EUMETCAST', source_id='EO:EUM:DAT:MSG:MPE-GRIB'):
                # Call ingestion routine (out_file to be removed ?)
            #    ingestion.ingestion(inputFiles, product, subproducts, mapset, datasource_descr, out_file)

            # Call ingestion routine
            ingestion.ingest_file(inputFiles, out_file, product, subproducts,'',native_mapset=native_mapset, unzip='zip')

            # Compare output file
            #assert filecmp.cmp(out_file, ref_file)

        def test_ingest_tamsat_rfe_africa(self):

            # Definitions
            inputFiles=test_data_dir_in+'rfe2013_01-dk1.nc'

            out_filename = '20130101_TAMSAT_RFE_RFE_native.tif'
            ref_filename = '20130101_TAMSAT_RFE_RFE_native_ref.tif'

            out_file = test_data_dir_out + out_filename
            ref_file = test_data_dir_ref + ref_filename

            # Definitions for extracting products
            product = 'TAMSAT_RFE'
            sprod1 = {'subproduct': 'RFE', 're_process':'', 're_extract': ''}

            subproducts = (sprod1, 0)
            mapset = ''
            for filter, datasource_descr in queryDB.get_datasource_descr(echo=1, source_type='EUMETCAST', source_id='EO:EUM:DAT:MSG:RFE'):
                # Call ingestion routine (out_file to be removed ?)
                ingestion.ingestion(inputFiles, product, subproducts, mapset, datasource_descr, out_file)

            # Compare output file
            #assert filecmp.cmp(out_file, ref_file)

        def test_ingest_amodis_chl_global(self):

            # Definitions
            inputFiles=test_data_dir_in+'A2002185.L3m_DAY_CHL_chlor_a_4km.bz2'

            out_filename = '20020704_MODIS_CHLA_DAY_CHL.tif'
            ref_filename = '20020704_MODIS_CHLA_DAY_CHL_ref.tif'

            out_file = test_data_dir_out + out_filename
            ref_file = test_data_dir_ref + ref_filename

            # Definitions for extracting products
            product = 'MODIS_CHLA'
            sprod1 = {'subproduct': 'chla_day', 're_process':'', 're_extract': ''}

            subproducts = (sprod1, 0)
            mapset = MapSet()
            mapset.assign_modis_global()

            for filter, datasource_descr in queryDB.get_datasource_descr(echo=1, source_type='EUMETCAST', source_id='EO:EUM:DAT:AQUA:CHLORA'):
                # Call ingestion routine (out_file to be removed ?)
                ingestion.ingestion(inputFiles, product, subproducts, mapset, datasource_descr, out_file)

            # Compare output file
            #assert filecmp.cmp(out_file, ref_file)

        def test_ingest_modis_ba_tile(self):

            # Definitions
            inputFiles = glob.glob(test_data_dir_in+'/MCD45A1*')

            out_filename = '20111201_MODIS_BA_BURNDATE_WGS84_Africa_1km.tif'
            ref_filename = '20111201_MODIS_BA_BURNDATE_WGS84_Africa_1km_ref.tif'

            out_file = test_data_dir_out + out_filename
            ref_file = test_data_dir_ref + ref_filename

            # Definitions for extracting products
            product = 'MODIS_BA'
            sprod1 = {'subproduct': 'BURNDATE', 're_process':'', 're_extract': ''}

            subproducts = (sprod1, 0)
            target_mapset = MapSet()
            target_mapset.assign_vgt4africa()

            # Note: the grib can be managed by python-gdal already !
            tmp_geotiff_file=ingestion.compose_regions('MODIS_HDF4_TILE', subproducts, inputFiles)

            # Call ingestion routine
            ingestion.ingest_file(tmp_geotiff_file, out_file, product, subproducts,target_mapset, unzip='')

            # Compare output file
            assert filecmp.cmp(out_file, ref_file)

        def test_ingest_modis_ndvi_tile(self):

            # Definitions TODO-M.C.: to be done/tested for Haiti/Bolivia
            inputFiles = glob.glob(test_data_dir_in+'/MOD13Q1*')

            #out_filename = '20111201_MODIS_BA_BURNDATE_WGS84_Africa_1km.tif'
            #ref_filename = '20111201_MODIS_BA_BURNDATE_WGS84_Africa_1km_ref.tif'

            out_file = test_data_dir_out + out_filename
            ref_file = test_data_dir_ref + ref_filename

            # Definitions for extracting products
            #product = 'MODIS_BA'
            #sprod1 = {'subproduct': 'BURNDATE', 're_process':'burndate', 're_extract': 'burndate'}

            subproducts = (sprod1, 0)
            target_mapset = MapSet()
            #target_mapset.assign_vgt4africa()

            # Note: the grib can be managed by python-gdal already !
            #tmp_geotiff_file=ingestion.compose_regions('MODIS_BA', subproducts, inputFiles, 'tiles')

            # Call ingestion routine
            #ingestion.ingest_file(tmp_geotiff_file, out_file, product, subproducts,target_mapset, unzip='')

            # Compare output file
            #assert filecmp.cmp(out_file, ref_file)

        def test_ingest_lsasaf_lst(self):

            # Definitions
            inputFiles = glob.glob(test_data_dir_in+'/S-LSA*MSG_LST*201402251200*')

            out_filename = '201402251200_LSASAF_LST_LST_Africa.tif'
            ref_filename = '201402251200_LSASAF_LST_LST_Africa_ref.tif'

            out_file = test_data_dir_out + out_filename
            ref_file = test_data_dir_ref + ref_filename

            # Definitions for extracting products
            product = 'LSASAF_LST'
            sprod1 = {'subproduct': 'lst', 're_process':'lst', 're_extract': 'LST'}
            mapset = ''
            subproducts = (sprod1, 0)
            for filter, datasource_descr in queryDB.get_datasource_descr(echo=1, source_type='EUMETCAST', source_id='EO:EUM:DAT:MSG:LST-SEVIRI'):
                # Call ingestion routine (out_file to be removed ?)
                ingestion.ingestion(inputFiles, product, subproducts, mapset, datasource_descr, out_file)


        def test_ingest_modis_ba_windows(self):

            # TODO-M.C.: move to 500m resolution in output (now it gives Memory Error)
            # Definitions
            inputFiles = glob.glob(test_data_dir_in+'/MCD45monthly*2005274*')

            out_filename = '20110401_MODIS_BA_BURNDATE_WGS84_Africa_1km.tif'
            ref_filename = '20110401_MODIS_BA_BURNDATE_WGS84_Africa_1km_ref.tif'

            out_file = test_data_dir_out + out_filename
            ref_file = test_data_dir_ref + ref_filename

            # Definitions for extracting products
            product = 'MODIS_BA_WINDOW'
            sprod1 = {'subproduct': 'BURNDATE', 're_process':'burndate_glb', 're_extract': 'burndate'}

            subproducts = (sprod1, 0)

            target_mapset = MapSet()
            target_mapset.assign_vgt4africa()

            # Compose Regions
            tmp_geotiff_file=ingestion.compose_regions('MODIS_TIF_WINDOW', subproducts, inputFiles)
            # Call ingestion routine
            ingestion.ingest_file(tmp_geotiff_file, out_file, product, subproducts,target_mapset,
                                  unzip='')

            # Compare output file
            #assert filecmp.cmp(out_file, ref_file)
