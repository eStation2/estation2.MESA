from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
__author__ = "Marco Clerici"

from apps.processing import proc_functions
from multiprocessing import Queue
#   ---------------------------------------------------------------------
# vgt-ndvi
#   ---------------------------------------------------------------------
from apps.processing.processing_std_ndvi import *
def my_proc_std_ndvi(pipe_run=0, pipe_print=3, touch_files_only=False):
    #(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):

    productcode='vgt-ndvi'
    subproductcode='ndv'
    version='sv2-pv2.2'
    start_date='20180101'
    end_date=None

    list_dates = proc_functions.get_list_dates_for_dataset(productcode, subproductcode, version, start_date=start_date, end_date=end_date)

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': productcode,\
            'starting_sprod':subproductcode,\
            'mapset': 'SPOTV-Africa-1km',\
            'version': version,
            'starting_dates': list_dates,
            'logfile':'test_processing_ndvi',
            'touch_files_only':touch_files_only}

    #res_queue = Queue()
    res_queue = None
    proc_lists = processing_std_ndvi_prods_only(res_queue,**args)
    # proc_lists = processing_std_ndvi_stats_only(res_queue,**args)
    #proc_lists = processing_std_ndvi_all(res_queue,**args)

#   ---------------------------------------------------------------------
# vgt-ndvi merge (for sv2-pv2.2)
#   ---------------------------------------------------------------------
from apps.processing.processing_merge import *
def my_proc_ndvi_merge(pipe_run=0, pipe_print=3, touch_files_only=False):

    process_id = 51
    input_products = querydb.get_processing_chain_products(process_id,type='input')
    output_products = querydb.get_processing_chain_products(process_id,type='output')

    args = {'pipeline_run_level':0, \
            'pipeline_printout_level':3, \
            'input_products': input_products,\
            'output_product':output_products,\
            'mapset': 'SPOTV-Africa-1km'}

    res_queue = None
    processing_merge(**args)

#   ---------------------------------------------------------------------
# pml-modis-sst
#   ---------------------------------------------------------------------
from apps.processing.processing_std_fronts import *
def my_proc_pml_modis_fronts(pipe_run=0, pipe_print=3, touch_files_only=False):

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'pml-modis-sst',\
            'starting_sprod':'sst-3day',\
            'mapset': 'SPOTV-IOC-1km',\
            'version':'3.0',
            'logfile':'pml-modis-sst',
            'touch_files_only':touch_files_only
            }
    res_queue = None
    processing_std_fronts(res_queue, **args)
#   ---------------------------------------------------------------------
# modis-sst
#   ---------------------------------------------------------------------
from apps.processing.processing_std_fronts import *
def my_proc_std_fronts(pipe_run=0, pipe_print=3, touch_files_only=False):
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'pml_modis-sst',\
            'starting_sprod':'sst-day',\
            'mapset': 'MODIS-Africa-4km',\
            'version':'v2013.1',
            'logfile':'modis-sst'
            }
    res_queue = None
    processing_std_fronts(res_queue, **args)

#   ---------------------------------------------------------------------
# modis-chla
#   ---------------------------------------------------------------------
from apps.processing.processing_std_modis_monavg import *
def my_proc_std_modis_chla(pipe_run=0, pipe_print=3, touch_files_only=False):
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'modis-chla',\
            'starting_sprod':'chla-day',\
            'mapset': 'MODIS-Africa-4km',\
            'version':'v2013.1',
            'logfile':'modis-chla'
            }
    res_queue = None
    processing_std_modis_monavg(res_queue, **args)

#   ---------------------------------------------------------------------
# modis-sst monavg
#   ---------------------------------------------------------------------
from apps.processing.processing_std_modis_monavg import *
def my_proc_std_modis_sst(pipe_run=0, pipe_print=3, touch_files_only=False):

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'modis-sst',\
            'starting_sprod':'sst-day',\
            'mapset': 'MODIS-Global-4km',\
            'version':'v2013.1',
            'logfile':'modis-sst'
            }
    res_queue = None
    processing_std_modis_monavg(res_queue, **args)

