__author__ = "Marco Clerici"

import datetime
import proc_functions
# #   ---------------------------------------------------------------------
# # vgt-ndvi
# #   ---------------------------------------------------------------------
# from apps.processing.processing_std_ndvi import *
# args = {'pipeline_run_level':4, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'vgt-ndvi',\
#         'starting_sprod':'ndv',\
#         'mapset': 'SPOTV-Africa-1km',\
#         'version':'sv2-pv2.1'
#         }
# # processing_std_ndvi(**args)
# #processing_std_ndvi_stats_only(**args)
# processing_std_ndvi_prods_only(**args)

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
# args = {'pipeline_run_level':5, \
#         'pipeline_printout_level':0, \
#         'pipeline_printout_graph_level': 0, \
#         'prod': 'chirps-dekad',\
#         'starting_sprod':'10d',\
#         'starting_dates': starting_dates,\
#         'mapset': 'CHIRP-Africa-5km',\
#         'version':'2.0'}
#         #'write2file':'/tmp/eStation2/ruffus_chirps-dekad.txt'}
#
# proc_lists=processing_std_precip_prods_only(**args)
#print(proc_lists)
#upsert_database(process_id, product_code, version, mapset, proc_lists, input_product_info)

#from apps.processing.processing_modis_sst import *
#   ---------------------------------------------------------------------
# modis-sst
#   ---------------------------------------------------------------------
from apps.processing.processing_std_fronts import *
args = {'pipeline_run_level':5, \
        'pipeline_printout_level':0, \
        'pipeline_printout_graph_level': 0, \
        'prod': 'modis-sst',\
        'starting_sprod':'sst-day',\
        'mapset': 'MODIS-Africa-4km',\
        'version':'v2013.1'
        }
processing_std_fronts(**args)
