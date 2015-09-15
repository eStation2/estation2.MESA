__author__ = "Marco Clerici"

# General definitions/switches
args = {'pipeline_run_level':4, \
        'pipeline_run_touch_only':0, \
        'pipeline_printout_level':0, \
        'pipeline_printout_graph_level': 0, \
        'prod': 'vgt-ndvi',\
        'starting_sprod':'ndv',\
        'mapset': 'SPOTV-Africa-1km',\
        'version':'sv2-pv2.1'
        }

#from apps.processing.processing_modis_sst import *
#from apps.processing.processing_std_precip import *
from apps.processing.processing_std_ndvi import *
#   ---------------------------------------------------------------------
#   Run the pipeline

#processing_std_ndvi(**args)
#processing_std_ndvi_stats_only(**args)
processing_std_ndvi_prods_only(**args)
#processing_std_ndvi_prods_only(**args)