#   ---------------------------------------------------------------------
# modis-par monavg
#   ---------------------------------------------------------------------
from apps.processing.processing_std_modis_monavg import *
def my_proc_std_modis_par(pipe_run=0, pipe_print=3, touch_files_only=False):

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'modis-par',\
            'starting_sprod':'par-day',\
            'mapset': 'MODIS-Africa-4km',\
            'version':'v2012.0',
            'logfile':'modis-par'
            }
    res_queue = None
    processing_std_modis_monavg(res_queue, **args)

#   ---------------------------------------------------------------------
# modis-kd490 monavg
#   ---------------------------------------------------------------------
from apps.processing.processing_std_modis_monavg import *
def my_proc_std_modis_kd490(pipe_run=0, pipe_print=3, touch_files_only=False):
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'modis-kd490',\
            'starting_sprod':'kd490-day',\
            'mapset': 'MODIS-Africa-4km',\
            'version':'v2012.0',
            'logfile':'modis-kd490'
            }
    res_queue = None
    processing_std_modis_monavg(res_queue, **args)

#   ---------------------------------------------------------------------
# modis-pp computation - NON standard
#   ---------------------------------------------------------------------
from apps.processing.processing_modis_pp import *
def my_proc_modis_pp(pipe_run=0, pipe_print=3, touch_files_only=False):
    derivation_method = 'modis_pp'
    algorithm = 'modis_pp'
    mapset = 'MODIS-Africa-4km'
    process_id = 62

    # Get input products
    input_products = querydb.get_processing_chain_products(process_id,type='input')
    output_products = querydb.get_processing_chain_products(process_id,type='output')

    # Prepare arguments
    args = {'pipeline_run_level':pipe_run,
            'pipeline_printout_level':pipe_print,
            'input_products': input_products,
            'output_product' : output_products,
            'logfile': 'test_processing.log',
            'nrt_products' : False,
            'update_stats' : True
            }

    res_queue = None
    processing_modis_pp(res_queue, **args)

#   ---------------------------------------------------------------------
# olci-wrr median filter
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_median_filter import *
# def my_proc_std_median_filter(pipe_run=0, pipe_print=3, touch_files_only=False):
#     start_date = '20181125'
#     end_date = '20181201'
#     starting_dates = proc_functions.get_list_dates_for_dataset('olci-wrr', 'chl-oc4me', 'V02.0',
#                                                                start_date=start_date, end_date=end_date)
#
#     args = {'pipeline_run_level':pipe_run, \
#             'pipeline_printout_level':pipe_print, \
#             'pipeline_printout_graph_level': 0, \
#             'prod': 'olci-wrr',\
#             'starting_sprod':'chl-oc4me',\
#             'mapset': 'SPOTV-Africa-1km',\
#             'version':'V02.0',
#             'logfile':'olci-wrr',
#             'starting_dates':starting_dates
#             }
#     res_queue = None
#     processing_std_median_filter(res_queue, **args)
#   ---------------------------------------------------------------------
# tamsat-rfe
#   ---------------------------------------------------------------------
from apps.processing.processing_std_precip import *
def my_proc_tamsat_rfe(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('tamsat-rfe', '10d', '3.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'tamsat-rfe',\
            'starting_sprod':'10d',\
            'starting_dates': starting_dates,\
            'mapset': 'TAMSAT-Africa-4km',\
            'version':'3.0',
            'logfile':'log-tamsat.log'}

    res_queue = None
    proc_lists=processing_std_precip_stats_only(res_queue,**args)
    print (proc_lists)

#   ---------------------------------------------------------------------
# fewsnet-rfe
#   ---------------------------------------------------------------------
from apps.processing.processing_std_precip import *
def my_proc_fewsnet_rfe(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):
    # Create the list of dates -> returns empty if start==end==None
    #start_date='20010101'
    #end_date='20141221'
    #starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0', start_date=start_date, end_date=end_date)
    starting_dates = None
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'fewsnet-rfe',\
            'starting_sprod':'10d',\
            'starting_dates': starting_dates,\
            'mapset': 'FEWSNET-Africa-8km',\
            'version':'2.0',
            'logfile':'log-fewsnet.log'}

    res_queue = None
    proc_lists=processing_std_precip_prods_only(res_queue,**args)
    print (proc_lists)

