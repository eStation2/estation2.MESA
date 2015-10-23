__author__ = "Marco Clerici"

import datetime
import proc_functions
from multiprocessing import Queue
# # #   ---------------------------------------------------------------------
# # # vgt-ndvi
# # #   ---------------------------------------------------------------------
# from apps.processing.processing_std_ndvi import *
# args = {'pipeline_run_level':3, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'vgt-ndvi',\
#         'starting_sprod':'ndv',\
#         'mapset': 'SPOTV-Africa-1km',\
#         'version':'sv2-pv2.1',
#         'logfile':'test_processing'}
# # processing_std_ndvi(**args)
# #processing_std_ndvi_stats_only(**args)
# res_queue = None
# processing_std_ndvi_prods_only(res_queue,**args)

#   ---------------------------------------------------------------------
# chirps-dekad
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_precip import *
# # Create the list of dates -> returns empty if start==end==None
# start_date='20110101'
# end_date='20150901'
# starting_dates = proc_functions.get_list_dates_for_dataset('chirps-dekad', '10d', '2.0',
#                                                                start_date=start_date, end_date=end_date)
#
# request_queue = Queue()
# args = {'pipeline_run_level':0, \
#         'pipeline_printout_level':3, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'chirps-dekad',\
#         'starting_sprod':'10d',\
#         'starting_dates': starting_dates,\
#         'mapset': 'CHIRP-Africa-5km',\
#         'version':'2.0',
#         'logfile':'ruffus-fewsnet'}
#         #'write2file':'/tmp/eStation2/ruffus_chirps-dekad.txt'}
#
# proc_lists=processing_std_precip_prods_only(request_queue, **args)
#print(proc_lists)
#upsert_database(process_id, product_code, version, mapset, proc_lists, input_product_info)

#from apps.processing.processing_modis_sst import *
#   ---------------------------------------------------------------------
# modis-sst
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_fronts import *
# args = {'pipeline_run_level':5, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'modis-sst',\
#         'starting_sprod':'sst-day',\
#         'mapset': 'MODIS-Africa-4km',\
#         'version':'v2013.1'
#         }
# processing_std_fronts(**args)
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
#
# proc_lists=processing_std_precip_prods_only(**args)
# print(proc_lists)
#   ---------------------------------------------------------------------
# fewsnet-rfe
#   ---------------------------------------------------------------------
from apps.processing.processing_std_precip import *
# Create the list of dates -> returns empty if start==end==None
#start_date='20010101'
#end_date='20141221'
#starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0', start_date=start_date, end_date=end_date)
starting_dates = None
args = {'pipeline_run_level':3, \
        'pipeline_printout_level':0, \
        'pipeline_printout_graph_level': 0, \
        'prod': 'tamsat-rfe',\
        'starting_sprod':'10d',\
        'starting_dates': starting_dates,\
        'mapset': 'TAMSAT-Africa-4km',\
        'version':'2.0',
        'logfile':'log-tamsat.log'}

res_queue = None
proc_lists=processing_std_precip_prods_only(res_queue,**args)
print(proc_lists)
