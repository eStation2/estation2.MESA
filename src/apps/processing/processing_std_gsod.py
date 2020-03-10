from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Compute the GSOD 1d interpolated product and 10d cumulation
#	author:  M.Clerici, BDMS Staff
#	date:	 30.11.2016
#   descr:	 Compute the GSOD 1d interpolated product (1d-gRf)and 10d cumulation (10d-gRf)
#	history: 1.0 - Initial Version
#

# Source my definitions
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os
import glob
import datetime
import tempfile
import shutil
# Import eStation2 modules

from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from lib.python.mapset import *

# Import third-party modules
from ruffus import *

# Flags to activate processing
activate_1d_gRf_comput = 1
activate_10d_gRf_comput = 0

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None):

    land_mask = '/eStation2/static/sadc_mask_byte_1km.tif'

    tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(prod),
                                  dir=es_constants.base_tmp_dir)

    #   ---------------------------------------------------------------------
    #   Create lists

    if proc_lists is None:
        proc_lists = functions.ProcLists()

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files (daily products)
    in_prod_ident_noext = functions.set_path_filename_no_date(prod, starting_sprod,mapset, version, '')
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod,mapset, version, '.shp')
    input_dir = es2_data_dir+functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    if starting_dates is not None:
        starting_files = []
        for my_date in starting_dates:
            if os.path.isfile(input_dir+my_date+in_prod_ident):
                starting_files.append(input_dir+my_date+in_prod_ident)
    else:
        starting_files=glob.glob(input_dir+"*"+in_prod_ident)

    #   ---------------------------------------------------------------------
    #   Define output files (1dmeas-interp)

    output_sprod = proc_lists.proc_add_subprod("1d-grf", "none", final=False,
                                                descriptive_name='1 Day interpolated',
                                                description='1 Day interpolated',
                                                frequency_id='e1day',
                                                date_format='YYYYMMDD',
                                                masked=False,
                                                timeseries_role='',
                                                active_default=True)

    prod_ident_1d_gRf = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_1d_gRf = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in="(?P<YYYYMMDD>[0-9]{8})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+subdir_1d_gRf+"{YYYYMMDD[0]}"+prod_ident_1d_gRf

    @active_if(activate_1d_gRf_comput)
    @transform(starting_files, formatter(formatter_in), formatter_out)
    def std_precip_1d_gRf(input_file, output_file):

        functions.check_output_dir(os.path.dirname(output_file))
        my_date = functions.get_date_from_path_full(input_file)
        layer = my_date+in_prod_ident_noext

        mapset_obj = MapSet()
        mapset_obj.assigndb(mapset)

        # Prepare tmpfile
        output_file_tmp = tmpdir+os.path.basename(output_file)

        # Extract info from mapset
        size_x = mapset_obj.size_x
        size_y = mapset_obj.size_y
        geo_transform = mapset_obj.geo_transform
        pixel_shift_x = geo_transform[1]
        pixel_shift_y = geo_transform[5]
        ulx = geo_transform[0]
        uly = geo_transform[3]
        lrx = ulx + pixel_shift_x*size_x
        lry = uly + pixel_shift_y*size_y

        txe = str(ulx)+' '+str(lrx)
        tye = str(uly)+' '+str(lry)
        te  = str(ulx)+' '+str(lry)+' '+str(lrx)+' '+str(uly)
        tr  = str(pixel_shift_x)+' '+str(pixel_shift_x)
        outsize = str(size_x)+' '+str(size_y)

        # Interpolate at the original resolution (no outsize)
        command = 'gdal_grid '\
                + ' -ot Float32 -of GTiff -co "compress=LZW" ' \
                + ' -txe ' + txe\
                + ' -tye ' + tye\
                + ' -zfield precipitat '\
                + ' -l '+layer \
                + ' -a invdist:power=2.0:smooting=1:radius1=0.0:radius2=0.0:angle=0.0:max_points=0:min_points=0:nodata:0.0 '\
                + input_file +' '+output_file_tmp
        try:
            os.system(command)
        except:
            pass

        # Interpolate at the original resolution
        command = 'gdalwarp '\
                + '-t_srs "EPSG:4326" '\
                + ' -of GTiff -co "compress=LZW" ' \
                + ' -te ' + te\
                + ' -tr ' + tr+ ' '\
                + output_file_tmp +' '+output_file
                # + ' -ts ' + outsize \

        try:
            print (command)
            os.system(command)
        except:
            pass
        try:
            shutil.rmtree(tmpdir)
        except:
            print ('Error in removing temporary directory. Continue')
            raise NameError('Error in removing tmpdir')

    #   ---------------------------------------------------------------------
    #   Define output files (10dmeas)

    output_sprod = proc_lists.proc_add_subprod("10d-grf", "none", final=False,
                                                descriptive_name='10 Day interpolated cum',
                                                description='10 Day interpolated cumulate',
                                                frequency_id='e1dekad',
                                                date_format='YYYYMMDD',
                                                masked=False,
                                                timeseries_role='',
                                                active_default=True)


    prod_ident_10dmeas = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_10dmeas = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_10dmeas():

        dekad_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in starting_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd)
            if mydekad_nbr not in dekad_list:
              dekad_list.append(mydekad_nbr)

        dekad_list = sorted(dekad_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        dekad_now = functions.conv_date_2_dekad(today_str)

        for dekad in dekad_list:
            # Exclude the current dekad
             if dekad != dekad_now:
                file_list = []
                my_dekad_str = functions.conv_dekad_2_date(dekad)
                expected_days = functions.day_per_dekad(my_dekad_str)

                for input_file in starting_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd[0:8])
                    if mydekad_nbr == dekad:
                        file_list.append(input_file)

                    output_file=es_constants.processing_dir+subdir_10dmeas+os.path.sep+my_dekad_str+prod_ident_10dmeas
                if len(file_list) >= expected_days-1:
                    yield (file_list, output_file)
                else:
                    print ('Too many missing files for dekad {0}'.format(my_dekad_str))

    @active_if(activate_10d_gRf_comput)
    @files(generate_parameters_10dmeas)
    def std_precip_10dmeas(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        # Prepare temporary working directory for intermediate results
        tmpdirpath = tempfile.mkdtemp()
        # Cumulated but not masked output
        tmp_output_file = tmpdirpath + os.path.sep + os.path.basename(output_file)

        # Call the function for cumulating
        args = {"input_file": input_file, "output_file": tmp_output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

        # Call the function for masking
        args = {"input_file": tmp_output_file, "mask_file": land_mask,
                "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "mask_value": 0, "out_value": 0}
        raster_image_math.do_mask_image(**args)

        # Remove temp directory
        shutil.rmtree(tmpdirpath)

#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_std_gsod(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                        pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                        starting_dates=None, write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_gsod')

    create_pipeline(prod, starting_sprod, mapset, version, starting_dates=starting_dates, proc_lists=None)

    spec_logger.info("Entering routine %s" % 'processing gsod')
    if pipeline_run_level > 0:
        spec_logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger,
                     log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_gsod.sqlite'),
                     checksum_level=0, one_second_per_job=True, multiprocess=1, multithread=0)
    
    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