def my_proc_fewsnet_rfe(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'fewsnet-rfe',\
            'starting_sprod':'10d',\
            'starting_dates': starting_dates,\
            'mapset': 'FEWSNET-Africa-8km',\
            'version':'2.0',
            'logfile':'log-fewsnet.log'}

    res_queue = None
    proc_lists=processing_std_precip_stats_only(res_queue,**args)
    print (proc_lists)

#   ---------------------------------------------------------------------
# chirps-dekad
#   ---------------------------------------------------------------------
from apps.processing.processing_std_precip import *
def my_proc_chirps_dekad(pipe_run=0, pipe_print=3, start_date=None, end_date=None, upsert_db=False, touch_files_only=False):

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
            'upsert_db': upsert_db,
            'touch_only':touch_files_only}

    request_queue = Queue()
    proc_lists=processing_std_precip_stats_only(request_queue, **args)
    # proc_lists = processing_std_precip_prods_only(request_queue, **args)


def my_proc_arc2rain_dekad(pipe_run=0, pipe_print=3, start_date=None, end_date=None, upsert_db=False, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('chirps-dekad', '10d', '2.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'arc2-rain',\
            'starting_sprod':'10d',\
            'starting_dates': starting_dates,\
            'mapset': 'CHIRP-Africa-5km',\
            'version':'2.0',
            'logfile':'ruffus-chirps',
            'upsert_db': upsert_db,
            'touch_only':touch_files_only}

    request_queue = Queue()
    proc_lists=processing_std_precip_stats_only(request_queue, **args)

#   ---------------------------------------------------------------------
# chirps-lp
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_precip_lp import *
# def my_proc_chirps_lp(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False, type=''):
#
#     # Create the list of dates -> returns empty if start==end==None
#     if start_date is not None and end_date is not None:
#         starting_dates = proc_functions.get_list_dates_for_dataset('chirps-dekad', '1moncum', '2.0', start_date=start_date, end_date=end_date)
#     else:
#         starting_dates = None
#
#     args = {'pipeline_run_level':pipe_run, \
#             'pipeline_printout_level':pipe_print, \
#             'pipeline_printout_graph_level': 0, \
#             'prod': 'chirps-dekad',\
#             'starting_sprod':'1moncum',\
#             'starting_dates': starting_dates,\
#             'mapset': 'CHIRP-Africa-5km',\
#             'version':'2.0',
#             'logfile':'ruffus-chirps',
#             'touch_only':touch_files_only}
#
#     request_queue = Queue()
#     if type == 'prods':
#         proc_lists=processing_std_precip_lp_prods(request_queue, **args)
#     elif type == 'stats':
#         proc_lists=processing_std_precip_lp_stats(request_queue, **args)
#     elif type == 'anoms':
#         proc_lists=processing_std_precip_lp_anoms(request_queue, **args)

#   ---------------------------------------------------------------------
# lsasaf-et
#   ---------------------------------------------------------------------
from apps.processing.processing_std_lsasaf_et import *
def my_proc_std_lsasaf_et(pipe_run=3, pipe_print=0, start_date=None, end_date=None, touch_files_only=False):

    # # Create the list of dates -> returns empty if start==end==None
    if (start_date) or (end_date):
        starting_dates = proc_functions.get_list_dates_for_dataset('lsasaf-et', 'et', 'undefined', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    native_mapset='MSG-satellite-3km'
    target_mapset='SPOTV-Africa-1km'

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'lsasaf-et',\
            'starting_sprod':'et',\
            'starting_dates': starting_dates,\
            'native_mapset': native_mapset,\
            'mapset': target_mapset,\
            'version':'undefined',
            'logfile':'log-lsasaf-et.log'}

    res_queue = None
    proc_lists=processing_std_lsasaf_et(res_queue,**args)
    print (proc_lists)
#   ---------------------------------------------------------------------
# lsasaf-lst
#   ---------------------------------------------------------------------
from apps.processing.processing_std_lsasaf_lst import *
def my_proc_std_lsasaf_lst(pipe_run=4, pipe_print=0, start_date=None, end_date=None, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    # start_date='201510010000'
    # end_date='201510102345'
    # starting_dates = proc_functions.get_list_dates_for_dataset('lsasaf-lst', 'lst', 'undefined', start_date=start_date, end_date=end_date)
    starting_dates = None
    native_mapset='MSG-satellite-3km'
    target_mapset='SPOTV-CEMAC-1km'

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'lsasaf-lst',\
            'starting_sprod':'lst',\
            'starting_dates': starting_dates,\
            'native_mapset': native_mapset,\
            'mapset': target_mapset,\
            'version':'undefined',
            'logfile':'log-lsasaf-lst.log'}

    res_queue = None
    proc_lists=processing_std_lsasaf_lst(res_queue,**args)
    print (proc_lists)

#   ---------------------------------------------------------------------
# modis-firms
#   ---------------------------------------------------------------------
from apps.processing.processing_std_modis_firms import *
def my_proc_std_modis_firms(start_date=None, end_date=None, pipe_run=0, pipe_print=3, start_date_stats=None, end_date_stats=None, touch_files_only=False):

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
            'update_stats' : True,
            'nrt_products' : True,
            'touch_files_only':touch_files_only}

    res_queue = None
    proc_lists=processing_std_modis_firms(res_queue,**args)
    print (proc_lists)

