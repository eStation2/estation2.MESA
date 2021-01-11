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
from lib.python import metadata

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

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None):


    my_date=None
    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    activate_reprojection = 1
    #activate_shapefile_conversion = 1

    sds_meta = metadata.SdsMetadata()
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
    output_sprod_group=proc_lists.proc_add_subprod_group("ndvi")
    output_sprod=proc_lists.proc_add_subprod("ndvi", "ndvi", final=False,
                                             descriptive_name='NDVI',
                                             description='NDVI 1km',
                                             frequency_id='',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    target_mapset_name = 'SPOTV-Africa-1km'
    prod_ident_reprojected = functions.set_path_filename_no_date(prod, output_sprod,target_mapset_name, version, ext)
    subdir_reprojected = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, target_mapset_name)

    formatter_in = "(?P<YYYYMMDD>[0-9]{8})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_reprojected+"{YYYYMMDD[0]}"+prod_ident_reprojected]

    @active_if(activate_reprojection)
    @transform(starting_files, formatter(formatter_in),formatter_out)
    def reprojected_computation(input_file, output_file):

        no_data = int(sds_meta.get_nodata_value(input_file))
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
def processing_std_reproject(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                             pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                             starting_dates=None, write2file=None, logfile=None,
                             touch_files_only=False):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_reproject9')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_std_chla_gradient.sqlite'),touch_files_only=touch_files_only,
                     checksum_level=0)

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    #res_queue.put(proc_lists)
    return None

