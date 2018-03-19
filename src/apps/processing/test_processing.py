__author__ = "Marco Clerici"

import datetime, os
import proc_functions
from multiprocessing import Queue
#   ---------------------------------------------------------------------
# vgt-ndvi
#   ---------------------------------------------------------------------

# from apps.processing.processing_std_ndvi import *
# productcode='vgt-ndvi'
# subproductcode='ndv'
# version='sv2-pv2.2'
# start_date='19990101'
# end_date='20161231'
#
# list_dates = proc_functions.get_list_dates_for_dataset(productcode, subproductcode, version, start_date=start_date, end_date=end_date)
#
# args = {'pipeline_run_level':1, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': productcode,\
#         'starting_sprod':subproductcode,\
#         'mapset': 'SPOTV-Africa-1km',\
#         'version': version,
#         'starting_dates': list_dates,
#         'logfile':'test_processing_ndvi',
#         'touch_files_only':False}
#
#
# res_queue = None
# processing_std_ndvi_prods_only(res_queue,**args)

#   ---------------------------------------------------------------------
# vgt-ndvi merge (for sv2-pv2.2)
#   ---------------------------------------------------------------------
# from apps.processing.processing_merge import *
#
# process_id = 51
# input_products = querydb.get_processing_chain_products(process_id,type='input')
# output_products = querydb.get_processing_chain_products(process_id,type='output')
#
# args = {'pipeline_run_level':0, \
#         'pipeline_printout_level':3, \
#         'input_products': input_products,\
#         'output_product':output_products,\
#         'mapset': 'SPOTV-Africa-1km'}
#
# res_queue = None
# processing_merge(**args)

#   ---------------------------------------------------------------------
# pml-modis-sst
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_fronts import *
# def test_proc_pml_modis_fronts(pipe_run=0, pipe_print=3, touch_files_only=False):
#
#     args = {'pipeline_run_level':pipe_run, \
#             'pipeline_printout_level':pipe_print, \
#             'pipeline_printout_graph_level': 0, \
#             'prod': 'pml-modis-sst',\
#             'starting_sprod':'sst-3day',\
#             'mapset': 'SPOTV-IOC-1km',\
#             'version':'3.0',
#             'logfile':'pml-modis-sst',
#             'touch_files_only':touch_files_only
#             }
#     res_queue = None
#     processing_std_fronts(res_queue, **args)
#   ---------------------------------------------------------------------
# modis-sst
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_fronts import *
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'pml_modis-sst',\
#         'starting_sprod':'sst-day',\
#         'mapset': 'MODIS-Africa-4km',\
#         'version':'v2013.1',
#         'logfile':'modis-sst'
#         }
# res_queue = None
# processing_std_fronts(res_queue, **args)
#   ---------------------------------------------------------------------
# modis-chla
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_modis_monavg import *
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'modis-chla',\
#         'starting_sprod':'chla-day',\
#         'mapset': 'MODIS-Africa-4km',\
#         'version':'v2013.1',
#         'logfile':'modis-chla'
#         }
# res_queue = None
# processing_std_modis_monavg(res_queue, **args)

#   ---------------------------------------------------------------------
# modis-sst monavg
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_modis_monavg import *
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'modis-sst',\
#         'starting_sprod':'sst-day',\
#         'mapset': 'MODIS-Global-4km',\
#         'version':'v2013.1',
#         'logfile':'modis-sst'
#         }
# res_queue = None
# processing_std_modis_monavg(res_queue, **args)
#   ---------------------------------------------------------------------
# modis-par monavg
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_modis_monavg import *
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'modis-par',\
#         'starting_sprod':'par-day',\
#         'mapset': 'MODIS-Africa-4km',\
#         'version':'v2012.0',
#         'logfile':'modis-par'
#         }
# res_queue = None
# processing_std_modis_monavg(res_queue, **args)
#   ---------------------------------------------------------------------
# modis-kd490 monavg
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_modis_monavg import *
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'modis-kd490',\
#         'starting_sprod':'kd490-day',\
#         'mapset': 'MODIS-Africa-4km',\
#         'version':'v2012.0',
#         'logfile':'modis-kd490'
#         }
# res_queue = None
# processing_std_modis_monavg(res_queue, **args)
#   ---------------------------------------------------------------------
# modis-pp computation - NON standard
#   ---------------------------------------------------------------------
# from apps.processing.processing_modis_pp import *
#
# derivation_method = 'modis_pp'
# algorithm = 'modis_pp'
# mapset = 'MODIS-Africa-4km'
# process_id = 62
#
# # Get input products
# input_products = querydb.get_processing_chain_products(process_id,type='input')
# output_products = querydb.get_processing_chain_products(process_id,type='output')
#
# # Prepare arguments
# args = {'pipeline_run_level':3,
#         'pipeline_printout_level':0,
#         'input_products': input_products,
#         'output_product': output_products,
#         'logfile': 'test_processing.log'}
#
# res_queue = None
# processing_modis_pp(res_queue, **args)