# ---------------------------------------------------------------------
# fewsnet: rain onset
#   ---------------------------------------------------------------------
from apps.processing.processing_std_rain_onset import *
def my_proc_std_rain_onset(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):

    #   ---------------------------------------------------------------------
    # onset computation
    #   ---------------------------------------------------------------------

    start_date='20160901'
    end_date = '20161011'
    starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0',
                                                               start_date=start_date, end_date=end_date)

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'fewsnet-rfe',\
            'starting_sprod':'10d',\
            'mapset': 'FEWSNET-Africa-8km',\
            'version':'2.0',
            'logfile':'rain-onset',
            'starting_dates':starting_dates
            }
    res_queue = None
    processing_std_rain_onset(res_queue, **args)

#   ---------------------------------------------------------------------
# arc2-rain cumulate
#   ---------------------------------------------------------------------
from apps.processing.processing_std_precip_1day import *
# Create the list of dates -> returns empty if start==end==None
def  my_proc_std_precip_1day(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):
    start_date='20160101'
    end_date = '20170601'
    starting_dates = proc_functions.get_list_dates_for_dataset('arc2-rain','1day', '2.0', start_date=start_date, end_date=end_date)
    # starting_dates = None
    mapset='ARC2-Africa-11km'
    # #
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'arc2-rain',\
            'starting_sprod':'1day',\
            'starting_dates': starting_dates,\
            'mapset': mapset,\
            'version':'2.0',
            'logfile':'log-arc2-rain.log'}

    res_queue = None
    proc_lists=processing_std_precip_1day(res_queue,**args)
    print (proc_lists)

#   ---------------------------------------------------------------------
# arc2-rain SPI
#   ---------------------------------------------------------------------
from apps.processing.processing_std_precip_spi import *
def my_proc_std_spi_monthly(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):
    start_date='19830301'
    end_date = '19830310'
    starting_dates = proc_functions.get_list_dates_for_dataset('arc2-rain','1day', '2.0', start_date=start_date, end_date=end_date)
    starting_dates = None
    mapset='ARC2-Africa-11km'
    # #
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'arc2-rain',\
            'starting_sprod':'1mon',\
            'starting_dates': starting_dates,\
            'mapset': mapset,\
            'version':'2.0',
            'logfile':'log-arc2-rain.log'}

    res_queue = None
    proc_lists=processing_std_spi_monthly(res_queue,**args)
    print (proc_lists)

