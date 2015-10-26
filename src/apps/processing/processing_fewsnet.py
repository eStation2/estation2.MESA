#
#	purpose: Define the processing service (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products / implements processing chains
#	history: 1.0
#
#   Still to be done
#   TODO-M.C.: more checks on the IN/OUT
#   TODO-M.C.test: Activate/deactivate according to DB settings
#   TODO-M.C.test: Add a mechanism to extract/visualize the 'status' -> pipeline_printout(verbose=3)+grep-like function ?
#   TODO-M.C.: create unittest-like functions for validating the chain
#   TODO-M.C.test: add the Np anomalies
#   TODO-M.C.test: find a robust method to solve the tuple/string issue in filename (fttb: return_as_element_of_list() ?)
#   TODO-M.C.: add management of 'version' !!
#

# Source my definitions
from config import es_constants
import os

# Import eStation2 modules
#from database import querydb
from lib.python import functions
from lib.python import metadata
from lib.python.image_proc import raster_image_math
from lib.python.image_proc import recode
from database import crud
from lib.python import es_logging as log

# This is temporary .. to be replace with a DB call
from apps.processing.processing_switches import *

# Import third-party modules
from ruffus import *

logger = log.my_logger(__name__)

#   General definitions for this processing chain
prod="fewsnet_rfe"
mapset='FEWSNET_Africa_8km'
ext='.tif'
version='undefined'

#   switch wrt temporal resolution
activate_10d_comput=1
activate_1month_comput=1

#   specific switch for each subproduct
# 1. 10d prod stats
activate_10davg_comput=1
activate_10dmin_comput=1
activate_10dmax_comput=1
# 2.a 10d prod anom
activate_10ddiff_comput=1
activate_10davgperc_comput=1
activate_10dperc_comput=1
activate_10dnp_comput=1

# 2.a 10d prod anom
activate_1moncum_comput=1
activate_1monavg_comput=1
activate_1monmin_comput=1
activate_1monmax_comput=1
activate_1mondiff_comput=1
activate_1monperc_comput=1
activate_1monnp_comput=1

