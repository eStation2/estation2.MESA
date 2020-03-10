from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = "Marco Clerici"

#   ---------------------------------------------------------------------
# chla gradient
#   ---------------------------------------------------------------------
from apps.processing.processing_std_gradient import *
def test_proc_olci_wrr_chla_gradient(pipe_run=0, pipe_print=3, touch_files_only=False):

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'olci-wrr',\
            'starting_sprod':'chl-oc4me',\
            'mapset': 'SPOTV-Africa-1km',\
            'version':'V02.0',
            'logfile':'olci-wrr',
            'touch_files_only':touch_files_only
            }
    res_queue = None

    processing_std_gradient(res_queue, **args)


test_proc_olci_wrr_chla_gradient(pipe_run=3, pipe_print=0, touch_files_only=False)