#   ---------------------------------------------------------------------
# seas cumulation computation
#   ---------------------------------------------------------------------
from apps.processing.processing_std_seas_cum import *
def my_proc_std_seas_cum(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):
    # start_date='20150901'
    # end_date = '20160621'
    # starting_dates = proc_functions.get_list_dates_for_dataset('fewsnet-rfe', '10d', '2.0',
    #                                                            start_date=start_date, end_date=end_date)
    starting_dates=None
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'fewsnet-rfe',\
            'starting_sprod':'10d',\
            'mapset': 'FEWSNET-Africa-8km',\
            'version':'2.0',
            'logfile':'cum.log',
            'mapset': 'SPOTV-SADC-1km',\
            'starting_dates':starting_dates
            }
    res_queue = None
    processing_std_seas_cum(res_queue, **args)

#   ---------------------------------------------------------------------
#   GSOD
#   ---------------------------------------------------------------------
from apps.processing.processing_std_gsod import *
def my_proc_std_gsod(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):
    start_date='20160503'
    end_date = '20160505'
    starting_dates = proc_functions.get_list_dates_for_dataset('gsod-rain', '1dmeas', '1.0',
                                                                start_date=start_date, end_date=end_date)
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'gsod-rain',\
            'starting_sprod':'1dmeas',\
            'mapset': 'SPOTV-SADC-1km',\
            'version':'1.0',
            'logfile':'gsod.log',
            'starting_dates':starting_dates
            }
    res_queue = None
    processing_std_gsod(res_queue, **args)