def create_pipeline(starting_sprod):
    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, ext)

    input_dir = es_constants.processing_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    starting_files = input_dir+"*"+in_prod_ident

    #   ---------------------------------------------------------------------
    #   Average
    output_sprod="10davg"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][4]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_fewsnet_rfe_comput, activate_10d_comput, activate_10davg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def fewsnet_10davg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)


    #   ---------------------------------------------------------------------
    #   Minimum
    output_sprod="10dmin"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][4]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_fewsnet_rfe_comput, activate_10d_comput, activate_10dmin_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def fewsnet_10dmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Maximum
    output_sprod="10dmax"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][4]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_fewsnet_rfe_comput, activate_10d_comput, activate_10dmax_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def fewsnet_10dmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   10dDiff
    output_sprod="10ddiff"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][4]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "10davg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][4]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(fewsnet_10davg)
    @active_if(activate_fewsnet_rfe_comput, activate_10d_comput, activate_10ddiff_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def fewsnet_10ddiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)
   #   ---------------------------------------------------------------------
    #   10dAvgPerc
    output_sprod="10davgperc"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][4]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "10davg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][4]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(fewsnet_10ddiff)
    @active_if(activate_fewsnet_rfe_comput, activate_10d_comput, activate_10davgperc_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def fewsnet_10davgperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_division_perc(**args)
        
    #   ---------------------------------------------------------------------
    #   10dperc
    output_sprod="10dperc"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][4]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "10davg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input="{subpath[0][4]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(fewsnet_10davg)
    @active_if(activate_fewsnet_rfe_comput, activate_10d_comput, activate_10dperc_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def fewsnet_10dperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

    #   ---------------------------------------------------------------------
    #   10dnp
    output_sprod="10dnp"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + min + max
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][4]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod_1 = "10dmin"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, ext)
    ancillary_subdir_1      = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived',version, mapset)
    ancillary_input_1="{subpath[0][4]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "10dmax"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, ext)
    ancillary_subdir_2      = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived',version, mapset)
    ancillary_input_2="{subpath[0][4]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    @follows(fewsnet_10dmin, fewsnet_10dmax)
    @active_if(activate_fewsnet_rfe_comput, activate_10d_comput, activate_10dnp_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2), formatter_out)
    def fewsnet_10dnp(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "min_file": input_file[1],"max_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_make_vci(**args)

    #   ---------------------------------------------------------------------
    #   1moncum
    output_sprod="1moncum"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    # inputs: files from same months
    formatter_in="(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})"+in_prod_ident
    formatter_out="{subpath[0][4]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+'01'+out_prod_ident

    # @follows(fewsnet_10davg)
    @active_if(activate_fewsnet_rfe_comput, activate_1month_comput, activate_1moncum_comput)
    @collate(starting_files, formatter(formatter_in), formatter_out)
    def fewsnet_1moncum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file,"output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Average
    new_input_subprod='1moncum'
    in_prod_ident= functions.set_path_filename_no_date(prod, new_input_subprod, mapset, ext)

    output_sprod='1monavg'
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][4]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_fewsnet_rfe_comput, activate_1month_comput, activate_1monavg_comput)
    @collate(fewsnet_1moncum, formatter(formatter_in),formatter_out)
    def fewsnet_1monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Minimum
    output_sprod="1monmin"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][4]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_fewsnet_rfe_comput, activate_1month_comput, activate_1monmin_comput)
    @collate(fewsnet_1moncum, formatter(formatter_in),formatter_out)
    def fewsnet_1monmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Maximum
    output_sprod="1monmax"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    reg_ex_in="[0-9]{4}([0-9]{4})"+in_prod_ident

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][4]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_fewsnet_rfe_comput, activate_1month_comput, activate_1monmax_comput)
    @collate(fewsnet_1moncum, formatter(formatter_in),formatter_out)
    def fewsnet_1monmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   1monDiff
    output_sprod="1mondiff"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    # inputs
    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][4]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "1monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input="{subpath[0][4]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(fewsnet_1monavg)
    @active_if(activate_fewsnet_rfe_comput, activate_1month_comput, activate_1mondiff_comput)
    @transform(fewsnet_1moncum, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def fewsnet_1mondiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   1monperc
    output_sprod="1monperc"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    # inputs
    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][4]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "1monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][4]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(fewsnet_1monavg)
    @active_if(activate_fewsnet_rfe_comput, activate_1month_comput, activate_1monperc_comput)
    @transform(fewsnet_1moncum, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def fewsnet_1monperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

    #   ---------------------------------------------------------------------
    #   1monnp
    output_sprod="1monnp"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + min + max
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][4]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod_1 = "1monmin"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, ext)
    ancillary_subdir_1      = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived',version, mapset)
    ancillary_input_1="{subpath[0][4]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "1monmax"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, ext)
    ancillary_subdir_2      = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived',version, mapset)
    ancillary_input_2="{subpath[0][4]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    @follows(fewsnet_1monmin, fewsnet_1monmax)
    @active_if(activate_fewsnet_rfe_comput, activate_1month_comput, activate_1monnp_comput)
    @transform(fewsnet_1moncum, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2), formatter_out)
    def fewsnet_1monnp(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "min_file": input_file[1],"max_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_make_vci(**args)

#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_fewsnet_rfe(pipeline_run_level=0,pipeline_run_touch_only=0, pipeline_printout_level=0,
                           pipeline_printout_graph_level=0):

    create_pipeline(starting_sprod='rfe')

    list = pipeline_get_task_names()
    print list
    logger.info("Entering routine %s" % 'processing_fewsnet_rfe')
    if pipeline_run_level > 0:
        logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level, touch_files_only=pipeline_run_touch_only)
    
    if pipeline_printout_level > 0:
        
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
