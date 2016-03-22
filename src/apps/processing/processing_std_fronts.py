#
#	purpose: Define the processing chain for 'sst-fronts' processing chains
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 05.01.2015
#   descr:	 Generate additional Derived products /implements processing chains
#	history: 1.0
#

# Import std modules
import os

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants

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

    activate_front_detection = 1
    activate_shapefile_conversion = 1

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files (SST)
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    input_dir = es2_data_dir+ functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    if my_date:
        starting_files = input_dir+my_date+"*"+in_prod_ident
    else:
        starting_files = input_dir+"*"+in_prod_ident

    #   ---------------------------------------------------------------------
    #   1. Define and customize parameters
    #   ---------------------------------------------------------------------

    # Default values are from the routine are used if None is passed
    parameters = None

    if prod == 'modis-sst':
        parameters = {  'histogramWindowStride': None,
                        'minTheta' : None,
                        'minPopProp' : None,
                        'minPopMeanDifference' : None,
                        'minSinglePopCohesion' : None,
                        'histogramWindowSize' : None,
                        'minImageValue' : None,
                        'minThreshold' : None }

    if prod == 'pml-modis-sst':
        parameters = {  'histogramWindowStride': None,
                        'minTheta' : None,
                        'minPopProp' : None,
                        'minPopMeanDifference' : None,
                        'minSinglePopCohesion' : None,
                        'histogramWindowSize' : None,
                        'minImageValue' : None,
                        'minThreshold' : None }

    #   ---------------------------------------------------------------------
    #   SST Fronts (raster)
    output_sprod_group=proc_lists.proc_add_subprod_group("fronts")
    output_sprod=proc_lists.proc_add_subprod("sst-fronts", "fronts", final=False,
                                             descriptive_name='SST Fronts',
                                             description='Sea Surface Temperature Fronts',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_fronts = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_fronts = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYYMMDD>[0-9]{8})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_fronts+"{YYYYMMDD[0]}"+prod_ident_fronts]

    @active_if(activate_front_detection)
    @transform(starting_files, formatter(formatter_in),formatter_out)
    def sst_fronts_detection(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw",
                "parameters": parameters}

        raster_image_math.do_detect_sst_fronts(**args)
        print 'Done with raster'

    #   ---------------------------------------------------------------------
    #   SST Fronts (shapefile)

    input_subprod_fronts = "sst-fronts"
    in_prod_ident_fronts = functions.set_path_filename_no_date(prod, input_subprod_fronts,mapset, version, ext)

    input_dir_fronts = es2_data_dir+ functions.set_path_sub_directory(prod, input_subprod_fronts, 'Derived', version, mapset)

    starting_files_fronts = input_dir_fronts+"*"+in_prod_ident_fronts
    output_sprod=proc_lists.proc_add_subprod("sst-fronts-shp", "fronts", final=False,
                                             descriptive_name='SST Fronts',
                                             description='Sea Surface Temperature Fronts (shape)',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_fronts_shp = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, '.shp')
    subdir_fronts_shp = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYYMMDD>[0-9]{8})"+in_prod_ident_fronts
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_fronts_shp+"{YYYYMMDD[0]}"+prod_ident_fronts_shp]

    @active_if(activate_shapefile_conversion)
    @transform(starting_files_fronts, formatter(formatter_in),formatter_out)
    def sst_shapefile_conversion(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        #command=[es_constants.es2globals['gdal_polygonize'], input_file, output_file, '-nomask', '-f', 'ESRI Shapefile']
        #p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #out, err = p.communicate()
        command=es_constants.es2globals['gdal_polygonize']+' '+ input_file+' '+ output_file+' -nomask -f "ESRI Shapefile"'
        print command
        p = os.system(command)

    return proc_lists

#   ---------------------------------------------------------------------
#   Run the pipeline
def processing_std_fronts(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                        pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                        starting_dates=None, update_stats=False, nrt_products=True, write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_fronts')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, history_file='/eStation2/log/.ruffus_history.sqlite')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    #res_queue.put(proc_lists)
    return True

