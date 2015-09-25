#
#	purpose: Define the processing service (by using ruffus)
#	author:  Olivier Thamba and Maixent Kambi 
#	date:	 20150318
#   	descr:	 Generate additional derived products / implements processing chains
#	history: 1.0
#

# Source my definitions
from config import es_constants
import os
import glob 
import re
# Import eStation2 modules
#from database import querydb
from lib.python import functions
from lib.python import metadata
from lib.python.image_proc import raster_image_math
from lib.python.image_proc import recode
from database import crud

from lib.python import es_logging as log

# Import third-party modules
from ruffus import *
import pickle
import datetime
import itertools

logger = log.my_logger(__name__)

#   General definitions for this processing chain
prod="lsasaf-etp"
mapset='MSG-satellite-3km'
ext='.tif'
version='4.0'

#   switch wrt temporal resolution
activate_10d30min_comput=0
activate_10daycum_comput=0
activate_1moncum_comput=1

def create_pipeline(starting_sprod):

    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    input_dir = es_constants.processing_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    starting_files = input_dir+"*"+in_prod_ident

    #   Dekad average for every 30min (mm/h)

    output_sprod="10d30min"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_10d30min():

        ##   Look for all input files in input_dir, and sort them
        input_files = glob.glob(starting_files)
        dekad_list = []
        # Create unique list of all months
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd)
            if mydekad_nbr not in dekad_list:
              dekad_list.append(mydekad_nbr)

        # Generate the list of 30 min time
        timelist = [datetime.time(h,m).strftime("%H%M") for h,m in itertools.product(xrange(0,24),xrange(0,60,30))]

        for time in timelist:
            files_for_time = glob.glob(input_dir+os.path.sep+'*'+time+in_prod_ident)
            for dekad in dekad_list:
                file_list = []
                my_dekad_str = functions.conv_dekad_2_date(dekad)
                output_file=es_constants.processing_dir+output_subdir+os.path.sep+my_dekad_str+'_'+time+out_prod_ident

                for myfile in files_for_time:
                    basename=os.path.basename(myfile)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd[0:8])
                    if mydekad_nbr == dekad:
                        file_list.append(myfile)

                yield (file_list, output_file)


    @active_if(activate_10d30min_comput)
    @files(generate_parameters_10d30min)
    def lsasaf_etp_10d30min(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', \
                "options": "compress=lzw", "input_nodata":-1}

        raster_image_math.do_avg_image(**args)



    # ----------------------------------------------------------------------------------------------------------------
    # #   10 day Cumulate (mm)
    output_sprod_10daycum="10daycum"
    out_prod_ident_10daycum = functions.set_path_filename_no_date(prod, output_sprod_10daycum, mapset, version, ext)
    output_subdir_10daycum  = functions.set_path_sub_directory   (prod, output_sprod_10daycum, 'Derived', version, mapset)

    #   Define input files
    in_prod_10daycum = '10d30min'
    in_prod_ident_10daycum = functions.set_path_filename_no_date(prod, in_prod_10daycum, mapset, version, ext)

    input_dir_10daycum = es_constants.processing_dir+ \
                functions.set_path_sub_directory(prod, in_prod_10daycum, 'Derived', version, mapset)

    starting_files_10daycum = input_dir_10daycum+"*"+in_prod_ident_10daycum

    formatter_in="(?P<YYYYMMDD>[0-9]{8})_[0-9]{4}"+in_prod_ident_10daycum
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir_10daycum+"{YYYYMMDD[0]}"+out_prod_ident_10daycum]

    @active_if(activate_10daycum_comput)
    @collate(starting_files_10daycum, formatter(formatter_in),formatter_out)
    def lsasaf_etp_10daycum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        # Get the number of days of that dekad
        basename=os.path.basename(output_file)
        mydate=functions.get_date_from_path_filename(basename)
        nbr_days_dekad = functions.day_per_dekad(mydate)
        # Compute the correcting factor: we sum-up all 48 30min cycles and:
        # Divide by 2 (mm/h -> mm)
        # Multiply by number of days
        # Divide by 100, so that the scale factor changes from 0.0001 (30min) to 0.01
        factor = float(nbr_days_dekad)*0.005
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "scale_factor": factor, "input_nodata":-1}
        raster_image_math.do_cumulate(**args)

    # 1moncum
    output_sprod='1moncum'
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    #file d'entre
    in_prod_1moncum='10daycum'
    in_prod_ident_1moncum = functions.set_path_filename_no_date(prod, in_prod_1moncum, mapset, version, ext)
    input_dir_1moncum = es_constants.processing_dir+ \
                     functions.set_path_sub_directory(prod, in_prod_1moncum, 'Derived', version, mapset)

    starting_files_1moncum = input_dir_1moncum+"*"+in_prod_ident_1moncum
    print("starting_files %s" % starting_files_1moncum)

    formatter_in="(?P<YYYYMM>[0-9]{6})[0-9]{2}"+in_prod_ident_1moncum
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+'01'+out_prod_ident
#
    @active_if(activate_1moncum_comput)
    @collate(starting_files_1moncum, formatter(formatter_in),formatter_out)
    def lsasaf_etp_1moncum(input_file, output_file):
#
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        print(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "input_nodata":-1}
        raster_image_math.do_cumulate(**args)
#

def processing_lsasaf_etp(pipeline_run_level=0,pipeline_printout_level=0,
                           pipeline_printout_graph_level=0):

    create_pipeline(starting_sprod='30min')

    list = pipeline_get_task_names()
    print list
    logger.info("Entering routine %s" % 'processing_lsasaf_etp')
    if pipeline_run_level > 0:
        logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level)
    
    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
