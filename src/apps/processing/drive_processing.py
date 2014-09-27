__author__ = "Marco Clerici"


import time
from apps.processing.processing_switches import *

# General definitions/switches

args = {'pipeline_run_level':pipeline_run_level, \
        'pipeline_run_touch_only':pipeline_run_touch_only, \
        'pipeline_printout_level':pipeline_printout_level, \
        'pipeline_printout_graph_level':pipeline_printout_graph_level}

from apps.processing.processing_fewsnet import *
#from apps.processing.processing_ndvi import *

start = time.clock()

#   ---------------------------------------------------------------------
#   Run the pipeline

processing_fewsnet_rfe(**args)
# processing_vgt_ndvi(**args)