#   ---------------------------------------------------------------------
#   MSG-MPE
#   ---------------------------------------------------------------------
from apps.processing.processing_std_msg_mpe import *
def my_proc_msg_mpe(start_date=None, end_date=None, pipe_run=0, pipe_print=3, start_date_stats=None, end_date_stats=None, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('msg-mpe', '10dcum', 'undefined', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'msg-mpe',\
            'starting_sprod':'10dcum',\
            'starting_dates': starting_dates,\
            'mapset': 'SPOTV-Africa-1km',\
            'version':'undefined',
            'logfile':'ruffus-chirps',
            'touch_only':touch_files_only}

    res_queue = None
    proc_lists=processing_std_msg_mpe(res_queue,**args)
    print (proc_lists)
#
#   Test Ruffus for completeness bars
#
# from apps.processing.processing_completeness import *
# def test_proc_completeness():
#
#     args = {'prod': 'modis-firms',\
#             'subprod':'1day',\
#             'starting_dates': None,\
#             'mapset': 'SPOTV-Africa-1km',\
#             'version':'v6.0',
#             'product_type':"Ingest",
#             'touch_only':False,
#             'logfile':"apps.processing.test_completeness"}
#
#     status=processing_completeness(**args)

from apps.processing.processing_std_olci_wrr import *
def my_proc_olci_wrr(start_date=None, end_date=None, pipe_run=0, pipe_print=3, start_date_stats=None, end_date_stats=None, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    if start_date is not None and end_date is not None:
        #starting_dates = proc_functions.get_list_dates_for_dataset('olci-wrr', 'chl-nn', 'V02.0', start_date=start_date, end_date=end_date)
        starting_dates = proc_functions.get_list_dates_for_dataset('olci-wrr', 'chl-oc4me', 'V02.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'olci-wrr',\
            'starting_sprod':'chl-oc4me',\
            'starting_dates': starting_dates,\
            'mapset': 'SPOTV-Africa-1km',\
            'version':'V02.0',
            'logfile':'ruffus-chirps'}

    res_queue = None
    proc_lists=processing_std_olci_wrr(res_queue,**args)
    print (proc_lists)

#   ---------------------------------------------------------------------
# vgt-dmp
#   ---------------------------------------------------------------------
from apps.processing.processing_std_dmp import *
def my_proc_vgt_dmp(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False):

    # Create the list of dates -> returns empty if start==end==None
    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('vgt-dmp', 'dmp', 'V2.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'vgt-dmp',\
            'starting_sprod':'dmp',\
            'starting_dates': starting_dates,\
            'mapset': 'SPOTV-Africa-1km',\
            'version':'V2.0',
            'logfile':'ruffus-chirps',
            'touch_only':touch_files_only}

    request_queue = Queue()
    proc_lists=processing_std_dmp_all(request_queue, **args)

from apps.processing.processing_std_opfish import *
def test_proc_modis_chla_opfish(pipe_run=0, pipe_print=3, touch_files_only=False):

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'modis-chla',\
            'starting_sprod':'chla-day',\
            'mapset': 'MODIS-Africa-4km',\
            'version':'v2013.1',
            'logfile':'modis-chla',
            'touch_files_only':touch_files_only
            }
    res_queue = None

    processing_std_opfish(res_queue, **args)

#   ---------------------------------------------------------------------
# modis-ba (not yet there ?!?)
#   ---------------------------------------------------------------------
# from apps.processing.processing_std_ba import *
# def my_proc_std_ba(start_date=None, end_date=None, pipe_run=0, pipe_print=3, start_date_stats=None, end_date_stats=None, touch_files_only=False):
#
#     # Create the list of dates -> returns empty if start==end==None
#     if start_date is not None and end_date is not None:
#         starting_dates = proc_functions.get_list_dates_for_dataset('vgt-ba', 'ba', 'V1.5', start_date=start_date, end_date=end_date)
#     else:
#         starting_dates = None
#
#     if start_date_stats is not None and end_date_stats is not None:
#         starting_dates_stats = proc_functions.get_list_dates_for_dataset('vgt-ba', 'ba', 'V1.5', start_date=start_date_stats, end_date=end_date_stats)
#     else:
#         starting_dates_stats = None
#
#     target_mapset='SPOTV-Africa-1km'
#
#     touch_files_only=False
#
#     args = {'pipeline_run_level':pipe_run,
#             'pipeline_printout_level':pipe_print,
#             'pipeline_printout_graph_level': 0,
#             'prod': 'vgt-ba',
#             'starting_sprod':'ba',
#             'starting_dates': starting_dates,
#             'starting_dates_stats': starting_dates_stats,
#             'mapset': target_mapset,
#             'version':'V1.5',
#             'logfile':'log-modis-firms.log',
#             'touch_files_only':touch_files_only}
#
#     res_queue = None
#     proc_lists=processing_std_ba_stats_only(res_queue,**args)
#     print (proc_lists)

#   ---------------------------------------------------------------------
#    OLCI-WRR: chla gradient
#   ---------------------------------------------------------------------
from apps.processing.processing_std_gradient import *
def my_proc_olci_wrr_chla_gradient(pipe_run=0, pipe_print=3, touch_files_only=False):

    # args = {'pipeline_run_level':pipe_run, \
    #         'pipeline_printout_level':pipe_print, \
    #         'pipeline_printout_graph_level': 0, \
    #         'prod': 'olci-wrr',\
    #         'starting_sprod':'chl-oc4me',\
    #         'mapset': 'SPOTV-Africa-1km',\
    #         'version':'V02.0',
    #         'logfile':'olci-wrr',
    #         'touch_files_only':touch_files_only
    #         }
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'modis-chla',\
            'starting_sprod':'chla-day',\
            'mapset': 'MODIS-Africa-4km',\
            'version':'v2013.1',
            'logfile':'modis-chla',
            'touch_files_only':touch_files_only
            }
    res_queue = None

    processing_std_gradient(res_queue, **args)

from apps.processing.processing_std_vgt import *
def test_subprocess_vgt_fapar(pipe_run=4, pipe_print=0, touch_files_only=False):
    start_date = None
    end_date = None

    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('vgt-fapar', 'fapar', 'V2.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'vgt-fapar',\
            'starting_sprod':'fapar',\
            'mapset': 'SPOTV-Africa-1km',\
            'version':'V2.0',
            'starting_dates': starting_dates,
            'logfile':'vgt-fapar',
            'upsert_db' : False,
            'touch_only':touch_files_only
            }
    res_queue = None

    processing_std_vgt_prods_only(res_queue, **args)

