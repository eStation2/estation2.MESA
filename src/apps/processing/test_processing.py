__author__ = "Marco Clerici"

# General definitions/switches
args = {'pipeline_run_level':0, \
        'pipeline_run_touch_only':0, \
        'pipeline_printout_level':6, \
        'pipeline_printout_graph_level': 0}

#from apps.processing.processing_modis_sst import *
#from apps.processing.processing_std_precip import *
from apps.processing.processing_std_ndvi import *
#   ---------------------------------------------------------------------
#   Run the pipeline

processing_std_ndvi(**args)