# #
#   ---------------------------------------------------------------------
# tamsat-rfe
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_precip import *
# # # Create the list of dates -> returns empty if start==end==None
# # #start_date='20010101'
# # #end_date='20141221'
# # #starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0', start_date=start_date, end_date=end_date)
# starting_dates = None
# args = {'pipeline_run_level':0, \
#         'pipeline_printout_level':3, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'tamsat-rfe',\
#         'starting_sprod':'10d',\
#         'starting_dates': starting_dates,\
#         'mapset': 'TAMSAT-Africa-4km',\
#         'version':'2.0',
#         'logfile':'log-tamsat.log'}
#
# res_queue = None
# proc_lists=processing_std_precip_prods_only(res_queue,**args)
# print(proc_lists)

#   ---------------------------------------------------------------------
# fewsnet-rfe
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_precip_new import *
# # Create the list of dates -> returns empty if start==end==None
# #start_date='20010101'
# #end_date='20141221'
# #starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0', start_date=start_date, end_date=end_date)
# starting_dates = None
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'fewsnet-rfe',\
#         'starting_sprod':'10d',\
#         'starting_dates': starting_dates,\
#         'mapset': 'FEWSNET-Africa-8km',\
#         'version':'2.0',
#         'logfile':'log-fewsnet.log'}
#
# res_queue = None
# proc_lists=processing_std_precip_prods_only(res_queue,**args)
# print(proc_lists)
#   ---------------------------------------------------------------------
# chirps-dekad
#   ---------------------------------------------------------------------
from apps.processing.processing_std_precip import *
def test_proc_chirps_dekad(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('chirps-dekad', '10d', '2.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'chirps-dekad',\
            'starting_sprod':'10d',\
            'starting_dates': starting_dates,\
            'mapset': 'CHIRP-Africa-5km',\
            'version':'2.0',
            'logfile':'ruffus-chirps',
            'touch_only':touch_files_only}

    request_queue = Queue()
    proc_lists=processing_std_precip_all(request_queue, **args)

#   ---------------------------------------------------------------------
# lsasaf-et
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_lsasaf_et import *
# # # Create the list of dates -> returns empty if start==end==None
# # start_date='201510010000'
# # end_date='201510102345'
# # starting_dates = proc_functions.get_list_dates_for_dataset('lsasaf-et', 'et', 'undefined', start_date=start_date, end_date=end_date)
# starting_dates = None
# native_mapset='MSG-satellite-3km'
# target_mapset='SPOTV-Africa-1km'
#
# args = {'pipeline_run_level':0, \
#         'pipeline_printout_level':3, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'lsasaf-et',\
#         'starting_sprod':'et',\
#         'starting_dates': starting_dates,\
#         'native_mapset': native_mapset,\
#         'mapset': target_mapset,\
#         'version':'undefined',
#         'logfile':'log-lsasaf-et.log'}
#
# res_queue = None
# proc_lists=processing_std_lsasaf_et(res_queue,**args)
# print(proc_lists)
#   ---------------------------------------------------------------------
# lsasaf-lst
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_lsasaf_lst import *
# # Create the list of dates -> returns empty if start==end==None
# # start_date='201510010000'
# # end_date='201510102345'
# # starting_dates = proc_functions.get_list_dates_for_dataset('lsasaf-lst', 'lst', 'undefined', start_date=start_date, end_date=end_date)
# starting_dates = None
# native_mapset='MSG-satellite-3km'
# target_mapset='SPOTV-CEMAC-1km'
#
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'lsasaf-lst',\
#         'starting_sprod':'lst',\
#         'starting_dates': starting_dates,\
#         'native_mapset': native_mapset,\
#         'mapset': target_mapset,\
#         'version':'undefined',
#         'logfile':'log-lsasaf-lst.log'}
#
# res_queue = None
# proc_lists=processing_std_lsasaf_lst(res_queue,**args)
# print(proc_lists)
#   ---------------------------------------------------------------------
# modis-firms
#   ---------------------------------------------------------------------
from apps.processing.processing_std_modis_firms import *
def test_proc_modis_firms(start_date=None, end_date=None, pipe_run=0, pipe_print=3, start_date_stats=None, end_date_stats=None, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('modis-firms', '1day', 'v6.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    if start_date_stats is not None and end_date_stats is not None:
        starting_dates_stats = proc_functions.get_list_dates_for_dataset('modis-firms', '10dcount', 'v6.0', start_date=start_date_stats, end_date=end_date_stats)
    else:
        starting_dates_stats = None

    target_mapset='SPOTV-Africa-1km'

    touch_files_only=False

    args = {'pipeline_run_level':pipe_run,
            'pipeline_printout_level':pipe_print,
            'pipeline_printout_graph_level': 0,
            'prod': 'modis-firms',
            'starting_sprod':'1day',
            'starting_dates': starting_dates,
            'starting_dates_stats': starting_dates_stats,
            'mapset': target_mapset,
            'version':'v6.0',
            'logfile':'log-modis-firms.log',
            'update_stats' : False,
            'nrt_products' : True,
            'touch_files_only':touch_files_only}

    res_queue = None
    proc_lists=processing_std_modis_firms(res_queue,**args)
    print(proc_lists)
# ---------------------------------------------------------------------
# msg-mpe
#   ---------------------------------------------------------------------
from apps.processing.processing_std_msg_mpe import *
# # # Create the list of dates -> returns empty if start==end==None

#print(proc_lists)
#   ---------------------------------------------------------------------
# onset computation
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_rain_onset import *
# start_date='20160901'
# end_date = '20161011'
# starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0',
#                                                            start_date=start_date, end_date=end_date)
#
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'fewsnet-rfe',\
#         'starting_sprod':'10d',\
#         'mapset': 'FEWSNET-Africa-8km',\
#         'version':'2.0',
#         'logfile':'rain-onset',
#         'starting_dates':starting_dates
#         }
# res_queue = None
# processing_std_rain_onset(res_queue, **args)


#   ---------------------------------------------------------------------
# arc2-rain cumulate
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_precip_1day import *
# # # # # # # Create the list of dates -> returns empty if start==end==None
# # # #
# start_date='20160101'
# end_date = '20170601'
# starting_dates = proc_functions.get_list_dates_for_dataset('arc2-rain','1day', '2.0', start_date=start_date, end_date=end_date)
# # starting_dates = None
# mapset='ARC2-Africa-11km'
# # #
# args = {'pipeline_run_level':0, \
#         'pipeline_printout_level':3, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'arc2-rain',\
#         'starting_sprod':'1day',\
#         'starting_dates': starting_dates,\
#         'mapset': mapset,\
#         'version':'2.0',
#         'logfile':'log-arc2-rain.log'}
#
# res_queue = None
# proc_lists=processing_std_precip_1day(res_queue,**args)
# print(proc_lists)

#   ---------------------------------------------------------------------
# arc2-rain SPI
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_spi_monthly import *
# # # # # Create the list of dates -> returns empty if start==end==None
# #
# #start_date='19830301'
# #end_date = '19830310'
# #starting_dates = proc_functions.get_list_dates_for_dataset('arc2-rain','1day', '2.0', start_date=start_date, end_date=end_date)
# starting_dates = None
# mapset='ARC2-Africa-11km'
# # #
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'arc2-rain',\
#         'starting_sprod':'1mon',\
#         'starting_dates': starting_dates,\
#         'mapset': mapset,\
#         'version':'2.0',
#         'logfile':'log-arc2-rain.log'}
#
# res_queue = None
# proc_lists=processing_std_spi_monthly(res_queue,**args)
# print(proc_lists)
#   ---------------------------------------------------------------------
# seas cumulation computation
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_seas_cum import *
# # start_date='20150901'
# # end_date = '20160621'
# # starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0',
# #                                                            start_date=start_date, end_date=end_date)
# starting_dates=None
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'fewsnet-rfe',\
#         'starting_sprod':'10d',\
#         'mapset': 'FEWSNET-Africa-8km',\
#         'version':'2.0',
#         'logfile':'cum.log',
#         'trg_mapset': 'SPOTV-SADC-1km',\
#         'starting_dates':starting_dates
#         }
# res_queue = None
# processing_std_seas_cum(res_queue, **args)
#   ---------------------------------------------------------------------
#   GSOD
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_gsod import *
# start_date='20160503'
# end_date = '20160505'
# starting_dates = proc_functions.get_list_dates_for_dataset('gsod-rain', '1dmeas', '1.0',
#                                                             start_date=start_date, end_date=end_date)
# args = {'pipeline_run_level':6, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'gsod-rain',\
#         'starting_sprod':'1dmeas',\
#         'mapset': 'SPOTV-SADC-1km',\
#         'version':'1.0',
#         'logfile':'gsod.log',
#         'starting_dates':starting_dates
#         }
# res_queue = None
# processing_std_gsod(res_queue, **args)

#   ---------------------------------------------------------------------
#   Calls
#   ---------------------------------------------------------------------

#test_proc_pml_modis_fronts(pipe_run=4, pipe_print=0, touch_files_only=False)
#test_proc_modis_firms(pipe_run=4, pipe_print=0, start_date_stats='20030101', end_date_stats='20161221', touch_files_only=True)
test_proc_chirps_dekad(pipe_run=3, pipe_print=0, start_date=None, end_date=None, touch_files_only=False)

# my_starting_dates_stats = proc_functions.get_list_dates_for_dataset('modis-firms', '10dcount', 'v6.0', start_date='20020701', end_date='20170821')
# for date in my_starting_dates_stats:
#     filename='/data/processing/modis-firms/v6.0/SPOTV-Africa-10km/derived/10dcount10k/'+date+'_modis-firms_10dcount10k_SPOTV-Africa-10km_v6.0.tif'
#     st=os.system('touch '+filename)