def test_subprocess_vgt_fcover(pipe_run=4, pipe_print=0, touch_files_only=False):
    start_date = '19990101'
    end_date = '20181221'

    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('vgt-fcover', 'fcover', 'V2.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None
    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'vgt-fcover',\
            'starting_sprod':'fcover',\
            'mapset': 'SPOTV-Africa-1km',\
            'version':'V2.0',
            'starting_dates': starting_dates,
            'logfile':'vgt-fcover',
            'upsert_db' : False,
            'touch_only':touch_files_only
            }
    res_queue = None

    processing_std_vgt_stats_only(res_queue, **args)

def test_subprocess_vgt_lai(pipe_run=4, pipe_print=0, touch_files_only=False):
    #     # Create the list of dates -> returns empty if start==end==None
    start_date = '19990101'
    end_date = '20181221'

    if start_date is not None and end_date is not None:
        starting_dates = proc_functions.get_list_dates_for_dataset('vgt-lai', 'lai', 'V2.0', start_date=start_date, end_date=end_date)
    else:
        starting_dates = None

    args = {'pipeline_run_level':pipe_run, \
            'pipeline_printout_level':pipe_print, \
            'pipeline_printout_graph_level': 0, \
            'prod': 'vgt-lai',\
            'starting_sprod':'lai',\
            'mapset': 'SPOTV-Africa-1km',\
            'version':'V2.0',
            'logfile':'vgt-lai',
            'starting_dates':starting_dates,
            'upsert_db' : False,
            'touch_only':touch_files_only
            }
    res_queue = None

    processing_std_vgt_stats_only(res_queue, **args)

# from apps.processing.processing_std_swi import *
# def test_subprocess_swi(pipe_run=4, pipe_print=0, touch_files_only=False):
#     start_date = '19990101'
#     end_date = '20181221'
#
#     if start_date is not None and end_date is not None:
#         starting_dates = proc_functions.get_list_dates_for_dataset('vgt-ba', 'ba', 'V1.5', start_date=start_date, end_date=end_date)
#     else:
#         starting_dates = None
#     args = {'pipeline_run_level':pipe_run, \
#             'pipeline_printout_level':pipe_print, \
#             'pipeline_printout_graph_level': 0, \
#             'prod': 'ascat-swi',\
#             'starting_sprod':'swi',\
#             'mapset': 'ASCAT-Africa-12-5km',\
#             'version':'V3.1',
#             'starting_dates': starting_dates,
#             'logfile':'ascat-swi',
#             'upsert_db' : True,
#             'touch_only':touch_files_only
#             }
#     res_queue = None
#
#     processing_std_swi_stats_only(res_queue, **args)




#   ---------------------------------------------------------------------
#   Call a specific processing chain - To be TESTED after 03.3.2019
#   ---------------------------------------------------------------------

# test_subprocess_swi(pipe_run=3, pipe_print=0, touch_files_only=False)
# test_subprocess_vgt_lai(pipe_run=0, pipe_print=4, touch_files_only=False)
# test_subprocess_vgt_fcover(pipe_run=3, pipe_print=0, touch_files_only=False)
# test_subprocess_vgt_fapar(pipe_run=0, pipe_print=4, touch_files_only=False)
# my_proc_std_ndvi(pipe_run=3, pipe_print=0, touch_files_only=False)
#my_proc_ndvi_merge(pipe_run=0, pipe_print=3, touch_files_only=False)
# my_proc_pml_modis_fronts(pipe_run=3, pipe_print=0, touch_files_only=False)
#my_proc_std_fronts(pipe_run=0, pipe_print=3, touch_files_only=False)
#my_proc_std_modis_chla(pipe_run=0, pipe_print=3, touch_files_only=False)
#my_proc_std_modis_sst(pipe_run=0, pipe_print=3, touch_files_only=False)
#my_proc_std_modis_par(pipe_run=0, pipe_print=3, touch_files_only=False)
#my_proc_std_modis_kd490(pipe_run=0, pipe_print=3, touch_files_only=False)
#my_proc_modis_pp(pipe_run=0, pipe_print=4, touch_files_only=False)
#my_proc_std_median_filter()
#my_proc_tamsat_rfe(pipe_run=4, pipe_print=0, start_date='19830101', end_date='20171231', touch_files_only=False)
# proc_list=my_proc_fewsnet_rfe(pipe_run=0, pipe_print=8, start_date=None, end_date=None, touch_files_only=False)                       # OK

