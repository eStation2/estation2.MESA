#
#	purpose: Define the processing chain for 'sst-fronts' processing chains
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 05.01.2015
#   descr:	 Generate additional Derived products /implements processing chains
#	history: 1.0
#

# Import std modules
import os
import glob
import tempfile
import shutil

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from apps.processing import proc_functions

# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

#
#   Rational for 'active' flags:
#   A flag is defined for each product, with name 'activate_'+ prodname, ans initialized to 1: it is
#   deactivated only for optimization  - for 'secondary' products
#   In working conditions, products are activated by groups (for simplicity-clarity)
#
#   A list of 'final' (i.e. User selected) output products are defined (now hard-coded)
#   According to the dependencies, if set, they force the various groups

def create_pipeline(proc_lists=None, input_product=None, output_product=None):


    my_date=None
    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    if input_product is None and output_product is None:
        return None

    prod = input_product.productcode
    starting_sprod = input_product.subproductcode
    version = input_product.version
    mapset = input_product.mapsetcode

    # Define dates interval from input product
    start_date = input_product.start_date
    end_date = input_product.end_date

    # Manage the dates
    list_dates = proc_functions.get_list_dates_for_dataset(prod, starting_sprod, version,
                                                           start_date=start_date, end_date=end_date)

    activate_reprojection = 1

    # sds_meta = metadata.SdsMetadata()
    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    input_dir = es2_data_dir+ functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    if my_date:
        starting_files = input_dir+my_date+"*"+in_prod_ident
    else:
        starting_files = input_dir+"*"+in_prod_ident

    #   ---------------------------------------------------------------------
    #   NDVI 1km (raster)
    output_sprod_group=proc_lists.proc_add_subprod_group(output_product.subproductcode)
    output_sprod=proc_lists.proc_add_subprod(output_product.subproductcode, output_product.subproductcode, final=False,
                                             descriptive_name=output_product.subproductcode,
                                             description=output_product.subproductcode,
                                             frequency_id='',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    # output_sprod=proc_lists.proc_add_subprod("ndvi", "ndvi", final=False,
    #                                          descriptive_name='NDVI',
    #                                          description='NDVI 1km',
    #                                          frequency_id='',
    #                                          date_format='YYYYMMDD',
    #                                          masked=False,
    #                                          timeseries_role='',
    #                                          active_default=True)

    target_mapset_name = output_product.mapsetcode #mapset.split('-')[0]+'-'+mapset.split('-')[1]+'-1km' 'SPOTV-Africa-1km'
    prod_ident_reprojected = functions.set_path_filename_no_date(prod, output_sprod,target_mapset_name, version, ext)
    subdir_reprojected = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, target_mapset_name)

    formatter_in = "(?P<YYYYMMDD>[0-9]{8})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_reprojected+"{YYYYMMDD[0]}"+prod_ident_reprojected]

    @active_if(activate_reprojection)
    @transform(starting_files, formatter(formatter_in),formatter_out)
    def reprojected_computation(input_file, output_file):

        # no_data = int(sds_meta.get_nodata_value(input_file))
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        # args = {"inputfile": input_file, "output_file": output_file, "native_mapset_name": mapset,
        #         "target_mapset_name": target_mapset_name, "interpolation_method" : es_constants.ES2_AVERAGE_INTERP_METHOD}
        args = {"inputfile": input_file, "output_file": output_file, "native_mapset_name": mapset,
                "target_mapset_name": target_mapset_name}
        raster_image_math.do_reproject(**args)
        print 'Done reprojection'


    return proc_lists

#   ---------------------------------------------------------------------
#   Run the pipeline
def processing_reproject(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                             pipeline_printout_graph_level=0, input_products='', output_product='', write2file=None, logfile=None, nrt_products=True,
                        update_stats=True):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_reproject')


    proc_lists = None
    proc_lists = create_pipeline(proc_lists, input_product=input_products[0], output_product=output_product[0])

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_std_chla_gradient.sqlite'),
                     checksum_level=0)

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    #res_queue.put(proc_lists)
    return None

