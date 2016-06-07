__author__ = "Marco Clerici"

import datetime
import proc_functions
from multiprocessing import Queue
# #   ---------------------------------------------------------------------
# # vgt-ndvi
# #   ---------------------------------------------------------------------
# from apps.processing.processing_std_ndvi import *
# productcode='vgt-ndvi'
# subproductcode='ndv'
# version='sv2-pv2.1'
# start_date='19990101'
# end_date='20141231'
# list_dates = proc_functions.get_list_dates_for_dataset(productcode, subproductcode, version, start_date=start_date, end_date=end_date)
#
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': productcode,\
#         'starting_sprod':subproductcode,\
#         'mapset': 'SPOTV-Africa-1km',\
#         'version': version,
#         'starting_dates': list_dates,
#         'logfile':'test_processing_ndvi'}
#
# res_queue = None
# processing_std_ndvi_prods_only(res_queue,**args)
#processing_std_ndvi_all(res_queue,**args)

#   ---------------------------------------------------------------------
# chirps-dekad
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_precip_monstats import *
# # # Create the list of dates -> returns empty if start==end==None
# # start_date='20110101'
# # end_date='20150901'
# # starting_dates = proc_functions.get_list_dates_for_dataset('chirps-dekad', '10d', '2.0',
# #                                                                start_date=start_date, end_date=end_date)
# #
# request_queue = Queue()
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'chirps-dekad',\
#         'starting_sprod':'10d',\
#         'starting_dates': None,\
#         'mapset': 'CHIRP-Africa-5km',\
#         'version':'2.0',
#         'logfile':'ruffus-chirps'}
#         #'write2file':'/tmp/eStation2/ruffus_chirps-dekad.txt'}
#
# proc_lists=processing_std_precip_all(request_queue, **args)
# print(proc_lists)
# #upsert_database(process_id, product_code, version, mapset, proc_lists, input_product_info)

#from apps.processing.processing_modis_sst import *
# #   ---------------------------------------------------------------------
# # pml-modis-sst
# #   ---------------------------------------------------------------------
# from apps.processing.processing_std_fronts import *
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'pml-modis-sst',\
#         'starting_sprod':'sst-3day',\
#         'mapset': 'SPOTV-IOC-1km',\
#         'version':'3.0',
#         'logfile':'pml-modis-sst'
#         }
# res_queue = None
# processing_std_fronts(res_queue, **args)
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
# args = {'pipeline_run_level':7, \
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
#         'mapset': 'MODIS-Africa-4km',\
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
#         'pipeline_printout_level':3, \
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
#         'pipeline_printout_level':3, \
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
# fewsnet-rfe
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_precip import *
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
# fewsnet-rfe
#   ---------------------------------------------------------------------
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
# target_mapset='SPOTV-CEMAC-1km'
#
# args = {'pipeline_run_level':6, \
#         'pipeline_printout_level':0, \
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
from apps.processing.processing_modis_firms import *
# Create the list of dates -> returns empty if start==end==None
# start_date='201510010000'
# end_date='201510102345'
starting_dates = None
# native_mapset='MSG-satellite-3km'
target_mapset='SPOTV-Africa-1km'

args = {'pipeline_run_level':5,
        'pipeline_printout_level':0,
        'pipeline_printout_graph_level': 0,
        'prod': 'modis-firms',
        'starting_sprod':'1day',
        'starting_dates': starting_dates,
        # 'native_mapset': native_mapset,
        'mapset': target_mapset,
        'version':'v5.0',
        'logfile':'log-lsasaf-lst.log',
        'update_stats' : True,
        'nrt_products' :True }

res_queue = None
proc_lists=processing_modis_firms(res_queue,**args)
print(proc_lists)