# my_proc_chirps_dekad(pipe_run=3, pipe_print=0, start_date='20180101', end_date='20181231', upsert_db=False, touch_files_only=False)
# my_proc_fewsnet_rfe(pipe_run=3, pipe_print=0, start_date='20010101', end_date='20181231',touch_files_only=False)
# my_proc_arc2rain_dekad(pipe_run=0, pipe_print=6, start_date='19810101', end_date='20171231', upsert_db=False, touch_files_only=False)
# my_proc_chirps_lp(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False, type='')
# start_y='2019'; start_m='11'; start_d='01';       start_date=start_y+start_m+start_d+'0000'
# end_y  ='2019'; end_m  ='12'; end_d  ='31';       end_date=end_y+end_m+end_d+'2345'
# # start_date=None; end_date=None
# my_proc_std_lsasaf_et(pipe_run=6, pipe_print=0, start_date=start_date, end_date=end_date, touch_files_only=False)
#my_proc_std_lsasaf_lst(pipe_run=4, pipe_print=0, start_date=None, end_date=None, touch_files_only=False)
#my_proc_std_modis_firms(pipe_run=4, pipe_print=0, start_date='20020701', end_date='20180630',touch_files_only=False)
#my_proc_std_rain_onset(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False)
#my_proc_std_precip_1day(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False)
#my_proc_std_spi_monthly(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False)
#my_proc_std_seas_cum(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False)
#my_proc_std_gsod(pipe_run=0, pipe_print=3, start_date=None, end_date=None, touch_files_only=False)
#my_proc_msg_mpe(start_date=None, end_date=None, pipe_run=0, pipe_print=3, start_date_stats=None, end_date_stats=None, touch_files_only=False)
#my_proc_olci_wrr(start_date=None, end_date=None, pipe_run=0, pipe_print=3, start_date_stats=None, end_date_stats=None, touch_files_only=False)
#my_proc_vgt_dmp(pipe_run=4, pipe_print=0, start_date='19990101', end_date='20171231', touch_files_only=False)
#my_proc_std_ba(start_date=None, end_date=None, pipe_run=0, pipe_print=3, start_date_stats=None, end_date_stats=None, touch_files_only=False)
#my_proc_olci_wrr_chla_gradient(pipe_run=0, pipe_print=3, touch_files_only=False)
test_proc_modis_chla_opfish(pipe_run=3, pipe_print=0, touch_files_only=False)
#   ---------------------------------------------------------------------
#   OFF-LINE Tests (on raster-math functions)
#   ---------------------------------------------------------------------
# import numpy
# args = {"input_file": '/data/processing/exchange/Sentinel-3/gradient/20180202_olci-wrr_median-filter_SPOTV-Africa-1km_V02.0.tif', "output_file": '/data/processing/exchange/Sentinel-3/gradient/20180202_olci-wrr_extrapolated5_SPOTV-Africa-1km_V02.0.tif', "nodata": 1000,"output_format": 'GTIFF',
#         "options": "compress = lzw"}
# args = {"input_file": '/data/processing/exchange/Sentinel-3/gradient/CHL_orig_10-12-2018.tif', "output_file": '/data/processing/exchange/Sentinel-3/gradient/CHL_ord_1IT_10_sd_2_10-12-2018.tif', "nodata": numpy.nan,"output_format": 'GTIFF',
#         "options": "compress = lzw"}
# args = {"input_file": '/data/processing/exchange/Sentinel-3/gradient/20180202_olci-wrr_extrapolated5_SPOTV-Africa-1km_V02.0.tif', "output_file": '/data/processing/exchange/Sentinel-3/gradient/20180202_olci-wrr_gradient5_SPOTV-Africa-1km_V02.0.tif', "nodata": 1000,"output_format": 'GTIFF',
#         "options": "compress = lzw"}
#raster_image_math.extrapolate_edge(**args)
#raster_image_math.compute_median_filter(**args)
