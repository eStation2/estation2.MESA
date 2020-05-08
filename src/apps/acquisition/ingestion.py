from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
#
#	purpose: Define the ingest service
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 20.02.2014
#   descr:	 Process input files into the specified 'mapset'
#	history: 1.0
#
#   TODO-LinkIT: for MCD45monthly aborts for out-of-memory in re-scaling data ! FTTB ingest only 2 windows

# source eStation2 base definitions
# from config import es_constants

# import standard modules
from builtins import open
from builtins import int
from future import standard_library

standard_library.install_aliases()
from builtins import map
from builtins import str
from builtins import range
from past.utils import old_div
import re
import tempfile
import zipfile
import bz2
import glob
import ntpath
import os
import time, datetime
import numpy as N
import time
import shutil
import gzip
import psutil
import csv
import sys
import tarfile

# import h5py

from multiprocessing import *

# import eStation2 modules
from database import querydb
from lib.python import functions
from lib.python import es_logging as log
from lib.python import mapset
from lib.python import metadata
from config import es_constants
from apps.processing import proc_functions
from apps.productmanagement import products
from apps.productmanagement import datasets

# TODO: On reference machines pygrip works! Not on our development VMs!
# TODO: Change to  if sys.platform != 'win32':
if sys.platform == 'win32':
    import pygrib

import fnmatch
from osgeo import gdal
from osgeo import osr

logger = log.my_logger(__name__)

ingest_dir_in = es_constants.ingest_dir
ingest_error_dir = es_constants.ingest_error_dir
data_dir_out = es_constants.processing_dir

def loop_ingestion(dry_run=False, test_one_product=None):

#    Driver of the ingestion process
#    Reads configuration from the database
#    Reads the list of files existing in input directory
#    Loops over file and call the ingestion script
#    Arguments: dry_run -> if 1, read tables and report activity ONLY

    logger.info("Entering routine %s" % 'drive_ingestion')
    echo_query = False

    while True:

        # Manage the ingestion of Historical Archives (e.g. eStation prods disseminated via EUMETCast - MESA_JRC_*.tif)
        # try:
        #     status = ingest_archives_eumetcast(dry_run=dry_run)
        # except:
        #     logger.error("Error in executing ingest_archives_eumetcast")

        # Get all active product ingestion records with a subproduct count.
        active_product_ingestions = querydb.get_ingestion_product(allrecs=True)

        for active_product_ingest in active_product_ingestions:

            logger.info("Ingestion active for product: [%s] subproduct N. %s" % (active_product_ingest[0],
                                                                                 active_product_ingest[2]))
            productcode = active_product_ingest[0]
            productversion = active_product_ingest[1]

            # Verify the test-one-product case
            do_ingest_source = True
            if test_one_product:
                if productcode != test_one_product:
                    do_ingest_source = False

            # For the current active product ingestion: get all
            product = {"productcode": productcode,
                       "version": productversion}
            logger.debug("Processing product: %s - version %s" % (productcode,  productversion))

            # Get the list of acquisition sources that are defined for this ingestion 'trigger'
            # (i.e. prod/version)
            # NOTE: the following implies there is 1 and only 1 '_native' subproduct associated to a 'product';
            native_product = {"productcode": productcode,
                              "subproductcode": productcode + "_native",
                              "version": productversion}

            sources_list = querydb.get_product_sources(**native_product)

            logger.debug("For product [%s] N. %s  source is/are found" % (productcode,len(sources_list)))

            systemsettings = functions.getSystemSettings()

            if do_ingest_source:
                for source in sources_list:

                    logger_spec = log.my_logger('apps.ingestion.'+productcode+'.'+productversion)
                    logger.debug("Processing Source type [%s] with id [%s]" % (source.type, source.data_source_id))
                    # Re-initialize the datasource_descr
                    datasource_descr = None
                    files = []
                    # Get the 'filenaming' info (incl. 'area-type') from the acquisition source
                    if source.type == 'EUMETCAST':
                        datasource_descr = querydb.get_datasource_descr(source_type=source.type, source_id=source.data_source_id)
                        datasource_descr = datasource_descr[0]
                        eumetcast_filter = datasource_descr.filter_expression_jrc
                        # for eumetcast_filter, datasource_descr in querydb.get_datasource_descr(source_type=source.type,
                        #                                                                        source_id=source.data_source_id):
                        # TODO-M.C.: check the most performing options in real-cases
                        files = [os.path.basename(f) for f in glob.glob(ingest_dir_in+'*') if re.match(eumetcast_filter, os.path.basename(f))]
                        my_filter_expr = eumetcast_filter
                        logger.info("Eumetcast Source: looking for files in %s - named like: %s" % (ingest_dir_in, eumetcast_filter))

                    if source.type == 'INTERNET':
                        # Implement file name filtering for INTERNET data source.
                        # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type=source.type,
                        #                                                                       source_id=source.data_source_id):
                        datasource_descr = querydb.get_datasource_descr(source_type=source.type, source_id=source.data_source_id)
                        datasource_descr = datasource_descr[0]
                        internet_filter = datasource_descr.files_filter_expression

                        # temp_internet_filter = internet_filter.files_filter_expression
                        temp_internet_filter = internet_filter
                        # TODO-M.C.: check the most performing options in real-cases
                        #files = [f for f in os.listdir(ingest_dir_in) if re.match(temp_internet_filter, f)]
                        files = [os.path.basename(f) for f in glob.glob(ingest_dir_in+'*') if re.match(temp_internet_filter, os.path.basename(f))]
                        my_filter_expr = temp_internet_filter
                        logger.info("Internet Source: looking for files in %s - named like: %s" % (ingest_dir_in, temp_internet_filter))
                    # See ES2-204
                    logger_spec.debug("Number of files found for product [%s] is: %s" % (active_product_ingest[0], len(files)))
                    if len(files) > 0:
                        # Get list of ingestions triggers [prod/subprod/mapset]
                        ingestions = querydb.get_ingestion_subproduct(allrecs=False, **product)

                        # Loop over ingestion triggers
                        subproducts = list()
                        for ingest in ingestions:

                            dates_not_in_filename = False
                            if ingest.input_to_process_re == 'dates_not_in_filename':
                                dates_not_in_filename = True

                            logger.debug(" --> processing subproduct: %s" % ingest.subproductcode)
                            args = {"productcode": product['productcode'],
                                    "subproductcode": ingest.subproductcode,
                                    "datasource_descr_id": datasource_descr.datasource_descr_id,
                                    "version": product['version']}
                            product_in_info = querydb.get_product_in_info(**args)
                            try:
                                re_process = product_in_info.re_process
                                re_extract = product_in_info.re_extract
                                nodata_value=product_in_info.no_data
                                sprod = {'subproduct': ingest.subproductcode,
                                         'mapsetcode': ingest.mapsetcode,
                                         're_extract': re_extract,
                                         're_process': re_process,
                                         'nodata': nodata_value}
                                subproducts.append(sprod)
                            except:
                                logger.warning("Subproduct %s not defined for source %s" % (ingest.subproductcode,datasource_descr.datasource_descr_id))

                        # Get the list of unique dates by extracting the date from all files.
                        dates_list = []

                        #   Check the case 'dates_not_in_filename' (e.g. GSOD -> yearly files continuously updated)
                        if dates_not_in_filename:

                            # Build the list of dates from datasource description
                            start_datetime=datetime.datetime.strptime(str(datasource_descr.start_date),"%Y%m%d")
                            if datasource_descr.end_date is None:
                                end_datetime = datetime.date.today()
                            else:
                                end_datetime=datetime.datetime.strptime(str(datasource_descr.end_date),"%Y%m%d")

                            all_starting_dates = proc_functions.get_list_dates_for_dataset(product_in_info.productcode,\
                                                                                       product_in_info.subproductcode,\
                                                                                       product_in_info.version,\
                                                                                       start_date=datasource_descr.start_date,
                                                                                       end_date=datasource_descr.end_date)

                            my_dataset = products.Dataset(product_in_info.productcode,
                                                          product_in_info.subproductcode,
                                                          ingest.mapsetcode,
                                                          version=product_in_info.version,
                                                          from_date=start_datetime,
                                                          to_date=end_datetime)
                            my_dates = my_dataset.get_dates()

                            my_formatted_dates = []
                            for my_date in my_dates:
                                my_formatted_dates.append(my_dataset._frequency.format_date(my_date))

                            my_missing_dates = []
                            for curr_date in all_starting_dates:
                                if curr_date not in my_formatted_dates:
                                    my_missing_dates.append(curr_date)

                            dates_list = sorted(my_missing_dates, reverse=False)

                        else:
                            # Build the list of dates from filenames
                            for filename in files:
                                date_position = int(datasource_descr.date_position)
                                if datasource_descr.format_type == 'delimited':
                                    splitted_fn = re.split(datasource_descr.delimiter, filename)
                                    date_string = splitted_fn[date_position]
                                    if len(date_string) > len(datasource_descr.date_format):
                                        date_string=date_string[0:len(datasource_descr.date_format)]
                                    dates_list.append(date_string)
                                else:
                                    dates_list.append(filename[date_position:date_position + len(datasource_descr.date_format)])

                            dates_list = set(dates_list)
                            dates_list = sorted(dates_list, reverse=False)

                        # Loop over dates and get list of files
                        for in_date in dates_list:
                            if dates_not_in_filename:
                                date_fileslist = [ingest_dir_in + l for l in files]
                            else:
                                # Refresh the files list (some files have been deleted)
                                files = [os.path.basename(f) for f in glob.glob(ingest_dir_in+'*') if re.match(my_filter_expr, os.path.basename(f))]
                                logger_spec.debug("     --> processing date, in native format: %s" % in_date)
                                # Get the list of existing files for that date
                                regex = re.compile(".*(" + in_date + ").*")
                                date_fileslist = [ingest_dir_in + m.group(0) for l in files for m in [regex.search(l)] if m]
                            # Pass list of files to ingestion routine
                            if (not dry_run):
                                try:
                                    result = ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger_spec, echo_query=echo_query)
                                except:
                                    logger.error("Error in ingestion of file [%s] " % (functions.conv_list_2_string(date_fileslist)))
                                else:
                                    # Result is None means we are still waiting for some files to be received. Keep files in /data/ingest
                                    # dates_not_in_filename means the input files contains many dates (e.g. GSOD precip)
                                    if result is not None and not dates_not_in_filename:
                                        if source.store_original_data or systemsettings['type_installation'] == 'Server':
                                        # Special case for mesa-proc @ JRC
                                        # Copy to 'Archive' directory
                                            output_directory = data_dir_out + functions.set_path_sub_directory(product['productcode'],
                                                                                                           sprod['subproduct'],
                                                                                                           'Native',
                                                                                                           product['version'],
                                                                                                           'dummy_mapset_arg' )
                                            functions.check_output_dir(output_directory)
                                            # Archive the files
                                            for file_to_move in date_fileslist:
                                                logger_spec.debug("     --> now archiving input files: %s" % file_to_move)
                                                new_location=output_directory+os.path.basename(file_to_move)
                                                try:
                                                    if os.path.isfile(file_to_move):
                                                        shutil.move(file_to_move, new_location)
                                                    else:
                                                        logger_spec.debug("     --> file to be archived cannot be found: %s" % file_to_move)
                                                except:
                                                    logger_spec.debug("     --> error in archiving file: %s" % file_to_move)

                                        else:
                                            # Delete the files
                                            for file_to_remove in date_fileslist:
                                                logger_spec.debug("     --> now deleting input files: %s" % file_to_remove)
                                                try:
                                                    if os.path.isfile(file_to_remove):
                                                        os.remove(file_to_remove)
                                                    else:
                                                        logger_spec.debug("     --> file to be deleted cannot be found: %s" % file_to_remove)
                                                except:
                                                    logger_spec.debug("     --> error in deleting file: %s" % file_to_remove)

                            else:
                                time.sleep(10)

        # Wait at the end of the loop
        logger.info("Entering sleep time of  %s seconds" % str(10))
        time.sleep(10)


def ingest_archives_eumetcast(dry_run=False):
    #    Ingest the files in format MESA_JRC_<prod>_<sprod>_<date>_<mapset>_<version>
    #    disseminated by JRC through EUMETCast.
    #    Gets the list of products/version/subproducts active for ingestion and for processing
    #    Arguments: dry_run -> if 1, read tables and report activity ONLY

    logger.info("Entering routine %s" % 'ingest_archives_eumetcast')
    echo_query = False

    # Get all active product ingestion records with a subproduct count.
    active_product_ingestions = querydb.get_ingestion_product(allrecs=True)
    for active_product_ingest in active_product_ingestions:

        productcode = active_product_ingest[0]
        productversion = active_product_ingest[1]

        # For the current active product ingestion: get all
        product = {"productcode": productcode,
                   "version": productversion}

        # Get the list of acquisition sources that are defined for this ingestion 'trigger'
        # (i.e. prod/version)
        # NOTE: the following implies there is 1 and only 1 '_native' subproduct associated to a 'subproduct';
        native_product = {"productcode": productcode,
                              "subproductcode": productcode + "_native",
                              "version": productversion}
        sources_list = querydb.get_product_sources(**native_product)

        logger.debug("For product [%s] N. %s  source is/are found" % (productcode,len(sources_list)))

        ingestions = querydb.get_ingestion_subproduct(allrecs=False, **product)
        for ingest in ingestions:
            logger.debug("Looking for product [%s]/version [%s]/subproducts [%s]/mapset [%s]" % (productcode, productversion,ingest.subproductcode,ingest.mapsetcode))
            ingest_archives_eumetcast_product(productcode, productversion,ingest.subproductcode,ingest.mapsetcode,dry_run=dry_run)

    # Get all active processing chains [product/version/algo/mapset].
    active_processing_chains = querydb.get_active_processing_chains()
    for chain in active_processing_chains:
        a = chain.process_id
        logger.debug("Processing Chain N.:%s" % str(chain.process_id))
        processed_products = querydb.get_processing_chain_products(chain.process_id, type='output')
        for processed_product in processed_products:
            productcode = processed_product.productcode
            version = processed_product.version
            subproductcode = processed_product.subproductcode
            mapset = processed_product.mapsetcode
            logger.debug("Looking for product [%s]/version [%s]/subproducts [%s]/mapset [%s]" % (productcode, version,subproductcode,mapset))
            ingest_archives_eumetcast_product(productcode, version,subproductcode,mapset,dry_run=dry_run)


    # Get the list of files that have been treated
    working_dir=es_constants.es2globals['base_tmp_dir']+os.path.sep+'ingested_files'
    trace_files=glob.glob(working_dir+os.path.sep+'*tbd')
    if len(trace_files)> 0:
        for trace in trace_files:
            filename=os.path.basename(trace).strip('.tdb')
            file_path=es_constants.es2globals['ingest_dir']+os.path.sep+filename
            logger.debug("Removing file %s/" % file_path)
            if os.path.isfile(file_path):
                os.remove(file_path)
            # Remove trace file also
            os.remove(trace)

def ingest_archives_eumetcast_product(product_code, version, subproduct_code, mapset_id, dry_run=False,input_dir=None, no_delete=False):

#    Ingest all files of type MESA_JRC_ for a give prod/version/subprod/mapset
#    Note that mapset is the 'target' mapset
#    input_dir = if None -> looks in ingest_dir (default for EUMETCast dissemination)
#                if defined -> looks in the specific location (for Historical Archives)
#

    # Manage the input_dir option
    if input_dir is None:
        input_dir = es_constants.es2globals['ingest_dir']

    logger.debug("Looking for product [%s]/version [%s]/subproducts [%s]/mapset [%s]" % (product_code, version, subproduct_code, mapset_id))
    # match_regex = es_constants.es2globals['prefix_eumetcast_files'] + product_code + '_' + subproduct_code + '_*_' + version + '*'
    match_regex = '*' + product_code + '_' + subproduct_code + '_*_' + version + '*'

    logger.debug("Looking in directory: %s" % input_dir)
    # Get the list of matching files in /data/ingest
    available_files=[]
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in fnmatch.filter(filenames, match_regex):
            available_files.append(os.path.join(root, filename))

    # Call the ingestion routine
    if len(available_files)>0:
        for in_file in available_files:
            if dry_run:
                logger.info("Found file: %s" % in_file)
            else:
                try:
                    ingest_file_archive(in_file, mapset_id, echo_query=False, no_delete=no_delete)
                except:
                    logger.warning("Error in ingesting file %s" % in_file)


def ingestion(input_files, in_date, product, subproducts, datasource_descr, my_logger, echo_query=False, test_mode=False):
#   Manages ingestion of 1/more file/files for a given date
#   Arguments:
#       input_files: input file full names
#       product: product description name (for DB insertions)
#       subproducts: list of subproducts to be ingested. Contains dictionaries such as:
#
#                sprod = {'subproduct': subproductcode,
#                         'mapsetcode': mapsetcode,
#                         're_extract': regexp to identify files to extract from .zip (only for zip archives)
#                         're_process': regexp to identify files to be processed (there might be ancillary files)}
#
#       datasource_descr: datasource description object (incl. native_mapset, compose_area_method, ..)
#       my_logger: trigger-specific logger
#
#   Returns:
#       0 -> ingestion OK; files to be removed/stored
#       1 -> ingestion wrong; files to be copied to /data/ingest.wrong
#       None -> some mandatory files are missing: wait and do not touch files
#
    data_dir_out = es_constants.processing_dir
    my_logger.info("Entering routine %s for prod: %s and date: %s" % ('ingestion', product['productcode'], in_date))

    preproc_type = datasource_descr.preproc_type
    native_mapset_code = datasource_descr.native_mapset

    do_preprocess = 0
    composed_file_list = None

    # Create temp output dir
    try:
        # Reduce the length of the tmp_dir: the resulting path was too long for operating in the docker container (see ES2-544)
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(input_files[0])[0:6],
                                  dir=es_constants.base_tmp_dir)
    except:
        my_logger.error('Cannot create temporary dir ' + es_constants.base_tmp_dir + '. Exit')
        raise NameError('Error in creating tmpdir')

    if preproc_type != None and preproc_type != 'None' and preproc_type != '""' and preproc_type != "''" and preproc_type != '':
        do_preprocess = 1

    if do_preprocess == 1:
        my_logger.debug("Calling routine %s" % 'preprocess_files')
        try:
            composed_file_list = pre_process_inputs(preproc_type, native_mapset_code, subproducts, input_files, tmpdir,
                                                    my_logger, in_date=in_date)

            # Pre-process returns None if there are not enough files for continuing
            if composed_file_list is None:
                logger.debug('Waiting for additional files to be received. Return')
                shutil.rmtree(tmpdir)
                return None

            # Check if -1 is returned, i.e. nothing to do on the passed files (e.g. S3A night-files)
            if composed_file_list is -1:
                logger.debug('Nothing to do on the passed files. Return')
                shutil.rmtree(tmpdir)
                return -1
        except:
            # Error occurred and was NOT detected in pre_process routine
            my_logger.warning("Error in ingestion for prod: %s and date: %s" % (product['productcode'], in_date))
            # Move files to 'error/storage' directory (ingest.wrong)
            if not test_mode:
                for error_file in input_files:
                    if os.path.isfile(ingest_error_dir+os.path.basename(error_file)):
                        shutil.os.remove(ingest_error_dir+os.path.basename(error_file))
                    try:
                        shutil.move(error_file, ingest_error_dir)
                    except:
                        my_logger.warning("Error in moving file: %s " % error_file)

            shutil.rmtree(tmpdir)
            raise NameError('Caught Error in preprocessing routine')

        # Error occurred and was detected in pre_process routine
        if str(composed_file_list)=='1':
            my_logger.warning("Error in ingestion for prod: %s and date: %s" % (product['productcode'], in_date))
            # Move files to 'error/storage' directory
            if not test_mode:
                for error_file in input_files:
                    if os.path.isfile(ingest_error_dir+os.path.basename(error_file)):
                        shutil.os.remove(ingest_error_dir+os.path.basename(error_file))
                    try:
                        shutil.move(error_file, ingest_error_dir)
                    except:
                        my_logger.warning("Error in moving file: %s " % error_file)

            shutil.rmtree(tmpdir)
            raise NameError('Detected Error in preprocessing routine')
    else:
        composed_file_list = input_files

    try:
        ingest_file(composed_file_list, in_date, product, subproducts, datasource_descr, my_logger, in_files=input_files,
                echo_query=echo_query)
    except:
        my_logger.warning("Error in ingestion for prod: %s and date: %s" % (product['productcode'], in_date))
        # Move files to 'error/storage' directory
        if not test_mode:
            for error_file in input_files:
                if os.path.isfile(ingest_error_dir+os.path.basename(error_file)):
                    shutil.os.remove(ingest_error_dir+os.path.basename(error_file))
                try:
                    shutil.move(error_file, ingest_error_dir)
                except:
                    my_logger.warning("Error in moving file: %s " % error_file)

        shutil.rmtree(tmpdir)
        raise NameError('Error in ingestion routine')

    # -------------------------------------------------------------------------
    # Remove the Temp working directory
    # -------------------------------------------------------------------------
    try:
        shutil.rmtree(tmpdir)
    except:
        logger.error('Error in removing temporary directory. Continue')
        raise NameError('Error in removing tmpdir')

    return 0


def pre_process_msg_mpe (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process msg_mpe files
#   4 expected segments as input
#   Returns: pre_processed_list -> list of preprocessed files (to go on with ingestion)
#            None: waiting for additional files (keep existing files in /data/ingest)
#            Raise Exception: something went wrong (move existing files to /data/ingest.wrong)
#                             This applies also when there are <4 files, older than 1 day)

    # Output list of pre-processed files
    pre_processed_list = []

    # Test the files exist
    for ifile in input_files:
        if not os.path.isfile(ifile):
            my_logger.error('Input file does not exist')
            raise Exception("Input file does not exist: %s" % ifile)

    # Test the number of available files (must be 4 - see Tuleap ticket #10903)
    if len(input_files) != 4:

        # Check the datetime of input files: store the delta-days of the latest file
        min_delta_days = 10
        for ifile in input_files:
            mod_time_delta =  datetime.datetime.today()- datetime.datetime.fromtimestamp(os.path.getmtime(ifile))
            if mod_time_delta.days < min_delta_days:
                min_delta_days = mod_time_delta.days
        my_logger.debug('Min delta days found is {0}'.format(min_delta_days))

        # Latest file older than 2 days -> error
        if min_delta_days > 2:
            my_logger.info('Incomplete reception: <4 files older than 2 days. Error')
            raise Exception("Incomplete reception. Error")
        else:
            my_logger.info('Only {0} files present. Wait for the ingestion'.format(len(input_files)))
            return None

    # Remove small header and concatenate to 'grib' output
    input_files.sort()
    out_tmp_grib_file = tmpdir + os.path.sep + 'MSG_MPE_grib_temp.grb'
    out_tmp_tiff_file = tmpdir + os.path.sep + 'MSG_MPE_tiff_temp.grb'

    outfid = open(out_tmp_grib_file, "w")
    for ifile in input_files:
        infid = open(ifile, "r")
        # skip the PK_header (103 bytes)
        infid.seek(103)
        data = infid.read()
        outfid.write(data)
        infid.close()
    outfid.close()

    # Read the .grb and convert to gtiff (GDAL does not do it properly)
    grbs = pygrib.open(out_tmp_grib_file)
    grb = grbs.select(name='Instantaneous rain rate')[0]
    data = grb.values
    # Rotate 180 (i.e. flip both horiz/vertically) - bug from UFA12 Forum/SADC
    rev_data = N.fliplr(data)
    data = N.flipud(rev_data)
    output_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)
    output_ds = output_driver.Create(out_tmp_tiff_file, 3712, 3712, 1, gdal.GDT_Float64)
    output_ds.GetRasterBand(1).WriteArray(data)

    for subproduct in subproducts:
        pre_processed_list.append(out_tmp_tiff_file)

    return pre_processed_list


def pre_process_mpe_umarf (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process msg_mpe files in UMARF format
#   Typical filename is MSG3-SEVI-MSGMPEG-0100-0100-20160331234500.000000000Z-20160331235848-1193222.grb.gz
#   Returns: pre_processed_list -> list of preprocessed files (to go on with ingestion)
#            Raise Exception: something went wrong (move existing files to /data/ingest.wrong)

    # Output list of pre-processed files
    pre_processed_list = []

    # Test the files exist
    files_list = functions.element_to_list(input_files)
    for input_file in files_list:

        if not os.path.isfile(input_file):
            my_logger.error('Input file does not exist')
            raise Exception("Input file does not exist: %s" % input_file)

        out_tmp_tiff_file = tmpdir + os.path.sep + 'MSG_MPE_temp.tif'
        out_tmp_grib_file = tmpdir + os.path.sep + 'MSG_MPE_temp.grb'

        # Read the .grb and convert to gtiff (GDAL does not do it properly)

        with open(out_tmp_grib_file,'wb') as f_out, gzip.open(input_file,'rb') as f_in:                 # Create ZipFile object
            shutil.copyfileobj(f_in, f_out)

        grbs = pygrib.open(out_tmp_grib_file)
        grb = grbs.select(name='Instantaneous rain rate')[0]
        data = grb.values
        # Rotate 180 (i.e. flip both horiz/vertically) - bug from UFA12 Forum/SADC
        rev_data = N.fliplr(data)
        data = N.flipud(rev_data)
        output_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)
        output_ds = output_driver.Create(out_tmp_tiff_file, 3712, 3712, 1, gdal.GDT_Float64)
        output_ds.GetRasterBand(1).WriteArray(data)

        for subproduct in subproducts:
            pre_processed_list.append(out_tmp_tiff_file)

    return pre_processed_list


def pre_process_modis_hdf4_tile (subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process MODIS HDF4 tiled files
#
#   TODO-M.C.: add a mechanism to check input_files vs. mapsets ??
#              Optimize by avoiding repetition of the gdal_merge for the same sub_product, different mapset ?
#
    # Prepare the output file list
    pre_processed_list = []
    # Build a list of subdatasets to be extracted
    list_to_extr = []
    for sprod in subproducts:
        if sprod != 0:
            list_to_extr.append(sprod['re_extract'])

    # Extract the relevant datasets from all files
    for index, ifile in enumerate(input_files):

        # Test the file exists
        if not os.path.isfile(ifile):
            my_logger.error('Input file does not exist ' + ifile)
            raise Exception("Input file does not exist: %s" % ifile)

        # Test the hdf file and read list of datasets
        hdf = gdal.Open(ifile)
        sdsdict = hdf.GetMetadata('SUBDATASETS')
        sdslist = [sdsdict[k] for k in list(sdsdict.keys()) if '_NAME' in k]

        # Loop over datasets and check if they have to be extracted
        for subdataset in sdslist:
            id_subdataset = subdataset.split(':')[-1]
            if id_subdataset in list_to_extr:
                outputfile = tmpdir + os.path.sep + id_subdataset + '_' + str(index) + '.tif'
                sds_tmp = gdal.Open(subdataset)
                write_ds_to_geotiff(sds_tmp, outputfile)
                # sds_tmp = None

    # Loop over the subproducts extracted and do the merging.
    for sprod in subproducts:
        if sprod != 0:
            id_subproduct = sprod['re_extract']
            id_mapset = sprod['mapsetcode']
            out_tmp_file_gtiff = tmpdir + os.path.sep + id_subproduct + '_' + id_mapset + '.tif.merged'

            file_to_merge = glob.glob(tmpdir + os.path.sep + id_subproduct + '*.tif')
            # Take gdal_merge.py from es2globals
            command = es_constants.gdal_merge + ' -init 9999 -co \"compress=lzw\" -o '
            command += out_tmp_file_gtiff
            for file_add in file_to_merge:
                command += ' '
                command += file_add
            my_logger.debug('Command for merging is: ' + command)
            os.system(command)
            pre_processed_list.append(out_tmp_file_gtiff)

    return pre_processed_list


def pre_process_merge_tile(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process Merge tiled files from PROBAV 100 and 300 meters
#   Uses Gdal_merge to merge the file and gdal_translate to compress the file and assign BIGTIFF NO
#
    # Prepare the output file list
    pre_processed_list = []
    inter_processed_list = []
    # Check at least 1 file is reprojected file is there
    if len(input_files) == 0:
        my_logger.debug('No files. Return')
        return -1

    sprod = subproducts[0]
    nodata = sprod['nodata']

    if len(input_files) > 0:
        #
        # for file in input_files:
        #     filename = os.path.basename(file)
        #     clipped_file = os.path.join(tmpdir,filename)
        #
        #     # -------------------------------------------------------------------------
        #     # STEP 0: Gdalwarp to mask with shape file
        #     #  -------------------------------------------------------------------------
        #     try:
        #         command = 'gdalwarp '
        #         command += ' -co \"COMPRESS=LZW\"'
        #         command += ' -srcnodata '+str(nodata)
        #         command += ' -dstnodata '+str(nodata)+' -crop_to_cutline -cutline /eStation2/layers/AFR_00_g2015_2014.geojson '
        #         command += file+' ' + clipped_file
        #         # command += ' -ot BYTE '
        #         # for file in input_files:
        #         #     command += ' '+file
        #         my_logger.debug('Command for masking is: ' + command)
        #         os.system(command)
        #         inter_processed_list.append(clipped_file)
        #     except:
        #         pass
        #
        # OUTPUT FILES
        output_file = tmpdir + os.path.sep + 'merge_output.tif'
        output_file_vrt = tmpdir + os.path.sep + 'merge_output_rescaled.vrt'
        output_file_compressed = tmpdir + os.path.sep + 'merge_output_compressed.tif'

        # -------------------------------------------------------------------------
        # STEP 1: Merge all input products into a 'tmp' file
        # -------------------------------------------------------------------------
        # try:
        #     input_files_str = ''
        #     for file_add in input_files:
        #         input_files_str += ' '
        #         input_files_str += file_add
        #     # command = 'gdalwarp -srcnodata "{}" -dstnodata "{}" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(scaled_no_data, int(no_data),
        #     #      input_files_str, out_tmp_file_gtiff)
        #     command = 'gdalwarp '
        #     command += ' -co \"COMPRESS=LZW\"'
        #     command += ' -srcnodata '+str(nodata)
        #     command += ' -dstnodata '+str(nodata)+' '
        #     command += input_files_str+' ' + output_file
        #     # command += ' -ot BYTE '
        #     # for file in input_files:
        #     #     command += ' '+file
        #     my_logger.debug('Command for merging is: ' + command)
        #     os.system(command)
        #     # inter_processed_list.append(clipped_file)
        # except:
        #     pass

        try:
            command = es_constants.gdal_merge
            # command += ' -co \"compress=lzw\"'
            # command += ' -co \"BIGTIFF=Yes\"'
            command += ' -init '+str(nodata)
            command += ' -o ' + output_file
            command += ' -ot BYTE '
            command += ' -of GTiff '
            for file in input_files:
                command += ' '+file

            my_logger.debug('Command for merging is: ' + command)
            os.system(command)
        except:
            pass

        # # Rescale the data using gdal_calc( In this case of 300m and 100m rescale is possible with gdal_calc but due the storage problem we are storing it in BYTE
        # mask_layer='/data/processing/vgt-ndvi/proba300-v1.0/rasterize_full_afr_300m.tif'
        # rescale_func = "A*B"#"\"(A*0.004-0.08)*1000\""
        # rescale_command = "gdal_calc.py --NoDataValue=255 --type BYTE --co \"TILED=YES\" --co \"COMPRESS=LZW\" -A "+output_file+" -B "+mask_layer+" --calc="+rescale_func+" --outfile="+output_file_vrt
        # os.system(rescale_command)

        try:
            command = es_constants.gdal_translate
            command += ' -co \"compress=lzw\"'
            command += ' -co \"BIGTIFF=No\"'
            command += ' -ot BYTE '
            command += ' '+output_file
            # command += ' ' + output_file_vrt #To be changed if rescaling is done
            command += ' '+output_file_compressed

            my_logger.debug('Command for compress is: ' + command)
            os.system(command)

        except:
            pass

        pre_processed_list.append(output_file_compressed)

    # Else pass the single input file
    else:
        pre_processed_list.append(input_files[0])

    return pre_processed_list


def pre_process_retile_vito (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process Merge tiled files
#
#   TODO-M.C.: add a mechanism to check input_files vs. mapsets ??
#              Optimize by avoiding repetition of the gdal_merge for the same sub_product, different mapset ?
#
    # Prepare the output file list
    pre_processed_list = []
    # # Build a list of subdatasets to be extracted
    # Check at least 1 file is reprojected file is there
    if len(input_files) == 0:
        my_logger.debug('No files. Return')
        return -1

    args = {"productcode": product['productcode'],
            "subproductcode": subproducts[ii]['subproduct'],
            "datasource_descr_id": datasource_descr.datasource_descr_id,
            "version": product['version']}

    # Get information from sub_dataset_source table
    product_in_info = querydb.get_product_in_info(**args)

    # Loop over input file to create VRT files
    if len(input_files) > 1:
        for input_file in input_files:
            out_vrt_file = tmpdir + os.path.sep+ os.path.split(input_file)[-1]+ ".vrt"
            # convert_vrt_cmd = "gdalwarp -of vrt -ot Float32 "+ input_file + " " + input_file +".vrt"
            convert_vrt_cmd = "gdal_translate -of vrt -ot Float32 " + input_file + " " + out_vrt_file
            os.system(convert_vrt_cmd)

        # List all the vrt file and store in text file
        text_file_ls = tmpdir + os.path.sep + "list.txt"
        os.system("ls "+tmpdir+"/*.vrt >" + text_file_ls)

        # Merge all the vrt files with gdalbuildvrt
        merged_vrt_file = tmpdir + os.path.sep+ "merged_vrt.vrt"#tmpdir + os.path.sep + "merged_vrt.vrt"
        os.system("gdalbuildvrt -input_file_list " + text_file_ls + " "+ merged_vrt_file)

        # Create retile dir functions.check_output_dir(output_dir)
        output_retile_dir = tmpdir + os.path.sep + "retiled"
        functions.check_output_dir(output_retile_dir)

        # Convert merged vrt file to Gtiff file with the compression
        cmd_retile = "gdal_retile.py -v -ps 16384 16384 -co \"TILED=YES\" -co \"COMPRESS=LZW\" -targetDir "+output_retile_dir+" "+tmpdir+"/*.vrt"
        os.system(cmd_retile)
        pre_processed_list.append(glob.glob(output_retile_dir))

        for retile_file in glob.glob(output_retile_dir):
            gdal_calc_cmd = "gdal_calc.py --format=VRT --type Int16 -A "+retile_file+" --calc=\"(A*0.004-0.08)*1000\" --outfile=/data/ingest/test_calc_int16.vrt"

    else:
        pre_processed_list.append(input_files[0])
            # sds_tmp = None

    return pre_processed_list



def drive_pre_process_lsasaf_hdf5(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Drive the Pre-process LSASAF HDF5 files
#
    # This is a quick fix of the gdal 1.9.2 bug on closing HDF files (see http://trac.osgeo.org/gdal/ticket/5103)
    # Since the files cannot be closed, and end up in reaching the max-number of open files (1024) we
    # call the routine as a detached process

    module_name = 'ingestion'
    function_name = 'pre_process_lsasaf_hdf5'
    proc_dir = __import__("apps.acquisition")
    proc_pck = getattr(proc_dir, "acquisition")
    proc_mod = getattr(proc_pck, module_name)
    proc_func= getattr(proc_mod, function_name)
    out_queue = Queue()

    # Check the input files (corrupted would stop the detached process)
    for infile in input_files:
        try:
            command = 'bunzip2 -t {0} > /dev/null 2>/dev/null'.format(infile)
            status = os.system(command)
            if status:
                my_logger.error('File {0} is not a valid bz2. Exit'.format(os.path.basename(infile)))
                raise Exception('Error preproc')
        except:
            my_logger.error('Error in checking file {0}. Exit'.format(os.path.basename(infile)))
            raise Exception('Error preproc')

    args = [subproducts, tmpdir, input_files, my_logger, out_queue]
    try:
        p = Process(target=proc_func, args=args)
        p.start()
        pre_processed_list = out_queue.get()
        p.join()
    except:
        my_logger.error('Error in calling pre_process_lsasaf_hdf5 as detached process')
        raise NameError('Error in calling pre_process_lsasaf_hdf5 as detached process')

    return pre_processed_list


def pre_process_lsasaf_hdf5(subproducts, tmpdir , input_files, my_logger, out_queue):
# -------------------------------------------------------------------------------------------------------
#   Pre-process LSASAF HDF5 files
#
    # It receives in input the list of the (.bz2) files (e.g. NAfr, SAfr)
    # It unzips the files to tmpdir, extracts relevant sds from hdf, does the merging in original proj.
    # Note that it 'replicates' the file_list for each target mapset

    pre_processed_files = []
    unzipped_input_files = []

    # Loop over input files and unzips
    for index, ifile in enumerate(input_files):
        my_logger.debug('Processing input file  ' + ifile)
        # Test the file exists
        if not os.path.isfile(ifile):
            my_logger.error('Input file does not exist ' + ifile)
            return 1
            # raise Exception("Input file does not exist: %s" % ifile)
        # Unzip to tmpdir and add to list
        if re.match('.*\.bz2', ifile):
            try:
                my_logger.debug('Decompressing bz2 file: ' + ifile)
                bz2file = bz2.BZ2File(ifile)                    # Create ZipFile object
                data = bz2file.read()                           # Get the list of its contents
                filename = os.path.basename(ifile)
                filename = filename.replace('.bz2', '')
                myfile_path = os.path.join(tmpdir, filename)
                myfile = open(myfile_path, "wb")
                myfile.write(data)
                unzipped_input_files.append(myfile_path)
            except:
                my_logger.error('Error in unzipping my file: ' + ifile)
                if myfile is not None:
                    myfile.close()
                if bz2file is not None:
                    bz2file.close()
                # Need to put something, otherwise goes in error
                out_queue.put('')
                return 1
                # raise Exception("Error in unzipping file: %s" % ifile)
            else:
                myfile.close()
                bz2file.close()

    # Build a list of subdatasets to be extracted
    list_to_extr = []
    for sprod in subproducts:
        if sprod != 0:
            list_to_extr.append(sprod['re_extract'])

    # Loop over unzipped files and extract relevant SDSs
    for unzipped_file in unzipped_input_files:
        my_logger.debug('Processing unzipped file: ' + unzipped_file)
        # Identify the region from filename
        region = unzipped_file.split('_')[-2]
        my_logger.debug('Region of unzipped file is :' + region)
        # Test the file exists
        if not os.path.isfile(unzipped_file):
            my_logger.error('Input file does not exist ' + unzipped_file)
            out_queue.put('')
            # raise Exception("Input file does not exist: %s" % unzipped_file)
            return 1
        # Test the hdf file and read list of datasets
        try:
            hdf = gdal.Open(unzipped_file)
            sdsdict = hdf.GetMetadata('SUBDATASETS')
            sdslist = [sdsdict[k] for k in list(sdsdict.keys()) if '_NAME' in k]
            sdsdict = None
            # Loop over datasets and check if they have to be extracted
            for subdataset in sdslist:
                id_subdataset = subdataset.split(':')[-1]
                id_subdataset = id_subdataset.replace('//', '')
                if id_subdataset in list_to_extr:
                    outputfile = tmpdir + os.path.sep + id_subdataset + '_' + region + '.tif'
                    sds_tmp = gdal.Open(subdataset)
                    write_ds_to_geotiff(sds_tmp, outputfile)
                    sds_tmp = None
            hdf = None
            #close_hdf_dataset(unzipped_file)
        except:
            my_logger.error('Error in extracting SDS')
            hdf = None
            #close_hdf_dataset(unzipped_file)
            out_queue.put('')
            return 1
            # raise Exception('Error in extracting SDS')

    # For each dataset, merge the files, by using the dedicated function
    for id_subdataset in list_to_extr:
        files_to_merge = glob.glob(tmpdir + os.path.sep + id_subdataset + '*.tif')

        output_file = tmpdir + os.path.sep + id_subdataset + '.tif'
        # Ensure a file exist for each Mapsets as well
        pre_processed_files.append(output_file)

    try:
        mosaic_lsasaf_msg(files_to_merge, output_file, '')
    except:
        my_logger.error('Error in mosaicing')
        out_queue.put('')
        return 1
        # raise Exception('Error in mosaicing')

    my_logger.debug('Output file generated: ' + output_file)

    out_queue.put(pre_processed_files)
    return 0


def pre_process_pml_netcdf(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process PML NETCDF files
#
# It receives in input the list of the (.bz2) files (windows)
# It unzips the files to tmpdir and does the merging in original proj, for each datasets
#
    unzipped_input_files = []

    # Prepare the output file list
    pre_processed_list = []

    # Loop over input files and unzips
    # TODO-M.C.: create and call a function for unzip
    for index, ifile in enumerate(input_files):
        logger.debug('Processing input file  ' + ifile)
        # Test the file exists
        if not os.path.isfile(ifile):
            my_logger.error('Input file does not exist ' + ifile)
            raise Exception("Input file does not exist: %s" % ifile)

        # Unzip to tmpdir and add to list
        if re.match('.*\.bz2', ifile):
            my_logger.debug('Decompressing bz2 file: ' + ifile)
            bz2file = bz2.BZ2File(ifile)                    # Create ZipFile object
            data = bz2file.read()                           # Get the list of its contents
            filename = os.path.basename(ifile)
            filename = filename.replace('.bz2', '')
            myfile_path = os.path.join(tmpdir, filename)
            myfile = open(myfile_path, "wb")
            myfile.write(data)
            myfile.close()
            bz2file.close()
            unzipped_input_files.append(myfile_path)        # It contains a list of .nc

    # Build a list of subdatasets to be extracted
    list_to_extr = []
    for sprod in subproducts:
        if sprod != 0:
            list_to_extr.append(sprod['re_extract'])

    geotiff_files = []
    # Loop over unzipped files and extract the relevant sds to tmp geotiffs
    for input_file in unzipped_input_files:

        # Test the. nc file and read list of datasets
        netcdf = gdal.Open(input_file)
        sdslist = netcdf.GetSubDatasets()

        if len(sdslist) >= 1:
            # Loop over datasets and extract the one from each unzipped
            for subdataset in sdslist:
                netcdf_subdataset = subdataset[0]
                id_subdataset = netcdf_subdataset.split(':')[-1]

                if id_subdataset in list_to_extr:
                    selected_sds = 'NETCDF:' + input_file + ':' + id_subdataset
                    sds_tmp = gdal.Open(selected_sds)
                    filename = os.path.basename(input_file) + '.geotiff'
                    myfile_path = os.path.join(tmpdir, filename)
                    write_ds_to_geotiff(sds_tmp, myfile_path)
                    sds_tmp = None
                    geotiff_files.append(myfile_path)
        else:
          # No subdatasets: e.g. SST -> read directly the .nc
            filename = os.path.basename(input_file) + '.geotiff'
            myfile_path = os.path.join(tmpdir, filename)
            write_ds_to_geotiff(netcdf, myfile_path)
            geotiff_files.append(myfile_path)
        netcdf = None

    # Loop over the subproducts extracted and do the merging.
    for sprod in subproducts:
        if sprod != 0:
            id_subproduct = sprod['re_extract']
            id_mapset = sprod['mapsetcode']
            nodata_value = sprod['nodata']
            out_tmp_file_gtiff = tmpdir + os.path.sep + id_subproduct + '_' + id_mapset + '.tif.merged'

            # Take gdal_merge.py from es2globals
            command = es_constants.gdal_merge + ' -init '+ str(nodata_value)+' -co \"compress=lzw\" -of GTiff -ot Float32 -o '
            command += out_tmp_file_gtiff
            for file_add in geotiff_files:
                command += ' '
                command += file_add
            my_logger.info('Command for merging is: ' + command)
            os.system(command)
            pre_processed_list.append(out_tmp_file_gtiff)

    return pre_processed_list


def pre_process_netcdf(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process NETCDF files (e.g. MODIS Global since July 2015)
#
# It receives in input the netcdf file (1 ONLY)
# It does the extraction of relevant datasets
#
# Note: modified on 19.4.16 to return a list of files (one foreach subproduct-mapset)
# Note: modified on 26.7.16 to save in tmp_dir the scale factor and offset, to be re-used in ingestion
#       This is related to the change in MODIS-Global Daily SST of the scale factor

    # Prepare the output file list
    pre_processed_list = []

    if isinstance(input_files, list):
        if len(input_files) > 1:
            raise Exception('More than 1 file passed: %i ' % len(input_files))
    input_file = input_files[0]
    # Build a list of subdatasets to be extracted
    list_to_extr = []
    geotiff_files = []
    previous_id_subdataset = ''

    for sprod in subproducts:
        if sprod != 0:
            subprod_to_extr = sprod['re_extract']

            # Test the. nc file and read list of datasets
            netcdf = gdal.Open(input_file)
            sdslist = netcdf.GetSubDatasets()

            if len(sdslist) >= 1:
                # Loop over datasets and extract the one from each unzipped
                for subdataset in sdslist:
                    netcdf_subdataset = subdataset[0]
                    id_subdataset = netcdf_subdataset.split(':')[-1]

                    if id_subdataset == subprod_to_extr:
                        if id_subdataset == previous_id_subdataset:
                            # Just append the last filename once again
                            geotiff_files.append(myfile_path)
                        else:
                            selected_sds = 'NETCDF:' + input_file + ':' + id_subdataset
                            sds_tmp = gdal.Open(selected_sds)
                            filename = os.path.basename(input_file) + '.geotiff'
                            myfile_path = os.path.join(tmpdir, filename)
                            write_ds_to_geotiff(sds_tmp, myfile_path)
                            sds_tmp = None
                            geotiff_files.append(myfile_path)
                            previous_id_subdataset = id_subdataset
                            # MC 26.07.2016: read/store scaling
                            try:
                                status = functions.save_netcdf_scaling(selected_sds, myfile_path)
                            except:
                                logger.debug('Error in reading scaling')
            else:
                if id_subdataset == previous_id_subdataset:
                    # Just append the last filename once again
                    geotiff_files.append(myfile_path)
                else:
                    # No subdatasets: e.g. SST -> read directly the .nc
                    filename = os.path.basename(input_file) + '.geotiff'
                    myfile_path = os.path.join(tmpdir, filename)
                    write_ds_to_geotiff(netcdf, myfile_path)
                    geotiff_files.append(myfile_path)
                    previous_id_subdataset = id_subdataset
                    # MC 26.07.2016: read/store scaling
                    # try:
                    #     status = functions.save_netcdf_scaling(sds_tmp, myfile_path)
                    # except:
                    #     logger.warning('Error in reading scaling')

            netcdf = None

    return geotiff_files


def pre_process_unzip(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process ZIPPED files
#
    out_tmp_gtiff_file = []
    #  zipped files containing one or more HDF4
    if isinstance(input_files, list):
        if len(input_files) > 1:
            logger.error('Only 1 file expected. Exit')
            raise Exception("Only 1 file expected. Exit")
        else:
            input_file = input_files[0]

    logger.debug('Unzipping/processing: .zip case')
    if zipfile.is_zipfile(input_file):
        zip_file = zipfile.ZipFile(input_file)              # Create ZipFile object
        zip_list = zip_file.namelist()                      # Get the list of its contents
        # Loop over subproducts and extract associated files
        for sprod in subproducts:

            # Define the re_expr for extracting files
            re_extract = '.*' + sprod['re_extract'] + '.*'
            my_logger.debug('Re_expression: ' + re_extract + ' to match sprod ' + sprod['subproduct'])

            for files in zip_list:
                my_logger.debug('File in the .zip archive is: ' + files)
                if re.match(re_extract, files):        # Check it matches one of sprods -> extract from zip
                    filename = os.path.basename(files)
                    data = zip_file.read(files)
                    myfile_path = os.path.join(tmpdir, filename)
                    myfile = open(myfile_path, "wb")
                    myfile.write(data)
                    myfile.close()
                    # Check if the file has to be processed, and add to intermediate list
                    re_process = '.*' + sprod['re_process'] + '.*'
                    if re.match(re_process, files):
                        out_tmp_gtiff_file.append(myfile_path)
        zip_file.close()

    else:
        my_logger.error("File %s is not a valid zipfile. Exit", input_files)
        raise Exception("File %s is not a valid zipfile. Exit", input_files)


        # TODO-M.C.:Check all datasets have been found (len(intermFile) ==len(subprods)))

    return out_tmp_gtiff_file


def pre_process_tarzip(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process .tgz files (e.g. WD-GEE)
#
    out_tmp_gtiff_file = []
    #  should be a single file
    if isinstance(input_files, list):
        if len(input_files) > 1:
            logger.error('Only 1 file expected. Exit')
            raise Exception("Only 1 file expected. Exit")
        else:
            input_file = input_files[0]

    logger.debug('Extracting from .tgz: .tarzip case')
    if tarfile.is_tarfile(input_file):
        tar_file = tarfile.open(input_file,'r:*')           # Open the .tgz
        tar_file.extractall(path=tmpdir)
        out_tmp_gtiff_file=glob.glob(tmpdir+os.path.sep+'*.tif')

        tar_file.close()

    else:
        my_logger.error("File %s is not a valid .tgz. Exit", input_files)
        raise Exception("File %s is not a valid .tgz. Exit", input_files)

        # TODO-M.C.:Check all datasets have been found (len(intermFile) ==len(subprods)))

    return out_tmp_gtiff_file


def pre_process_tarzip_wd_gee(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process .tgz files (e.g. WD-GEE)
#
    out_tmp_gtiff_file = []
    #  should be a single file
    # if isinstance(input_files, list):
    #     if len(input_files) > 1:
    #         logger.error('Only 1 file expected. Exit')
    #         raise Exception("Only 1 file expected. Exit")
    #     else:
    #         input_file = input_files[0]
    # complicated_case = False
    # if len(input_files)!=len(subproducts):
    #     complicated_case = True

    for sprod in subproducts:
        if sprod != 0:
            mapset_code = sprod['mapsetcode']

        fake_file_needed = True   # False only if the product exists and untared
        for index, input_file in enumerate(input_files):
            file = os.path.basename(input_file)
            input_file_mapset = file.split('_')[5]

            if str(mapset_code) == str(input_file_mapset):
                logger.debug('Extracting from .tgz: .tarzip case')
                if tarfile.is_tarfile(input_file):
                    tar_file = tarfile.open(input_file,'r:*')           # Open the .tgz
                    tar_file.extractall(path=tmpdir)
                    append_file_list = glob.glob(tmpdir+os.path.sep+'*'+input_file_mapset+'*.tif')
                    if len(append_file_list) > 0:
                        append_file = glob.glob(tmpdir + os.path.sep + '*' + input_file_mapset + '*.tif')[0]
                    out_tmp_gtiff_file.append(append_file)
                    tar_file.close()
                    fake_file_needed = False
                else:
                    my_logger.error("File %s is not a valid .tgz. Exit", input_files)
                    raise Exception("File %s is not a valid .tgz. Exit", input_files)
            # elif index == 2:
            #     # append empty file to out_tmp_gtiff_file
            #     out_tmp_gtiff_file.append('/dumpy')

        if fake_file_needed:
            out_tmp_gtiff_file.append('/fake_link/')
                # TODO-M.C.:Check all datasets have been found (len(intermFile) ==len(subprods)))

    return out_tmp_gtiff_file

def pre_process_bzip2 (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process bzip2 files
#
    interm_files_list = []

    # Make sure it is a list (if only a string is returned, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    for input_file in list_input_files:
        my_logger.info('Unzipping/processing: .bz2 case')
        bz2file = bz2.BZ2File(input_file)               # Create ZipFile object
        data = bz2file.read()                            # Get the list of its contents
        filename = os.path.basename(input_file)
        filename = filename.replace('.bz2', '')
        myfile_path = os.path.join(tmpdir, filename)
        myfile = open(myfile_path, "wb")
        myfile.write(data)
        myfile.close()
        bz2file.close()

    # Create a coherent intermediate file list
    for subproduct in subproducts:
        interm_files_list.append(myfile_path)

    return interm_files_list


def pre_process_gzip (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process gzip files
#
    interm_files_list = []

    # Make sure it is a list (if only a string is returned, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files=[]
        list_input_files.append(input_files)

    for input_file in list_input_files:
        my_logger.info('Unzipping/processing: .gzip case')
        gzipfile = gzip.open(input_file)                 # Create ZipFile object
        data = gzipfile.read()                           # Get the list of its contents
        filename = os.path.basename(input_file)
        filename = filename.replace('.gz', '')
        myfile_path = os.path.join(tmpdir, filename)
        myfile = open(myfile_path, "wb")
        myfile.write(data)
        myfile.close()
        gzipfile.close()

    # Create a coherent intermediate file list
    for subproduct in subproducts:
        interm_files_list.append(myfile_path)

    return interm_files_list


def pre_process_bz2_hdf4(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF4 files bz2 zipped
#   First unzips, then extract relevant subdatasets

    # prepare the output as an empty list
    interm_files_list = []

    # Build a list of subdatasets to be extracted
    list_to_extr = []
    for sprod in subproducts:
        if sprod != 0:
            list_to_extr.append(sprod['re_extract'])

    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    # Bz2 unzips to my_bunzip2_file
    # TODO-M.C.: re-use the method above ??
    for input_file in list_input_files:
        bz2file = bz2.BZ2File(input_file)               # Create ZipFile object
        data = bz2file.read()                           # Get the list of its contents
        filename = os.path.basename(input_file)
        filename = filename.replace('.bz2', '')
        my_bunzip2_file = os.path.join(tmpdir, filename)
        myfile = open(my_bunzip2_file, "wb")
        myfile.write(data)
        myfile.close()
        bz2file.close()

        # Test the hdf file and read list of datasets
        hdf = gdal.Open(my_bunzip2_file)
        sdsdict = hdf.GetMetadata('SUBDATASETS')
        sdslist = [sdsdict[k] for k in list(sdsdict.keys()) if '_NAME' in k]

        # Loop over datasets and extract the one in the list
        if len(sdslist) >= 1:
            for output_to_extr in list_to_extr:
                for subdataset in sdslist:
                    id_subdataset = subdataset.split(':')[-1]
                    if id_subdataset==output_to_extr:
                        outputfile = tmpdir + os.path.sep + filename + "_" + id_subdataset + '_' + '.tif'
                        sds_tmp = gdal.Open(subdataset)
                        write_ds_to_geotiff(sds_tmp, outputfile)
                        sds_tmp = None
                        interm_files_list.append(outputfile)
        else:
            # Manage case of 1 SDS only
            filename_gtif = os.path.basename(input_file) + '.geotiff'
            myfile_path = os.path.join(tmpdir, filename_gtif)
            write_ds_to_geotiff(hdf, myfile_path)
            interm_files_list.append(myfile_path)

    return interm_files_list


def pre_process_georef_netcdf(subproducts, native_mapset_code, tmpdir, input_files):
# -------------------------------------------------------------------------------------------------------
#   Convert netcdf to GTIFF (and assign geo-referencing)
#   This is treated as a special case, being not possible to 'update' geo-ref info in the netcdf

    # prepare the output as an empty list
    interm_files_list = []

    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    # Create native mapset object
    native_mapset = mapset.MapSet()
    native_mapset.assigndb(native_mapset_code)

    # Convert netcdf to GTIFF
    for subproduct in subproducts:
        for input_file in list_input_files:
            outputfile = tmpdir + os.path.sep + os.path.basename(input_file) + '_' + '.tif'
            dataset = gdal.Open(input_file)
            write_ds_and_mapset_to_geotiff(dataset, native_mapset, outputfile)
            interm_files_list.append(outputfile)

    return interm_files_list


def pre_process_hdf5_zip(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF5 zipped files (e.g. g2_biopar products)
#   Only one zipped file is expected, containing more files (.h5, .xls, .txt, .xml, ..)
#   Only the .h5 is normally extracted. Then, the relevant SDSs extracted and converted to geotiff.
#

    # prepare the output as an empty list
    interm_files_list = []

    # Build a list of subdatasets to be extracted
    sds_to_process = []
    for sprod in subproducts:
       # if sprod != 0:
            sds_to_process.append(sprod['re_process'])

    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    # Unzips the file
    for input_file in list_input_files:

        if zipfile.is_zipfile(input_file):
            zip_file = zipfile.ZipFile(input_file)              # Create ZipFile object
            zip_list = zip_file.namelist()                      # Get the list of its contents

            # Loop over subproducts and extract associated files
            for sprod in subproducts:

                # Define the re_expr for extracting files
                re_extract = '.*' + sprod['re_extract'] + '.*'
                my_logger.debug('Re_expression: ' + re_extract + ' to match sprod ' + sprod['subproduct'])

                for files in zip_list:
                    my_logger.debug('File in the .zip archive is: ' + files)
                    if re.match(re_extract, files):        # Check it matches one of sprods -> extract from zip
                        filename = os.path.basename(files)
                        data = zip_file.read(files)
                        myfile_path = os.path.join(tmpdir, filename)
                        myfile = open(myfile_path, "wb")
                        myfile.write(data)
                        myfile.close()
                        my_unzip_file = myfile_path

            zip_file.close()

        else:
            my_logger.error("File %s is not a valid zipfile. Exit", input_files)
            return 1

        # Test the hdf file and read list of datasets
        hdf = gdal.Open(my_unzip_file)
        sdsdict = hdf.GetMetadata('SUBDATASETS')

        # Manage the case of only 1 dataset (and no METADATA defined - e.g. PROBA-V NDVI v 2.x)
        if (len(sdsdict) > 0):
            sdslist = [sdsdict[k] for k in list(sdsdict.keys()) if '_NAME' in k]
            # Loop over datasets and extract the one in the list
            for output_sds in sds_to_process:
                for subdataset in sdslist:
                    id_subdataset = subdataset.split(':')[-1]
                    id_subdataset = id_subdataset.replace('/', '')
                    if id_subdataset == output_sds:
                        outputfile = tmpdir + os.path.sep + filename + "_" + id_subdataset + '.tif'
                        sds_tmp = gdal.Open(subdataset)
                        write_ds_to_geotiff(sds_tmp, outputfile)
                        sds_tmp = None

                        interm_files_list.append(outputfile)
        else:
            outputfile = tmpdir + os.path.sep + filename + '.tif'
            write_ds_to_geotiff(hdf, outputfile)
            sds_tmp = None
            interm_files_list.append(outputfile)

    return interm_files_list


def pre_process_hdf5_gls(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF5 zipped files (specifically for g_cls files from VITO)
#   Only one zipped file is expected, containing more files (.nc, .xls, .txt, .xml, ..)
#   Only the .nc is normally extracted. Then, the relevant SDSs extracted and converted to geotiff.
#

    # prepare the output as an empty list
    interm_files_list = []

    # Build a list of subdatasets to be extracted
    sds_to_process = []
    for sprod in subproducts:
       # if sprod != 0:
            sds_to_process.append(sprod['re_process'])

    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    # Unzips the file
    for input_file in list_input_files:

        if zipfile.is_zipfile(input_file):
            zip_file = zipfile.ZipFile(input_file)              # Create ZipFile object
            zip_list = zip_file.namelist()                      # Get the list of its contents

            # Loop over subproducts and extract associated files
            for sprod in subproducts:

                # Define the re_expr for extracting files
                re_extract = '.*' + sprod['re_extract'] + '.*'
                my_logger.debug('Re_expression: ' + re_extract + ' to match sprod ' + sprod['subproduct'])

                for files in zip_list:
                    my_logger.debug('File in the .zip archive is: ' + files)
                    if re.match(re_extract, files):        # Check it matches one of sprods -> extract from zip
                        filename = os.path.basename(files)
                        data = zip_file.read(files)
                        myfile_path = os.path.join(tmpdir, filename)
                        myfile = open(myfile_path, "wb")
                        myfile.write(data)
                        myfile.close()
                        my_unzip_file = myfile_path

            zip_file.close()

        else:
            my_logger.error("File %s is not a valid zipfile. Exit", input_files)
            return 1


        # Loop over datasets and extract the one in the list
        for output_sds in sds_to_process:
            # Open directly the SDS with the HDF interface (the NETCDF one goes in segfault)
            my_sds_hdf='NETCDF:'+my_unzip_file+'://'+output_sds
            sds_in = gdal.Open(my_sds_hdf)

            outputfile = tmpdir + os.path.sep + filename + '.tif'
            write_ds_to_geotiff(sds_in, outputfile)
            sds_in = None
            interm_files_list.append(outputfile)

    return interm_files_list


def pre_process_hdf5_gls_nc(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF5 non-zipped files (specifically for g_cls files from VITO)
#   It is the 'simplified' version of the pre_process_hdf5_gls method above, for the 'Global' files
#

    # prepare the output as an empty list
    interm_files_list = []

    # Build a list of subdatasets to be extracted
    sds_to_process = []
    for sprod in subproducts:
       # if sprod != 0:
            sds_to_process.append(sprod['re_process'])

    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    # Unzips the file
    for input_file in list_input_files:

        # Loop over datasets and extract the one in the list
        for output_sds in sds_to_process:
            # Open directly the SDS with the HDF interface (the NETCDF one goes in segfault)
            my_sds_hdf='NETCDF:'+input_file+'://'+output_sds
            sds_in = gdal.Open(my_sds_hdf)
            outputfile = tmpdir + os.path.sep + os.path.basename(input_file) + '.tif'
            write_ds_to_geotiff(sds_in, outputfile)
            sds_in = None
            interm_files_list.append(outputfile)

    return interm_files_list


def pre_process_nasa_firms(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Global_MCD14DL product retrieved from ftp://nrt1.modaps.eosdis.nasa.gov/FIRMS/Global
#   The columns are already there, namely: latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,
#                                          confidence,version,bright_t31,frp
#   NOTE: being the 'rasterization' a two-step process (here, w/o knowing the target-mapset, and in ingest-file)
#         during the tests a 'shift has been seen (due to the re-projection in ingest_file). We therefore ensure here
#         the global raster to be 'aligned' with the WGS84_Africa_1km (i.e. the SPOT-VGT grid)
#

    # prepare the output as an empty list
    interm_files_list = []
    # Definitions

    file_mcd14dl = input_files[0]
    logger.debug('Pre-processing file: %s' % file_mcd14dl)
    pix_size = '0.008928571428571'
    file_vrt = tmpdir+os.path.sep+"firms_file.vrt"
    file_csv = tmpdir+os.path.sep+"firms_file.csv"
    file_tif = tmpdir+os.path.sep+"firms_file.tif"
    out_layer= "firms_file"
    file_shp = tmpdir+os.path.sep+out_layer+".shp"

    # Write the 'vrt' file
    with open(file_vrt,'w') as outFile:
        outFile.write('<OGRVRTDataSource>\n')
        outFile.write('    <OGRVRTLayer name="firms_file">\n')
        outFile.write('        <SrcDataSource>'+file_csv+'</SrcDataSource>\n')
        outFile.write('        <OGRVRTLayer name="firms_file" />\n')
        outFile.write('        <GeometryType>wkbPoint</GeometryType>\n')
        outFile.write('        <LayerSRS>WGS84</LayerSRS>\n')
        outFile.write('        <GeometryField encoding="PointFromColumns" x="longitude" y="latitude" />\n')
        outFile.write('    </OGRVRTLayer>\n')
        outFile.write('</OGRVRTDataSource>\n')

    # Generate the csv file with header
    with open(file_csv,'w') as outFile:
        #outFile.write('latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp')
        with open(file_mcd14dl, 'r') as input_file:
            outFile.write(input_file.read())

    # Execute the ogr2ogr command
    command = 'ogr2ogr -f "ESRI Shapefile" ' + file_shp + ' '+file_vrt
    my_logger.debug('Command is: '+command)
    try:
        os.system(command)
    except:
        my_logger.error('Error in executing ogr2ogr')
        return 1

    # Convert from shapefile to rasterfile
    command = 'gdal_rasterize  -l ' + out_layer + ' -burn 1 '\
            + ' -tr ' + str(pix_size) + ' ' + str(pix_size) \
            + ' -co "compress=LZW" -of GTiff -ot Byte '     \
            + ' -te -179.995535714286 -89.995535714286 179.995535714286 89.995535714286 ' \
            +file_shp+' '+file_tif

    my_logger.debug('Command is: '+command)
    try:
        os.system(command)
    except:
        my_logger.error('Error in executing ogr2ogr')
        return 1

    interm_files_list.append(file_tif)

    return interm_files_list


def pre_process_wdb_gee(subproducts, native_mapset_code, tmpdir, input_files, my_logger):
# --------------------------PROCESS IS DONE ONLY IN DEVELOPEMENT MACHINE CANT BE USED IN MESA-PROC-------------------
#   Merges the various tiles of the .tif files retrieved from GEE application and remove the bigtif tag.
#   Additionally, writes to the 'standard' mapset 'WD-GEE-ECOWAS-AVG', which MUST be indicated as
#   'native-mapset' for the datasource
#   Here below gdal options used for testing (they refer to ECOWAS-AVG mapset):
#
#   gdalwarp format:
#       -te -17.5290058 4.2682552 24.0006488 27.3132762
#       -tr 0.000269494585236 0.000269494585236

#   gdal_merge.py format:
#       -ps 0.000269494585236 0.000269494585236
#       -ul_lr -17.5290058 27.3132762 24.0006488 4.2682552
    region = 'IGAD'

    # Get date from file name
    input_file_name  = os.path.basename(input_files[0])
    # date = '20181201'
    sprod = subproducts[0]
    sprod_code = str(sprod.get('subproduct'))

    if sprod_code == 'avg':
        #typical file name is JRC-WBD-AVG-CA_1985-2015_0601-0000000000-0000000000.tif
        date = input_file_name.split('_')[2]    #0601-0000000000-0000000000.tif
        date = date.split('-')[0]
        region_code = input_file_name.split('_')[0]
        region_code = region_code.split('-')[3]
    else:
        #JRC-WBD_NA_20190101-0000000000-0000000000.tif
        date = input_file_name.split('_')[2]  # 0601-0000000000-0000000000.tif
        date = date.split('-')[0]
        region_code = input_file_name.split('_')[1]
        # region_code = region_code.split('-')[3]

    if region_code == 'ICPAC':
        region='IGAD'
        # ullr_xy=' -17.5290058 27.3132762 24.0006488 4.2682552 '      # ECOWAS
        ullr_xy=' 21.8145086965016 23.1455424529815 51.4155244442228 -11.7612826888632 '      # IGAD
        # output_tar = '/data/ingest/MESA_JRC_wd-gee_avg_' + date + '_WD-GEE-' + region + '-AVG_1.0.tgz'  # for avg
        # output_tar='/data/ingest/MESA_JRC_wd-gee_occurr_'+date+'_WD-GEE-'+region+'-AVG_1.0.tgz'    # for occurr
        file_naming = 'MESA_JRC_wd-gee_' + sprod_code + '_' + date + '_WD-GEE-' + region + '-AVG_1.0'
        # output_tar = '/data/ingest/'+file_naming+'.tgz'

    elif region_code == 'NA':
        region = 'NORTHAFRICA'
        ullr_xy = ' -17.1042823357493 14.7154823322187 36.2489081763193 37.5610773118327 '
        file_naming = 'MESA_JRC_wd-gee_' + sprod_code + '_' + date + '_WD-GEE-' + region + '-AVG_1.0'
        # output_tar = '/data/ingest/'+file_naming+'.tgz'

    elif region_code == 'SA':
        region = 'SOUTHAFRICA'
        ullr_xy = ' 11.67019352	-46.98153003 40.83947894 -4.388180331 '
        file_naming = 'MESA_JRC_wd-gee_' + sprod_code + '_' + date + '_WD-GEE-' + region + '-AVG_1.0'

    elif region_code == 'CA':
        region = 'CENTRALAFRICA'
        ullr_xy = ' 5.6170756400709561 -13.4558646408263130 31.3120368693836895 23.4395610454738517 '
        file_naming = 'MESA_JRC_wd-gee_' + sprod_code + '_' + date + '_WD-GEE-' + region + '-AVG_1.0'

    elif region_code == 'WA':
        region = 'WESTAFRICA'
        ullr_xy = ' -25.3589014815236 4.26852473555073 15.9958511066742 25.0002041885746 '
        file_naming = 'MESA_JRC_wd-gee_' + sprod_code + '_' + date + '_WD-GEE-' + region + '-AVG_1.0'

    else :
        region = 'ECOWAS'
        ullr_xy = ' -17.5290058 27.3132762 24.0006488 4.2682552 '  # ECOWAS
        # ullr_xy = ' 21.8145086965016 23.1455424529815 51.4155244442228 -11.7612826888632 '  # IGAD
        # output_tar = '/data/ingest/MESA_JRC_wd-gee_occurr_' + date + '_WD-GEE-' + region + '-AVG_1.0.tgz'  # for occurr
        # output_tar = '/data/ingest/MESA_JRC_wd-gee_avg_' + date + '_WD-GEE-' + region + '-AVG_1.0.tgz'  # for avg
        file_naming = 'MESA_JRC_wd-gee_' + sprod_code + '_' + date + '_WD-GEE-' + region + '-AVG_1.0'
        # output_tar = '/data/ingest/'+file_naming+'.tgz'


    output_tar = '/data/ingest/'+file_naming+'.tgz'
    # Prepare the output as an empty list
    interm_files_list = []

    # Get the ID of the files associated to such subproduct
    for sprod in subproducts:
        match_regex = '*'+sprod['re_extract']+'*'

    # Make sure it is a list (if only a string is returned, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files=[]
        list_input_files.append(input_files)

    # Check if they match the regex
    good_input_files = []
    for file in list_input_files:
        if fnmatch.fnmatch(os.path.basename(file), match_regex):
            good_input_files.append(file)

    if len(good_input_files) == 0:
        return []
    # Does check the number of files ?
    output_file = tmpdir + os.path.sep + 'merge_output.tif'
    output_file_vrt = tmpdir + os.path.sep + 'merge_output_rescaled.vrt'
    # output_file_mapset  = tmpdir+os.path.sep + 'merge_output_WD-GEE-'+region+'-AVG.tif'
    output_file_mapset = tmpdir + os.path.sep + file_naming + '.tif'


    # -------------------------------------------------------------------------
    # STEP 1: Merge all input products into a 'tmp' file
    # -------------------------------------------------------------------------
    try:
        command = es_constants.gdal_merge
        command += ' -co \"compress=lzw\"'
        command += ' -ps 0.000269494585236 0.000269494585236 '
        # command += ' -ul_lr '+ ullr_xy      # If not specified it take the input file extent which is fine for us?
        command += ' -o ' + output_file
        command += ' -ot BYTE '
        for file in good_input_files:
            command += ' ' + file

        my_logger.debug('Command for merging is: ' + command)
        os.system(command)
    except:
        pass

    # # Rescale the data using gdal_calc (need only if the value of the data is binary)
    # rescale_func = "\"A * 100\""
    # rescale_command = "gdal_calc.py -A "+ output_file +" --co \"compress=lzw\" --type=Int16 --outfile="+output_file_vrt+" --calc="+rescale_func
    # os.system(rescale_command)
    # # M.C. 30.10.17 (see ES2-96)
    # # Do gdal_translate, in order to better compress the file

    try:
        command = es_constants.gdal_translate
        command += ' -co \"compress=lzw\"'
        command += ' -co \"BIGTIFF=No\"'
        command += ' -ot BYTE '
        command += ' '+output_file
        # command += ' ' + output_file_vrt #To be changed if rescaling is done
        command += ' '+output_file_mapset

        my_logger.debug('Command for re-project is: ' + command)
        os.system(command)
        interm_files_list.append(output_file_mapset)

    except:
        pass

    #Manually save tar file in the /data/ingest and send it to mesa-proc for the processing
    command = 'tar -cvzf '+output_tar+' -C ' + os.path.dirname(output_file_mapset) + ' ' + os.path.basename(output_file_mapset)
    # command = 'tar -cvzf /data/ingest/MESA_JRC_wd-gee_occurr_20190801_WD-GEE-ECOWAS-AVG_1.0.tgz -C ' + os.path.dirname(output_file_mapset) + ' ' + os.path.basename(output_file_mapset)
    my_logger.debug('Command for tar the file is: ' + command)
    os.system(command)
    # Assign output file
    # interm_files_list.append(output_file_mapset)

    return []


def pre_process_ecmwf_mars(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process SPIRITS ECMWF files
#

    #  Zipped files containing an .img and and .hdr file
    if isinstance(input_files, list):
        if len(input_files) > 1:
            logger.error('Only 1 file expected. Exit')
            raise Exception("Only 1 file expected. Exit")
        else:
            input_file = input_files[0]

    logger.debug('Unzipping/processing: ecmwf case')

    #  Extract .img and and .hdr file, and store .img name
    img_ext='.*.img'
    if zipfile.is_zipfile(input_file):
        zip_file = zipfile.ZipFile(input_file)              # Create ZipFile object
        zip_list = zip_file.namelist()                      # Get the list of its contents
        for files in zip_list:
            my_logger.debug('File in the .zip archive is: ' + files)
            filename = os.path.basename(files)
            data = zip_file.read(files)
            myfile_path = os.path.join(tmpdir, filename)
            myfile = open(myfile_path, "wb")
            myfile.write(data)
            myfile.close()
            if re.match(img_ext, filename):
               out_tmp_img_file = myfile_path
        zip_file.close()

    else:
        my_logger.error("File %s is not a valid zipfile. Exit", input_files)
        raise Exception("File %s is not a valid zipfile. Exit", input_files)

    #  Convert from .img to GTIFF
    if os.path.isfile(out_tmp_img_file):
        output_file = out_tmp_img_file.replace('.img','.tif')
        orig_ds = gdal.Open(out_tmp_img_file)
        write_ds_to_geotiff(orig_ds,output_file)
        orig_ds = None
    else:
        my_logger.error("No .img file found in zipfile. Exit")
        raise Exception("No .img file found in zipfile. Exit")

    return output_file


def pre_process_envi_to_geotiff(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process ENVI files
#
    #  input_files containing an .img and and .hdr file
    if isinstance(input_files, list):
        if len(input_files) != 2:
            return None
            # logger.error('2 files expected. Exit')
            # raise Exception("2 files expected. Exit")
        else:
            if input_files[0].endswith('.img'):
                input_file_img = input_files[0]
                input_file_hdr = input_files[1]
            else:
                input_file_img = input_files[1]
                input_file_hdr = input_files[0]

    #  Extract .img and and .hdr file, and store .img name
    my_logger.debug('File in the .img format is: ' + input_file_img)

    filename_img = os.path.basename(input_file_img)
    # filename_hdr = filename_img.split('.')[0]+'.hdr'
    filename_hdr = os.path.basename(input_file_hdr)
    filename_tif = filename_img.split('.')[0]+'.tif'
    # input_file_hdr = os.path.join(os.path.dirname(input_file_img), filename_hdr)

    if not os.path.isfile(input_file_hdr):
        return None

    tmp_img_file_path = os.path.join(tmpdir, filename_img)
    tmp_hdr_file_path = os.path.join(tmpdir, filename_hdr)
    shutil.copy(input_file_img, tmp_img_file_path)
    shutil.copy(input_file_hdr, tmp_hdr_file_path)

    #  Convert from .img to GTIFF
    if os.path.isfile(tmp_img_file_path):
        output_file = os.path.join(tmpdir, filename_tif)
        orig_ds = gdal.Open(tmp_img_file_path)
        write_ds_to_geotiff(orig_ds,output_file)
        orig_ds = None
    else:
        my_logger.error("No .img file found in zipfile. Exit")
        raise Exception("No .img file found in zipfile. Exit")

    return output_file

# -------------------------------------------------------------------------------------------------------
#   Pre-process CPC files TYPE (binary, 720 x 360, global at 0.5 degree resolution)
#   See: http://www.cpc.ncep.noaa.gov/soilmst/leaky_glb.htm
def pre_process_cpc_binary(subproducts, tmpdir , input_files, my_logger):

    logger.debug('Unzipping/processing: CPC_BINARY case')

    n_lines = 360
    n_cols = 720
    if isinstance(input_files, list):
        if len(input_files) > 1:
            logger.error('Only 1 file expected. Exit')
            raise Exception("Only 1 file expected. Exit")
        else:
            input_file = input_files[0]
    else:
        input_file = input_files

    if os.path.isfile(input_file):

        # Open and read the file as float32

        fid = open(input_file,"r")
        data = N.fromfile(fid,dtype=N.float32)

        # Byte swap (big -> little endian) + flip UD
        data2 = data.byteswap().reshape(n_lines,n_cols)
        data = N.flipud(data2)
        data_180=N.concatenate((data[...,360:720],data[...,0:360]),axis=1)

        # Re-arrange from -180 to 180 longitude

        # Write output
        output_file = os.path.join(tmpdir, os.path.basename(input_file))
        output_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)
        output_ds = output_driver.Create(output_file, n_cols, n_lines, 1, gdal.GDT_Float32)
        output_ds.GetRasterBand(1).WriteArray(data_180)
        output_ds = None
        fid.close()

    return output_file


def pre_process_gsod(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the GSOD yearly files (from ftp://ftp.ncdc.noaa.gov/pub/data/gsod/)
#   The file contains measurements from a single gauge station, with all available dates for the year
#   Typical file name is like 998499-99999-2016.op.gz, and contains columns:
#   STN--- WBAN   YEARMODA    TEMP       DEWP      SLP        STP       VISIB      WDSP     MXSPD   GUST    MAX     MIN   PRCP   SNDP   FRSHTT
#   998499 99999  20160101    25.2 24  9999.9  0  9999.9  0  9999.9  0  999.9  0   10.2 24   15.9  999.9    30.0    20.1*  0.00I 999.9  000000
#
#   The precipitation value is in inches and hundredths, followed by a flag, as below:
#
#      A = 1 report of 6-hour precipitation amount.
#      B = Summation of 2 reports of 6-hour precipitation amount.
#      C = Summation of 3 reports of 6-hour precipitation amount.
#      D = Summation of 4 reports of 6-hour precipitation amount.
#      E = 1 report of 12-hour precipitation amount.
#      F = Summation of 2 reports of 12-hour precipitation amount.
#      G = 1 report of 24-hour precipitation amount.
#      H = Station reported '0' as the amount for the day (eg, from 6-hour reports),
#          but also reported at least one occurrence of precipitation in hourly
#          observations--this could indicate a trace occurred, but should be considered
#          as incomplete data for the day.
#      I = Station did not report any precip data for the day and did not report any
#          occurrences of precipitation in its hourly observations--it's still possible that
#          precip occurred but was not reported.
#

    # Definitions: use 1km pixel size and global coverage
    pixel_size = '0.008928571428571'
    te_global = ' -179.995535714286 -89.995535714286 179.995535714286 89.995535714286 '
    interm_files_list = []

    # Arrange to create the .shp file as well
    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep
    ext=es_constants.ES2_OUTFILE_EXTENSION

    shp_prod_ident_noext = functions.set_path_filename_no_date('gsod-rain', \
                                                         subproducts[0]['subproduct'],\
                                                         subproducts[0]['mapsetcode'],
                                                         '1.0', '')
    shp_prod_ident = shp_prod_ident_noext + '.shp'
    shp_output_dir = es2_data_dir+functions.set_path_sub_directory('gsod-rain',\
                                                                    subproducts[0]['subproduct'],
                                                                    'Ingest',
                                                                    '1.0',
                                                                     subproducts[0]['mapsetcode'])


    shp_output_file = shp_output_dir+os.path.sep+str(in_date)+shp_prod_ident

    logger.debug('First pre-processing file: %s' % input_files[0])
    # Local definitions
    f_stations = '/eStation2/static/sadc_regional_stations.csv'      # TEMP ?????? -> move to a variable/argument
    file_csv = tmpdir+os.path.sep+"gsod_file.csv"
    file_out = tmpdir+os.path.sep+"gsod_raster.tif"
    out_layer= "gsod_file"

    file_shp = tmpdir+os.path.sep+out_layer+".shp"

    # Write the 'vrt' file
    file_vrt = tmpdir+os.path.sep+"gsod_file.vrt"
    with open(file_vrt,'w') as outFile:
        outFile.write('<OGRVRTDataSource>\n')
        outFile.write('    <OGRVRTLayer name="gsod_file">\n')
        outFile.write('        <SrcDataSource>'+file_csv+'</SrcDataSource>\n')
        outFile.write('        <OGRVRTLayer name="gsod_file" />\n')
        outFile.write('        <GeometryType>wkbPoint</GeometryType>\n')
        outFile.write('        <LayerSRS>WGS84</LayerSRS>\n')
        outFile.write('        <GeometryField encoding="PointFromColumns" x="longitude" y="latitude" />\n')
        outFile.write('    </OGRVRTLayer>\n')
        outFile.write('</OGRVRTDataSource>\n')

    # Unzip all input files in tmpdir
    for infile in input_files:
        command='gunzip -c '+infile+' > '+tmpdir+os.path.sep+os.path.basename(infile)
        try:
            os.system(command)
        except:
            my_logger.error('Error in unzipping file: '+infile)
            pass

    # Define the dates to consider (format YYYYMMDD) -> Should consider existing dates !!
    list_dates = []
    list_dates.append(in_date)

    # Loop over dates
    for mydate in list_dates:

        # Create a .txt file for each date
        outfile=tmpdir+os.path.sep+str(mydate)+'.gsod.all.stations.txt'
        command='grep -h '+mydate+' '+tmpdir+os.path.sep+'*.op* >>'+outfile
        try:
            os.system(command)
        except:
            my_logger.error('Error in creating outfile: '+outfile)
            pass

        f_meas=outfile

        # Read co-ordinates of all stations
        stations_list=[]
        f = open(f_stations,'rt')
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            stations_list.append(row)
        f.close()

        # Create dictionary for translating station -> Lat/Lon
        dict_latlon = {'empty_key':'empty_value'}
        # File downloaded from GBOC
        # for station in stations_list:
        #     #USAF   WBAN  STATION NAME                  CTRY ST CALL  LAT     LON      ELEV(M) BEGIN    END
        #     station_id = station[0][0:6]
        #     if station[0][58:65].strip() != '':
        #         station_lat = float(station[0][58:65])
        #     else:
        #         pass
        #     if station[0][66:73].strip() != '':
        #         station_lon = float(station[0][66:73])
        #     else:
        #         pass
        #     dict_latlon[station_id]=str(station_lat)+','+str(station_lon)

        # File received from Thembani
        for station in stations_list:
            #USAF   WBAN  STATION NAME                  CTRY ST CALL  LAT     LON      ELEV(M) BEGIN    END
            station_id = station[0]
            try:
                station_lat = float(station[1])
            except:
                station_lat = None
            try:
                station_lon = float(station[2])
            except:
                station_lon = None

            if station_lat is not None and station_lon is not None:
                dict_latlon[station_id]=str(station_lat)+','+str(station_lon)

        # Read measures file, and convert to csv file
        f = open(f_meas,'rt')
        fout = open(file_csv,'w')
        fout.write('latitude,longitude,precipitation,flag \n')

        reader = csv.reader(f)
        for measure in reader:
            station_id = measure[0][0:6]
            precipitation = measure[0][118:123]
            flag = measure[0][123:124]
            if float(precipitation) != 99.99:
                try:
                    lat_lon = dict_latlon[station_id]
                    fout.write('%16s,%8s \n' % (lat_lon,precipitation))
                except:
                    pass
        f.close()
        fout.close()

    # Convert from csv to Shape (ogr2ogr command)
    command = 'ogr2ogr -f "ESRI Shapefile" ' + file_shp + ' '+file_vrt
    my_logger.debug('Command is: '+command)
    try:
        os.system(command)
    except:
        my_logger.error('Error in executing ogr2ogr')
        return 1

    # Copy .shp to output_dir
    extensions = []
    extensions.append('.dbf')
    extensions.append('.prj')
    extensions.append('.shp')
    extensions.append('.shx')

    for ext in  range(len(extensions)):
        extension = extensions[ext]
        print (tmpdir + os.path.sep + "gsod_file" + extension)
        print (shp_output_dir + os.path.sep + str(in_date) + shp_prod_ident_noext + extension)
        shutil.copyfile(tmpdir+os.path.sep+"gsod_file"+extension,\
                        shp_output_dir+os.path.sep+str(in_date)+shp_prod_ident_noext+extension)

    # Convert from shapefile to rasterfile
    command = 'gdal_rasterize  -l ' + out_layer + ' -a precipitat '\
            + ' -tr ' + str(pixel_size) + ' ' + str(pixel_size) \
            + ' -co "compress=LZW" -of GTiff -ot Float32 '     \
            + ' -te  ' + te_global \
            +file_shp+' '+file_out

    my_logger.debug('Command is: '+command)
    try:
        os.system(command)
    except:
        my_logger.error('Error in executing ogr2ogr')
        return 1

    interm_files_list.append(file_out)

    return interm_files_list


def pre_process_netcdf_s3_wrr(subproducts, tmpdir, input_files, my_logger, in_date=None, zipped=False):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Sentinel 3 Level 2 product from OLCI - WRR
#   Returns -1 if nothing has to be done on the passed files
#

    # Prepare the output file list
    pre_processed_list = []

    list_input_files = []

    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        temp_list_input_files = input_files
    else:
        temp_list_input_files = []
        temp_list_input_files.append(input_files)

    # Select only the 'day-time' files
    for one_file in temp_list_input_files:
        one_filename = os.path.basename(one_file)
        in_date = one_filename.split('_')[7]
        day_data = functions.is_data_captured_during_day(in_date)
        if day_data:
            list_input_files.append(one_file)

    # Check at least 1 day-time file is there
    if len(list_input_files) == 0:
        my_logger.debug('No any file captured during the day. Return')
        return -1

    # Unzips the file
    for input_file in list_input_files:

        if zipped:
            # Unzip the .tar file in 'tmpdir'
            command = 'unzip ' + input_file + ' -d ' + tmpdir + os.path.sep  # ' --strip-components 1'
            print (command)
            status = os.system(command)
            # TODO: Change the code to OS independent
            # from zipfile import ZipFile
            # with ZipFile('input_file','r') as zipObj:
            #     zipObj.extractall(tmpdir + os.path.sep)

        else:
            # Unzip the .tar file in 'tmpdir'
            command = 'tar -xvf ' + input_file + ' -C ' + tmpdir + os.path.sep  # ' --strip-components 1'
            print (command)
            status = os.system(command)
            # TODO: Change the code to OS independent
            # import tarfile
            # tar = tarfile.open(input_file)
            # tar.extractall(path=tmpdir + os.path.sep)  # untar file into same directory
            # tar.close()

    # Loop over subproducts and extract associated files. In case of more Mapsets, more sprods exist
    for sprod in subproducts:
        interm_files_list = []
        # In each unzipped folder pre-process the dataset and store the list of files to be merged
        for untar_file in os.listdir(tmpdir):

            # Define the re_expr for extracting files
            bandname = sprod['re_extract']
            re_process = sprod['re_process']
            no_data = sprod['nodata']
            subproductcode = sprod['subproduct']
            # TODO scale nodata value from GPT has to be computed based on the product
            scaled_no_data = "103.69266"
            # ------------------------------------------------------------------------------------------
            # Extract latitude and longitude as geotiff in tmp_dir
            # ------------------------------------------------------------------------------------------
            tmpdir_untar = tmpdir + os.path.sep + untar_file
            tmpdir_untar_band = tmpdir + os.path.sep + untar_file + os.path.sep + re_process

            if not os.path.exists(tmpdir_untar_band):
                # ES2-284 fix
                # path = os.path.join(tmpdir, untar_file)
                if os.path.isdir(tmpdir_untar):
                    os.makedirs(tmpdir_untar_band)
                else:
                    continue

            # ------------------------------------------------------------------------------------------
            # Write a graph xml and subset the product for specific band, also applying flags
            # ------------------------------------------------------------------------------------------
            #functions.write_graph_xml_subset(output_dir=tmpdir_untar, band_name=re_process)
            # if subproductcode == 'chl-oc4me-filtered':
            #     expression = '(WQSF_lsb_CLOUD or WQSF_lsb_CLOUD_AMBIGUOUS or WQSF_lsb_CLOUD_MARGIN or WQSF_lsb_INVALID or WQSF_lsb_COSMETIC or WQSF_lsb_SATURATED or WQSF_lsb_SUSPECT or WQSF_lsb_HISOLZEN or WQSF_lsb_HIGHGLINT or WQSF_lsb_SNOW_ICE or WQSF_msb_ANNOT_ABSO_D or WQSF_lsb_OC4ME_FAIL or WQSF_msb_ANNOT_MIXR1 or WQSF_msb_ANNOT_DROUT or WQSF_msb_ANNOT_TAU06 or WQSF_msb_RWNEG_O2 or WQSF_msb_RWNEG_O3 or WQSF_msb_RWNEG_O4 or WQSF_msb_RWNEG_O5 or WQSF_msb_RWNEG_O6 or WQSF_msb_RWNEG_O7 or WQSF_msb_RWNEG_O8 or WQSF_lsb_AC_FAIL or WQSF_lsb_WHITECAPS) ? NaN : CHL_OC4ME'
            # else:
            #     expression='(WQSF_lsb_CLOUD or WQSF_lsb_CLOUD_AMBIGUOUS or WQSF_lsb_CLOUD_MARGIN or WQSF_lsb_INVALID or WQSF_lsb_COSMETIC or WQSF_lsb_SATURATED or WQSF_lsb_SUSPECT or WQSF_lsb_HISOLZEN or WQSF_lsb_HIGHGLINT or WQSF_lsb_SNOW_ICE) ? NaN : CHL_OC4ME'
            expression = '(WQSF_lsb_CLOUD or WQSF_lsb_CLOUD_AMBIGUOUS or WQSF_lsb_CLOUD_MARGIN or WQSF_lsb_INVALID or WQSF_lsb_COSMETIC or WQSF_lsb_SATURATED or WQSF_lsb_SUSPECT or WQSF_lsb_HISOLZEN or WQSF_lsb_HIGHGLINT or WQSF_lsb_SNOW_ICE or WQSF_msb_ANNOT_ABSO_D or WQSF_lsb_OC4ME_FAIL or WQSF_msb_ANNOT_MIXR1 or WQSF_msb_ANNOT_DROUT or WQSF_msb_ANNOT_TAU06 or WQSF_msb_RWNEG_O2 or WQSF_msb_RWNEG_O3 or WQSF_msb_RWNEG_O4 or WQSF_msb_RWNEG_O5 or WQSF_msb_RWNEG_O6 or WQSF_msb_RWNEG_O7 or WQSF_msb_RWNEG_O8 or WQSF_lsb_AC_FAIL or WQSF_lsb_WHITECAPS) ? NaN : CHL_OC4ME'
            functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process, expression= expression)     #'l2p_flags_cloud ? NaN : sea_surface_temperature')
            #functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process)


            graph_xml_subset = tmpdir_untar_band + os.path.sep + 'graph_xml_subset.xml'
            output_subset_tif = tmpdir_untar_band + os.path.sep + 'band_subset.tif'

            command = es_constants.gpt_exec+' '+ graph_xml_subset
            status=os.system(command)
            # ToDo : check the status or use try/except
            if os.path.exists(output_subset_tif):
                functions.write_graph_xml_reproject(output_dir=tmpdir_untar_band, nodata_value=scaled_no_data)

                graph_xml_reproject = tmpdir_untar_band + os.path.sep + 'graph_xml_reproject.xml'
                output_reproject_tif = tmpdir_untar_band + os.path.sep + 'reprojected.tif'

                command_reproject = es_constants.gpt_exec+' '+ graph_xml_reproject
                # print (command_reproject)
                os.system(command_reproject)

                if os.path.exists(output_reproject_tif):
                    output_vrt = tmpdir_untar_band + os.path.sep + 'single_band_vrt.vrt'
                    command_translate = 'gdal_translate -b 1 -a_nodata '+scaled_no_data+' -of VRT '+output_reproject_tif+ ' '+output_vrt
                    os.system(command_translate)
                    interm_files_list.append(output_vrt)

        # Check at least 1 file is reprojected file is there
        if len(interm_files_list) == 0:
            my_logger.debug('No any file overlapping the ROI. Return')
            return -1

        if len(interm_files_list) > 1 :
            out_tmp_file_gtiff = tmpdir + os.path.sep + re_process+'_merged.tif'
            input_files_str = ''
            for file_add in interm_files_list:
                input_files_str += ' '
                input_files_str += file_add
            command = 'gdalwarp -srcnodata "{}" -dstnodata "{}" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(scaled_no_data, int(no_data),
                 input_files_str, out_tmp_file_gtiff)
            # command = 'gdalwarp -srcnodata "103.69266" -dstnodata "1000" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
            #     input_files_str, out_tmp_file_gtiff)
            my_logger.info('Command for merging is: ' + command)
            os.system(command)
            pre_processed_list.append(out_tmp_file_gtiff)
        else:
            pre_processed_list.append(interm_files_list[0])

    return pre_processed_list


def pre_process_snap_subset_nc(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the netcdf using snap - subset and merge the tiles
#   Returns -1 if nothing has to be done on the passed files
#

    # Prepare the output file list
    pre_processed_list = []

    list_input_files = []


    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        temp_list_input_files = input_files
    else:
        temp_list_input_files = []
        temp_list_input_files.append(input_files)

    # Select only the 'day-time' files
    # for one_file in temp_list_input_files:
    #     one_filename = os.path.basename(one_file)
    #     in_date = one_filename.split('_')[7]
    #     day_data = functions.is_data_captured_during_day(in_date)
    #     if day_data:
    #         list_input_files.append(one_file)

    # Check at least 1 day-time file is there
    if len(temp_list_input_files) == 0:
        my_logger.debug('No any file captured during the day. Return')
        return -1

    # for input_file in temp_list_input_files:
    #
    #     # Unzip the .tar file in 'tmpdir'
    #     command = 'cp ' + input_file + ' ' + tmpdir + os.path.sep # ' --strip-components 1'
    #     # print (command)
    #     status = os.system(command)
    #     # ToDo : check the status or use try/except

    # Loop over subproducts and extract associated files. In case of more Mapsets, more sprods exist
    for sprod in subproducts:
        interm_files_list = []
        # In each unzipped folder pre-process the dataset and store the list of files to be merged
        count =  1
        for input_file in temp_list_input_files:

            # Define the re_expr for extracting files
            bandname = sprod['re_extract']
            re_process = sprod['re_process']
            no_data = sprod['nodata']
            subproductcode = sprod['subproduct']
            # TODO scale nodata value from GPT has to be computed based on the product
            # ------------------------------------------------------------------------------------------
            # Extract latitude and longitude as geotiff in tmp_dir
            # ------------------------------------------------------------------------------------------
            # tmpdir_untar = tmpdir + os.path.sep + untar_file
            count = count + 1

            tmpdir_output = tmpdir + os.path.sep + bandname + str(count)
            os.makedirs(tmpdir_output)
            tmpdir_output_band = tmpdir_output + os.path.sep + bandname

            if not os.path.exists(tmpdir_output_band):
                # ES2-284 fix
                # path = os.path.join(tmpdir, untar_file)
                if os.path.isdir(tmpdir_output):
                    os.makedirs(tmpdir_output_band)
                else:
                    continue

            # ------------------------------------------------------------------------------------------
            # Write a graph xml and subset the product for specific band, also applying flags
            # ------------------------------------------------------------------------------------------
            functions.write_graph_xml_subset(input_file=input_file, output_dir=tmpdir_output, band_name=bandname)     #'l2p_flags_cloud ? NaN : sea_surface_temperature')
            #functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process)


            graph_xml_subset = tmpdir_output_band  + os.path.sep + 'graph_xml_subset.xml'
            output_subset_tif = tmpdir_output_band + os.path.sep + 'band_subset.tif'

            command = es_constants.gpt_exec+' '+ graph_xml_subset   #es_constants.gpt_exec
            status=os.system(command)

            # pre_processed_list.append(output_subset_tif)
            # # ToDo : check the status or use try/except
            if os.path.exists(output_subset_tif):
                interm_files_list.append(output_subset_tif)

        # Check at least 1 file is reprojected file is there
        if len(interm_files_list) == 0:
            my_logger.debug('No any file overlapping the ROI. Return')
            return -1

        if len(interm_files_list) > 1 :
            out_tmp_file_gtiff = tmpdir + os.path.sep + re_process+'_merged.tif'
            input_files_str = ''
            for file_add in interm_files_list:
                input_files_str += ' '
                input_files_str += file_add
            command = 'gdalwarp -srcnodata "{}" -dstnodata "{}" -ot Float32 {} {}'.format(int(no_data), int(no_data),
                 input_files_str, out_tmp_file_gtiff)
            # command = 'gdalwarp -srcnodata "103.69266" -dstnodata "1000" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
            #     input_files_str, out_tmp_file_gtiff)
            my_logger.info('Command for merging is: ' + command)
            os.system(command)
            pre_processed_list.append(out_tmp_file_gtiff)
        else:
            pre_processed_list.append(interm_files_list[0])

    return pre_processed_list


def pre_process_netcdf_VGT300(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the PROBV300 product from VGT
#   Returns -1 if nothing has to be done on the passed files
#

    # Prepare the output file list
    pre_processed_list = []

    list_input_files = []


    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        temp_list_input_files = input_files
    else:
        temp_list_input_files = []
        temp_list_input_files.append(input_files)

    # Select only the 'day-time' files
    # for one_file in temp_list_input_files:
    #     one_filename = os.path.basename(one_file)
    #     in_date = one_filename.split('_')[7]
    #     day_data = functions.is_data_captured_during_day(in_date)
    #     if day_data:
    #         list_input_files.append(one_file)

    # Check at least 1 day-time file is there
    if len(temp_list_input_files) == 0:
        my_logger.debug('No any file captured during the day. Return')
        return -1

    # Unzips the files
    # for input_file in list_input_files:
    #
    #     # Unzip the .tar file in 'tmpdir'
    #     command = 'tar -xvf ' + input_file + ' -C ' + tmpdir + os.path.sep # ' --strip-components 1'
    #     # print (command)
    #     status = os.system(command)
    #     # ToDo : check the status or use try/except

    # Loop over subproducts and extract associated files. In case of more Mapsets, more sprods exist
    for sprod in subproducts:
        interm_files_list = []
        # In each unzipped folder pre-process the dataset and store the list of files to be merged
        for input_file in temp_list_input_files:

            # Define the re_expr for extracting files
            bandname = sprod['re_extract']
            re_process = sprod['re_process']
            # no_data = sprod['nodata']
            subproductcode = sprod['subproduct']
            # TODO scale nodata value from GPT has to be computed based on the product
            # scaled_no_data = "103.69266"
            # ------------------------------------------------------------------------------------------
            # Extract latitude and longitude as geotiff in tmp_dir
            # ------------------------------------------------------------------------------------------
            # tmpdir_untar = tmpdir + os.path.sep + untar_file
            tmpdir_output_band = tmpdir + os.path.sep + re_process

            if not os.path.exists(tmpdir_output_band):
                # ES2-284 fix
                # path = os.path.join(tmpdir, untar_file)
                if os.path.isdir(tmpdir):
                    os.makedirs(tmpdir_output_band)
                else:
                    continue

            # ------------------------------------------------------------------------------------------
            # Write a graph xml and subset the product for specific band, also applying flags
            # ------------------------------------------------------------------------------------------
            functions.write_graph_xml_subset(input_file=input_file, output_dir=tmpdir, band_name=re_process)     #'l2p_flags_cloud ? NaN : sea_surface_temperature')
            #functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process)


            graph_xml_subset = tmpdir_output_band + os.path.sep + 'graph_xml_subset.xml'
            output_subset_tif = tmpdir_output_band + os.path.sep + 'band_subset.tif'

            command = es_constants.gpt_exec+' '+ graph_xml_subset   #es_constants.gpt_exec
            status=os.system(command)

            pre_processed_list.append(output_subset_tif)
            # # ToDo : check the status or use try/except
            # if os.path.exists(output_subset_tif):
            #     functions.write_graph_xml_reproject(output_dir=tmpdir_untar_band, nodata_value=scaled_no_data)
            #
            #     graph_xml_reproject = tmpdir_untar_band + os.path.sep + 'graph_xml_reproject.xml'
            #     output_reproject_tif = tmpdir_untar_band + os.path.sep + 'reprojected.tif'
            #
            #     command_reproject = es_constants.gpt_exec+' '+ graph_xml_reproject
            #     # print (command_reproject)
            #     os.system(command_reproject)
            #
            #     if os.path.exists(output_reproject_tif):
            #         output_vrt = tmpdir_untar_band + os.path.sep + 'single_band_vrt.vrt'
            #         command_translate = 'gdal_translate -b 1 -a_nodata '+scaled_no_data+' -of VRT '+output_reproject_tif+ ' '+output_vrt
            #         os.system(command_translate)
            #         interm_files_list.append(output_vrt)

        # # Check at least 1 file is reprojected file is there
        # if len(interm_files_list) == 0:
        #     my_logger.debug('No any file overlapping the ROI. Return')
        #     return -1
        #
        # if len(interm_files_list) > 1 :
        #     out_tmp_file_gtiff = tmpdir + os.path.sep + re_process+'_merged.tif'
        #     input_files_str = ''
        #     for file_add in interm_files_list:
        #         input_files_str += ' '
        #         input_files_str += file_add
        #     command = 'gdalwarp -srcnodata "{}" -dstnodata "{}" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(scaled_no_data, int(no_data),
        #          input_files_str, out_tmp_file_gtiff)
        #     # command = 'gdalwarp -srcnodata "103.69266" -dstnodata "1000" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
        #     #     input_files_str, out_tmp_file_gtiff)
        #     my_logger.info('Command for merging is: ' + command)
        #     os.system(command)
        #     pre_processed_list.append(out_tmp_file_gtiff)
        # else:
        #     pre_processed_list.append(interm_files_list[0])

    return pre_processed_list


# def pre_process_netcdf_s3_wrr_gdal(subproducts, tmpdir, input_files, my_logger, in_date=None):
# # -------------------------------------------------------------------------------------------------------
# #   Pre-process the Sentinel 3 Level 2 product from OLCI - WRR
# #
#     import h5py
#     # Hard-coded definitions:
#     geo_file = 'geo_coordinates.nc'
#     coord_scale = 1000000.0
#     lat_file = 'latitude.tif'
#     long_file = 'longitude.tif'
#
#     # Prepare the output file list
#     pre_processed_list = []
#
#     interm_files_list = []
#     list_input_files = []
#
#     # Build a list of subdatasets to be extracted
#     # list_to_extr = []
#     # for sprod in subproducts:
#     #     if sprod != 0:
#     #         list_to_extr.append(sprod['re_extract'])
#
#
#     # Make sure input is a list (if only a string is received, it loops over chars)
#     if isinstance(input_files, list):
#         temp_list_input_files = input_files
#     else:
#         temp_list_input_files = []
#         temp_list_input_files.append(input_files)
#
#     # Select only the 'day-time' files
#     for one_file in temp_list_input_files:
#         one_filename = os.path.basename(one_file)
#         in_date = one_filename.split('_')[7]
#         day_data = functions.is_data_captured_during_day(in_date)
#         if day_data:
#             list_input_files.append(one_file)
#
#     # Unzips the files
#     for input_file in list_input_files:
#
#         # Unzip the .tar file in 'tmpdir'
#         command = 'tar -xvf ' + input_file + ' -C ' + tmpdir + os.path.sep # ' --strip-components 1'
#         # print (command)
#         status = os.system(command)
#
#
#     # Loop over subproducts and extract associated files
#     for sprod in subproducts:
#
#         # In each unzipped folder pre-process the dataset and store the list of files to be merged
#         for untar_file in os.listdir(tmpdir):
#
#             # Define the re_expr for extracting files
#             bandname = sprod['re_extract']
#             re_process = sprod['re_process']
#             target_mapset = sprod['mapsetcode']
#
#             # get map set
#             mapset_info = querydb.get_mapset(mapsetcode=target_mapset)
#
#             x_size = mapset_info.pixel_shift_long  # 0.00892857
#             y_size = mapset_info.pixel_shift_lat  # -0.00892857
#
#             upper_left_long = mapset_info.upper_left_long
#             upper_left_lat = mapset_info.upper_left_lat
#             lower_right_long = upper_left_long + (x_size * mapset_info.pixel_size_x)
#             lower_right_lat = upper_left_lat + (y_size * mapset_info.pixel_size_y)
#
#             lon_min = min(upper_left_long, lower_right_long)
#             lon_max = max(upper_left_long, lower_right_long)
#             lat_min = min(upper_left_lat, lower_right_lat)
#             lat_max = max(upper_left_lat, lower_right_lat)
#
#             mapset_bbox = [lon_min, lat_min, lon_max, lat_max]
#
#             # get data footprint
#             data_bbox = functions.sentinel_get_footprint(dir=tmpdir+ os.path.sep + untar_file)
#
#             # Test the overlap of the footprint with the BB of mapset
#             overlap = functions.check_polygons_intersects(mapset_bbox, data_bbox)
#
#             if not overlap:
#                 continue
#
#             # ------------------------------------------------------------------------------------------
#             # Extract latitude and longitude as geotiff in tmp_dir
#             # ------------------------------------------------------------------------------------------
#             tmpdir_untar = tmpdir + os.path.sep + untar_file
#
#             geo_fullname = tmpdir_untar+ os.path.sep + geo_file
#
#             fd = h5py.File(geo_fullname, 'r')
#
#             ds = fd['latitude']
#             data_read64 = N.zeros(ds.shape, dtype=float)
#             ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
#             latitude = ds.value / coord_scale
#             # my_logger.debug('The min/avg/max for latitude in {} are: {}/{}/{}'.format(geo_file, N.min(latitude),
#             #                                                                           N.mean(latitude),
#             #                                                                           N.max(latitude)))
#
#             output_file = tmpdir_untar + os.path.sep + lat_file
#             output_driver = gdal.GetDriverByName('GTiff')
#             orig_size_x = latitude.shape[1]
#             orig_size_y = latitude.shape[0]
#             in_data_type = gdal.GDT_Float32
#             output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
#             output_ds.GetRasterBand(1).WriteArray(latitude)
#             output_ds = None
#
#             ds = fd['longitude']
#             data_read64 = N.zeros(ds.shape, dtype=float)
#             ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
#             longitude = ds.value / coord_scale
#             # my_logger.debug('The min/avg/max for longitude in {} are: {}/{}/{}'.format(geo_file, N.min(longitude),
#             #                                                                            N.mean(longitude),
#             #                                                                            N.max(longitude)))
#
#             output_file = tmpdir_untar + os.path.sep + long_file
#             output_driver = gdal.GetDriverByName('GTiff')
#             orig_size_x = longitude.shape[1]
#             orig_size_y = longitude.shape[0]
#             in_data_type = gdal.GDT_Float32
#             output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
#             output_ds.GetRasterBand(1).WriteArray(longitude)
#             output_ds = None
#
#             fd.close()
#
#             # ------------------------------------------------------------------------------------------
#             # Extract the requested band and
#             # ------------------------------------------------------------------------------------------
#
#             bandpath = tmpdir_untar + os.path.sep + bandname
#             if bandpath is None:
#                 return
#
#             fd = h5py.File(bandpath, 'r')
#
#             bandname_without_ext = os.path.splitext(bandname)[0]
#             ds = fd[re_process]
#             data_read64 = N.zeros(ds.shape, dtype=float)
#             ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
#             bandvalues = ds.value
#             # my_logger.debug(
#             #     'The min/avg/max for reflectance in {} are: {}/{}/{}'.format(geo_file, N.min(bandvalues),
#             #                                                                  N.mean(bandvalues),
#             #                                                                  N.max(bandvalues)))
#
#             un_proj_filename = bandname_without_ext + '_un_proj.tif'
#             output_file = tmpdir_untar + os.path.sep + un_proj_filename
#             output_driver = gdal.GetDriverByName('GTiff')
#             orig_size_x = bandvalues.shape[1]
#             orig_size_y = bandvalues.shape[0]
#             in_data_type = gdal.GDT_Float32
#             output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
#             output_ds.GetRasterBand(1).WriteArray(bandvalues)
#             output_ds = None
#             del output_ds
#
#             # ------------------------------------------------------------------------------------------
#             # Write a vrt file and Reproject to lat/long
#             # ------------------------------------------------------------------------------------------
#
#             # TODO: replace the part below with info from mapset -> comment ?
#             d_lon_min = N.min(longitude)
#             d_lat_min = N.min(latitude)
#             d_lon_max = N.max(longitude)
#             d_lat_max = N.max(latitude)
#
#             functions.write_vrt_georef(output_dir=tmpdir_untar, band_file=un_proj_filename, n_lines=orig_size_x,
#                                        n_cols=orig_size_y)
#
#             input_vrt = tmpdir_untar + os.path.sep + 'reflectance.vrt'
#             output_tif = tmpdir + os.path.sep + untar_file+bandname_without_ext + '.tif'
#
#             command = 'gdalwarp -srcnodata "255" -dstnodata "255" -te {} {} {} {} -s_srs "epsg:4326" -tr {} {} -r near -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
#                 d_lon_min, d_lat_min, d_lon_max, d_lat_max, abs(x_size), abs(y_size), input_vrt, output_tif)
#
#             os.system(command)
#
#             interm_files_list.append(output_tif)
#
#     if len(interm_files_list) > 1 :
#         out_tmp_file_gtiff = tmpdir + os.path.sep + 'merged.tif.merged'
#         input_files_str = ''
#         for file_add in interm_files_list:
#             input_files_str += ' '
#             input_files_str += file_add
#
#         command = 'gdalwarp -srcnodata "255" -dstnodata "255" -te {} {} {} {} -s_srs "epsg:4326" -tr {} {} -r near -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
#             lon_min, lat_min, lon_max, lat_max, abs(x_size), abs(y_size), input_files_str, out_tmp_file_gtiff)
#         ###Take gdal_merge.py from es2globals
#         # command = es_constants.gdal_merge + ' -n 255 -a_nodata 255' + ' -o '   #-co \"compress=lzw\" -ot Float32
#         #
#         # out_tmp_file_gtiff = tmpdir + os.path.sep + 'merged.tif.merged'
#         #
#         # command += out_tmp_file_gtiff
#         #
#         # for file_add in interm_files_list:
#         #     command += ' '
#         #     command += file_add
#         my_logger.info('Command for merging is: ' + command)
#         os.system(command)
#         pre_processed_list.append(out_tmp_file_gtiff)
#     else:
#         pre_processed_list.append(interm_files_list[0])
#     return pre_processed_list


def pre_process_netcdf_s3_wst(subproducts, tmpdir, input_files, my_logger, in_date=None, zipped=False):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Sentinel 3 Level 2 product from SLSTR - WST
#
#   Description: the current implementation is based on GPT, and includes the following steps
#
#       1. Unzipping into a temp dir
#       2. Write a 'subset' graph xml in order to:
#           a. Subset geographically:
#           b. Band subset (SST only)
#           c. Apply a flag (band math)
#       3. Write a reprojection ..
#       4. Merge by applying input and output nodata (-n -54.53 -a_nodata -32768)
#
#   NOTE: now we mask by using l2p_flags_cloud ('True' means cloud detected -> reject)
#

    # Prepare the output file list
    pre_processed_list = []

    list_input_files = []

    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files, list):
        temp_list_input_files = input_files
    else:
        temp_list_input_files = []
        temp_list_input_files.append(input_files)

        # Select only the 'day-time' files
    for one_file in temp_list_input_files:
        one_filename = os.path.basename(one_file)
        in_date = one_filename.split('_')[7]
        day_data = functions.is_data_captured_during_day(in_date)
        if day_data:
            list_input_files.append(one_file)

    # Check at least 1 day-time file is there
    if len(list_input_files) == 0:
        my_logger.debug('No any file captured during the day. Return')
        return -1

    # Unzips the file
    for input_file in list_input_files:

        if zipped:
            # Unzip the .tar file in 'tmpdir'
            command = 'unzip ' + input_file + ' -d ' + tmpdir + os.path.sep  # ' --strip-components 1'
            print (command)
            status = os.system(command)
            # TODO: Change the code to OS independent
            # from zipfile import ZipFile
            # with ZipFile('input_file','r') as zipObj:
            #     zipObj.extractall(tmpdir + os.path.sep)

        else:
            # Unzip the .tar file in 'tmpdir'
            command = 'tar -xvf ' + input_file + ' -C ' + tmpdir + os.path.sep  # ' --strip-components 1'
            print (command)
            status = os.system(command)
            # TODO: Change the code to OS independent
            # import tarfile
            # tar = tarfile.open(input_file)
            # tar.extractall(path=tmpdir + os.path.sep)  # untar file into same directory
            # tar.close()

    # Loop over subproducts and extract associated files
    for sprod in subproducts:

        interm_files_list = []
        # In each unzipped folder preprocess the dataset and store the list of files to be merged
        for untar_file in os.listdir(tmpdir):

            # Define the re_expr for extracting files
            bandname = sprod['re_extract']
            re_process = sprod['re_process']
            no_data = sprod['nodata']
            # TODO scale nodata value from GPT has to be computed based on the product
            scaled_no_data = "-54.53"
            target_mapset = sprod['mapsetcode']

            tmpdir_untar = tmpdir + os.path.sep + untar_file
            tmpdir_untar_band = tmpdir + os.path.sep + untar_file + os.path.sep + re_process

            if not os.path.exists(tmpdir_untar_band):
                # ES2-284 fix
                # path = os.path.join(tmpdir, untar_file)
                if os.path.isdir(tmpdir_untar):
                    os.makedirs(tmpdir_untar_band)
                else:
                    continue
            # ------------------------------------------------------------------------------------------
            # Write a graph xml and subset the product for specific band
            # ------------------------------------------------------------------------------------------
            #functions.write_graph_xml_subset(output_dir=tmpdir_untar, band_name=re_process)
            #functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process, expression='l2p_flags_cloud ? NaN : sea_surface_temperature')
            functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process, expression='(quality_level_acceptable_quality or quality_level_best_quality) ? sea_surface_temperature : NaN')
            graph_xml_subset = tmpdir_untar_band + os.path.sep + 'graph_xml_subset.xml'
            output_subset_tif = tmpdir_untar_band + os.path.sep + 'band_subset.tif'

            command = es_constants.gpt_exec+' '+ graph_xml_subset
            print (command)
            os.system(command)

            if os.path.exists(output_subset_tif):
                # subset_files_list.append(output_subset_tif)
                functions.write_graph_xml_reproject(output_dir=tmpdir_untar_band, nodata_value=scaled_no_data)

                graph_xml_reproject = tmpdir_untar_band + os.path.sep + 'graph_xml_reproject.xml'
                output_reproject_tif = tmpdir_untar_band + os.path.sep + 'reprojected.tif'

                command_reproject = es_constants.gpt_exec + ' ' + graph_xml_reproject
                print (command_reproject)
                os.system(command_reproject)

                if os.path.exists(output_reproject_tif):
                    output_vrt = tmpdir_untar_band + os.path.sep + 'single_band_vrt.vrt'
                    command_translate = 'gdal_translate -b 1 -of VRT ' + output_reproject_tif + ' ' + output_vrt
                    os.system(command_translate)
                    interm_files_list.append(output_vrt)

        # Check at least 1 file is reprojected file is there
        if len(interm_files_list) == 0:
            my_logger.debug('No any file overlapping the ROI. Return')
            return -1

        if len(interm_files_list) > 1 :
            command = es_constants.gdal_merge + ' -of GTiff '+ '-n '+ scaled_no_data+' -a_nodata '+ str(int(no_data))+' -ot Float32 ' + ' -o '  # -co \"compress=lzw\" -ot Float32  -n -32768 -a_nodata -32768

            out_tmp_file_gtiff = tmpdir + os.path.sep + 'merged.tif.merged'

            command += out_tmp_file_gtiff

            for file_add in interm_files_list:
                command += ' '
                command += file_add
            my_logger.info('Command for merging is: ' + command)
            os.system(command)
            pre_processed_list.append(out_tmp_file_gtiff)
        else:
            pre_processed_list.append(interm_files_list[0])
    return pre_processed_list


    # ------------------------------------------------------------------------------------------------------------
    # The part below is the GDAL (rather then GPT) implementation, which we keep for possible re-use in the future.
    # ------------------------------------------------------------------------------------------------------------

    # command = es_constants.gdal_merge + ' -n -32768 -a_nodata -32768' + ' -o '     #-ot Float32    -co \"compress=lzw\"  -n -32768
    #
    # out_tmp_file_gtiff = tmpdir + os.path.sep + 'merged.tif.merged'
    #
    # command += out_tmp_file_gtiff
    #
    # for file_add in interm_files_list:
    #         command += ' '
    #         command += file_add
    # my_logger.info('Command for merging is: ' + command)
    # os.system(command)
    # pre_processed_list.append(out_tmp_file_gtiff)
    #
    # return pre_processed_list


    # command='tar -xvf '+input_file+' -C '+tmpdir+os.path.sep +' --strip-components 1'
    # print (command)
    # status = os.system(command)
    #
    # # Test the overlap of the footprint with the BB of mapset
    # # get map set
    # mapset_info = querydb.get_mapset(mapsetcode=target_mapset)
    #
    # x_size = mapset_info.pixel_shift_long  # 0.00892857
    # y_size = mapset_info.pixel_shift_lat  # 0.00892857
    #
    # upper_left_long = mapset_info.upper_left_long
    # upper_left_lat = mapset_info.upper_left_lat
    # lower_right_long = upper_left_long + (x_size * mapset_info.pixel_size_x)
    # lower_right_lat = upper_left_lat + (y_size * mapset_info.pixel_size_y)
    #
    # lon_min = min(upper_left_long, lower_right_long)
    # lon_max = max(upper_left_long, lower_right_long)
    # lat_min = min(upper_left_lat, lower_right_lat)
    # lat_max = max(upper_left_lat, lower_right_lat)
    #
    # mapset_bbox = [lon_min, lat_min, lon_max, lat_max]
    #
    # # get data footprint
    # data_bbox = functions.sentinel_get_footprint(dir=tmpdir)
    #
    # # Test the overlap of the footprint with the BB of mapset
    # overlap = functions.check_polygons_intersects(mapset_bbox, data_bbox)
    #
    # if not overlap:
    #     return
    #
    # for ifile in os.listdir(tmpdir):
    #
    #     # Unzip to tmpdir and add to list
    #     if re.match('.*' + bandname + '*.', ifile):
    #         geo_fullname = tmpdir + os.path.sep + ifile
    #
    # if geo_fullname is None:
    #     return
    #
    # fd=h5py.File(geo_fullname,'r')
    #
    # ds=fd['lat']
    # data_read64=N.zeros(ds.shape,dtype=float)
    # ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
    # latitude=ds.value
    # my_logger.debug('The min/avg/max for latitude in {} are: {}/{}/{}'.format(bandname, N.min(latitude),N.mean(latitude),N.max(latitude)))
    #
    # output_file = tmpdir+ os.path.sep+lat_file
    # output_driver = gdal.GetDriverByName('GTiff')
    # orig_size_x = latitude.shape[1]
    # orig_size_y = latitude.shape[0]
    # in_data_type= gdal.GDT_Float32
    # output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
    # output_ds.GetRasterBand(1).WriteArray(latitude)
    # output_ds = None
    #
    # ds=fd['lon']
    # data_read64=N.zeros(ds.shape,dtype=float)
    # ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
    # longitude=ds.value
    # my_logger.debug('The min/avg/max for longitude in {} are: {}/{}/{}'.format(bandname, N.min(longitude),N.mean(longitude),N.max(longitude)))
    #
    # output_file = tmpdir+ os.path.sep+long_file
    # output_driver = gdal.GetDriverByName('GTiff')
    # orig_size_x = longitude.shape[1]
    # orig_size_y = longitude.shape[0]
    # in_data_type= gdal.GDT_Float32
    # output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
    # output_ds.GetRasterBand(1).WriteArray(longitude)
    # output_ds = None
    #
    # # ------------------------------------------------------------------------------------------
    # # Extract the requested band and
    # # ------------------------------------------------------------------------------------------
    #
    #
    # ds = fd[re_process]
    # data_read64 = N.zeros(ds.shape, dtype=float)
    # ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
    # bandvalues = ds.value
    # my_logger.debug('The min/avg/max for reflectance in {} are: {}/{}/{}'.format(bandname, N.min(bandvalues), N.mean(bandvalues),
    #                                                                    N.max(bandvalues)))
    #
    # un_proj_filename = re_process + '_un_proj.tif'
    # output_file = tmpdir+ os.path.sep + un_proj_filename
    # output_driver = gdal.GetDriverByName('GTiff')
    # orig_size_x = bandvalues.shape[2]
    # orig_size_y = bandvalues.shape[1]
    # in_data_type = gdal.GDT_Float32
    # output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
    # #If the dataset is three dimension use this case(In this case sst is skin sst so there is just single ds)
    # for i, bandvalue in enumerate(bandvalues, 1):
    #     output_ds.GetRasterBand(i).WriteArray(bandvalue)
    # output_ds = None
    # del output_ds
    #
    # # ------------------------------------------------------------------------------------------
    # # Write a vrt file and Reproject to lat/long
    # # ------------------------------------------------------------------------------------------
    #
    # # TODO: replace the part below with info from mapset
    # lon_min = N.min(longitude)
    # lat_min = N.min(latitude)
    # lon_max = N.max(longitude)
    # lat_max = N.max(latitude)
    #
    # functions.write_vrt_georef(output_dir=tmpdir, band_file=un_proj_filename,n_lines=orig_size_x, n_cols=orig_size_y)
    # input_vrt_filename = 'reflectance.vrt'
    # input_vrt = tmpdir + os.path.sep+ input_vrt_filename
    # output_tif = tmpdir+ os.path.sep + re_process + '.tif'
    #
    # command = 'gdalwarp -dstnodata "-32768" -te {} {} {} {} -s_srs "epsg:4326" -tr {} {} -r near -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
    #     lon_min, lat_min, lon_max, lat_max, abs(x_size), abs(y_size), input_vrt, output_tif)
    #
    # os.system(command)
    #
    # interm_files_list.append(output_tif)
    #
    # return interm_files_list


def pre_process_oilspill_detection_sentinel1(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Sentinel 1 GRD product IW VV
#   Returns -1 if nothing has to be done on the passed files
#

    # Prepare the output file list
    pre_processed_list = []

    # Loop over subproducts and extract associated files. In case of more Mapsets, more sprods exist
    for sprod in subproducts:
        interm_files_list = []

        for input_file in input_files:

            # In each unzipped folder pre-process the dataset and store the list of files to be merged

            # Define the re_expr for extracting files
            bandname = sprod['re_extract']  #Amplitude_VV,Intensity_VV
            re_process = sprod['re_process']
            no_data = sprod['nodata']
            # TODO scale nodata value from GPT has to be computed based on the product
            scaled_no_data = "0"

            # ------------------------------------------------------------------------------------------
            # Write a graph xml and subset the product for specific band, also applying flags
            # ------------------------------------------------------------------------------------------
            graph_xml_terrain_correction_oilspill = tmpdir + os.path.sep + 'graph_xml_terrain_correction_oilspill.xml'
            output_tif = tmpdir + os.path.sep + 'band_subset.tif'

            functions.write_graph_xml_terrain_correction_oilspill(tmpdir, input_file, re_process, output_tif)
            #functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process)

            command = es_constants.gpt_exec+' '+ graph_xml_terrain_correction_oilspill
            status=os.system(command)
            # ToDo : check the status or use try/except
            interm_files_list.append(output_tif)

        # Check at least 1 file is reprojected file is there
        if len(interm_files_list) == 0:
            my_logger.debug('No any file overlapping the ROI. Return')
            return -1

        if len(interm_files_list) > 1 :
            out_tmp_file_gtiff = tmpdir + os.path.sep + 'merged.tif.merged'
            input_files_str = ''
            for file_add in interm_files_list:
                input_files_str += ' '
                input_files_str += file_add
            command = 'gdalwarp -srcnodata "{}" -dstnodata "{}" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(scaled_no_data, int(no_data),
                 input_files_str, out_tmp_file_gtiff)
            # command = 'gdalwarp -srcnodata "103.69266" -dstnodata "1000" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
            #     input_files_str, out_tmp_file_gtiff)
            my_logger.info('Command for merging is: ' + command)
            os.system(command)
            pre_processed_list.append(out_tmp_file_gtiff)
        else:
            pre_processed_list.append(interm_files_list[0])

    return pre_processed_list


def pre_process_aviso_mwind(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Aviso Mwind
#
    interm_files_list = []

    # Make sure it is a list (if only a string is returned, it loops over chars)
    if isinstance(input_files, list):
        list_input_files = input_files
    else:
        list_input_files=[]
        list_input_files.append(input_files)

    if isinstance(list_input_files, list):
        if len(list_input_files) > 1:
            raise Exception('More than 1 file passed: %i ' % len(list_input_files))
    input_file = list_input_files[0]

    #for input_file in list_input_files:
    my_logger.info('Unzipping/processing: .gzip case')
    gzipfile = gzip.open(input_file)                 # Create ZipFile object
    data = gzipfile.read()                           # Get the list of its contents
    filename = os.path.basename(input_file)
    filename = filename.replace('.gz', '')
    myfile_path = os.path.join(tmpdir, filename)
    myfile = open(myfile_path, "wb")
    myfile.write(data)
    myfile.close()
    gzipfile.close()

    input_file = myfile.name
    # # Create a coherent intermediate file list
    # for subproduct in subproducts:
    #     interm_files_list.append(myfile_path)
    #
    #     # Prepare the output file list
    #
    #
    # pre_processed_list = []
    #

    # # Build a list of subdatasets to be extracted
    list_to_extr = []
    geotiff_files = []
    previous_id_subdataset = ''

    for sprod in subproducts:
        if sprod != 0:
            subprod_to_extr = sprod['re_extract']

            # Test the. nc file and read list of datasets
            netcdf = gdal.Open(input_file)
            sdslist = netcdf.GetSubDatasets()

            if len(sdslist) >= 1:
                # Loop over datasets and extract the one from each unzipped
                for subdataset in sdslist:
                    netcdf_subdataset = subdataset[0]
                    id_subdataset = netcdf_subdataset.split(':')[-1]

                    if id_subdataset == subprod_to_extr:
                        if id_subdataset == previous_id_subdataset:
                            # Just append the last filename once again
                            geotiff_files.append(myfile_path)
                        else:
                            selected_sds = 'NETCDF:' + input_file + ':' + id_subdataset
                            sds_tmp = gdal.Open(selected_sds)
                            filename = os.path.basename(input_file) + '.geotiff'
                            myfile_path = os.path.join(tmpdir, filename)
                            write_ds_to_geotiff(sds_tmp, myfile_path)
                            sds_tmp = None
                            geotiff_files.append(myfile_path)
                            previous_id_subdataset = id_subdataset
                            # MC 26.07.2016: read/store scaling
                            try:
                                status = functions.save_netcdf_scaling(selected_sds, myfile_path)
                            except:
                                logger.debug('Error in reading scaling')
            else:
                # if id_subdataset == previous_id_subdataset:
                #     # Just append the last filename once again
                #     geotiff_files.append(myfile_path)
                # else:
                    # No subdatasets: e.g. SST -> read directly the .nc
                filename = os.path.basename(input_file) + '.geotiff'
                myfile_path = os.path.join(tmpdir, filename)
                write_ds_to_geotiff(netcdf, myfile_path)
                geotiff_files.append(myfile_path)
                # previous_id_subdataset = id_subdataset
                    # MC 26.07.2016: read/store scaling
                    # try:
                    #     status = functions.save_netcdf_scaling(sds_tmp, myfile_path)
                    # except:
                    #     logger.warning('Error in reading scaling')

            netcdf = None

    return geotiff_files


def pre_process_inputs(preproc_type, native_mapset_code, subproducts, input_files, tmpdir, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process one or more input files by:
#   1. Unzipping (optionally extracting one out of many layers - SDSs)
#   2. Extract one or more datasets from a zip file, or a multi-layer file (e.g. HDF)
#   3. Merging different segments/regions/tiles (compose area)
#   4. Format conversion to GTIFF
#   5. Apply geo-reference (native_mapset)
#
#   Input: one or more input files in the 'native' format, for a single data and a single mapset
#   Output: one or more files (1 foreach subproduct), geo-referenced in GTIFF
#
#   Arguments:
#       preproc_type:    type of preprocessing
#           MSG_MPE: 4 segments to be composed into a grib
#           MODIS_HDF4_TILE: hv-modis tiles, in hdf4 formats, containing 1+ SDSs
#           LSASAF_HDF5: landsaf region (Euro/SAme/SAfr/NAfr), HDF5 containing 1+ SDSs
#           PML_NETCDF: ocean product from PML in netcdf.
#           UNZIP: .zipped files containing more file, to be filtered by using sprod['re_extract'].
#           MODIS_SST_HDF4: MODIS SST files, in HDF4 (multi-SDS) b2zipped.
#           BZIP2: .bz2 zipped files (containing 1 file only).
#           GEOREF: only georeference, by assigning native mapset
#           HDF5_UNZIP: zipped files containing HDF5 (see g2_BIOPAR)
#           NASA_FIRMS: convert from csv to GTiff
#           NETCDF: netcdf datasets (e.g. MODIS Ocean products)
#           ECMWF: zipped file containing an .img and .hdr
#           CPC_BINARY: binary file in big-endian
#           BINARY: .bil product (e.g. GEOWRSI)
#           ENVI_2_GTIFF: convert ENVI files(.img,.hdr) to GEOTIF
#           NETCDF_S3_WRR: S3A OLCI WRR data treatment using SNAP-GPT to do band subset, reproject.
#           NETCDF_S3_WST: S3A SLSTR WST data treatment using SNAP-GPT to do band subset, reproject.
#           MERGE_TILE: Merge the tiles from VITO website and convert to nobigtif format
#           JRC_WBD_GEE: merges the various tiles of the .tif files retrieved from GEE application and remove the bigtif tag(works only in developement machine)
#       native_mapset_code: id code of the native mapset (from datasource_descr)
#       subproducts: list of subproducts to be extracted from the file. Contains dictionaries such as:
#           see ingestion() for full description
#       input_files: list of input files
#   Returned:
#       output_file: temporary created output file[s]
#       None: wait for additional files (e.g. MSG_MPE - in 4 segments)
#       -1: nothing to do on the passed files (e.g. for S3A night-files or out-of-ROI).
#

    my_logger.info("Input files pre-processing by using method: %s" % preproc_type)

    georef_already_done = False

    try:
        if preproc_type == 'MSG_MPE':
            interm_files = pre_process_msg_mpe (subproducts, tmpdir , input_files, my_logger)

        elif preproc_type == 'MPE_UMARF':
            interm_files = pre_process_mpe_umarf (subproducts, tmpdir , input_files, my_logger)

        elif preproc_type == 'MODIS_HDF4_TILE':
            interm_files = pre_process_modis_hdf4_tile (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'MERGE_TILE':
            interm_files = pre_process_merge_tile (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'LSASAF_HDF5':
            interm_files = drive_pre_process_lsasaf_hdf5 (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'PML_NETCDF':
            interm_files = pre_process_pml_netcdf (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'UNZIP':
            interm_files = pre_process_unzip (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'BZIP2':
            interm_files = pre_process_bzip2 (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'GEOREF_NETCDF':
            interm_files = pre_process_georef_netcdf(subproducts, native_mapset_code, tmpdir, input_files)
            georef_already_done = True

        elif preproc_type == 'BZ2_HDF4':
            interm_files = pre_process_bz2_hdf4 (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'HDF5_ZIP':
            interm_files = pre_process_hdf5_zip (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'HDF5_GLS':
            interm_files = pre_process_hdf5_gls (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'HDF5_GLS_NC':
            interm_files = pre_process_hdf5_gls_nc(subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'NASA_FIRMS':
            interm_files = pre_process_nasa_firms (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'GZIP':
            interm_files = pre_process_gzip (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'NETCDF':
            interm_files = pre_process_netcdf (subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'JRC_WBD_GEE':
            interm_files = pre_process_wdb_gee (subproducts, native_mapset_code, tmpdir, input_files, my_logger)
            georef_already_done = True

        elif preproc_type == 'ECMWF_MARS':
            interm_files = pre_process_ecmwf_mars(subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'ENVI_2_GTIFF':
            interm_files = pre_process_envi_to_geotiff(subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'CPC_BINARY':
            interm_files = pre_process_cpc_binary(subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'GSOD':
            interm_files = pre_process_gsod(subproducts, tmpdir, input_files, my_logger, in_date=in_date)

        elif preproc_type == 'NETCDF_S3_WRR_ZIP':
            interm_files = pre_process_netcdf_s3_wrr(subproducts, tmpdir, input_files, my_logger, in_date=in_date, zipped=True)

        elif preproc_type == 'NETCDF_S3_WRR':
            interm_files = pre_process_netcdf_s3_wrr(subproducts, tmpdir, input_files, my_logger, in_date=in_date)

        elif preproc_type == 'NETCDF_GPT_SUBSET':
            interm_files = pre_process_netcdf_VGT300(subproducts, tmpdir, input_files, my_logger, in_date=in_date)

        elif preproc_type == 'NETCDF_S3_WST':
            interm_files = pre_process_netcdf_s3_wst(subproducts, tmpdir, input_files, my_logger, in_date=in_date)

        elif preproc_type == 'NETCDF_S3_WST_ZIP':
            interm_files = pre_process_netcdf_s3_wst(subproducts, tmpdir, input_files, my_logger, in_date=in_date, zipped=True)

        elif preproc_type == 'TARZIP':
            interm_files = pre_process_tarzip(subproducts, tmpdir, input_files, my_logger)

        elif preproc_type == 'TARZIP_WD_GEE':
            interm_files = pre_process_tarzip_wd_gee(subproducts, tmpdir, input_files, my_logger)
            georef_already_done = True

        elif preproc_type == 'NETCDF_AVISO':
            interm_files = pre_process_aviso_mwind(subproducts, tmpdir, input_files, my_logger)
        # elif preproc_type == 'GSOD':
        #     interm_files = pre_process_netcdf_s3_wst(subproducts, tmpdir, input_files, my_logger, in_date=in_date)
        elif preproc_type == 'SNAP_SUBSET_NC':
            interm_files = pre_process_snap_subset_nc(subproducts, tmpdir, input_files, my_logger, in_date=in_date)

        else:
            my_logger.error('Preproc_type not recognized:[%s] Check in DB table. Exit' % preproc_type)
    except:
        my_logger.error('Error in pre-processing routine. Exit')
        raise NameError('Error in pre-processing routine')

    # Check if None is returned (i.e. waiting for remaining files)
    if interm_files is None:
        my_logger.info('Waiting for additional files to be received. Exit')
        return None

    # Check if -1 is returned (i.e. nothing to do on the passed files)
    if interm_files is -1:
        my_logger.info('Nothing to do on the passed files. Exit')
        return -1

    # Make sure it is a list (if only a string is returned, it loops over chars)
    if isinstance(interm_files, list):
        list_interm_files = interm_files
    else:
        list_interm_files = []
        list_interm_files.append(interm_files)

    # Create native mapset (or assign as empty string)
    if native_mapset_code != 'default' and (not georef_already_done):

        # Create Mapset object and test
        native_mapset = mapset.MapSet()
        native_mapset.assigndb(native_mapset_code)
        my_logger.debug('Native mapset IS passed: ' + native_mapset.short_name)

        if native_mapset.validate():
            my_logger.error('Native mapset passed is invalid: ' + native_mapset.short_name)
            return 1
        # Loop over interm_files and assign mapset
        for intermFile in list_interm_files:
            my_logger.debug('Intermediate file: ' + intermFile)

            # Open input dataset in update mode
            orig_ds = gdal.Open(intermFile, gdal.GA_Update)

            # Test result: in case of error (e.g. for nc files, it does not raise exception)
            # If wrong -> Open input dataset in read-only
            if orig_ds is None:
                orig_ds = gdal.Open(intermFile, gdal.GA_ReadOnly)

            # Otherwise read from native_mapset, and assign to ds
            orig_cs = native_mapset.spatial_ref
            orig_geo_transform = native_mapset.geo_transform
            orig_size_x = native_mapset.size_x
            orig_size_y = native_mapset.size_y

            orig_ds.SetGeoTransform(native_mapset.geo_transform)
            orig_ds.SetProjection(native_mapset.spatial_ref.ExportToWkt())

    return list_interm_files


def ingest_file(interm_files_list, in_date, product, subproducts, datasource_descr, my_logger, in_files='', echo_query=False):
# -------------------------------------------------------------------------------------------------------
#   Ingest one or more files (a file for each subproduct)
#   Arguments:
#       interm_files_list: input file full name (1 per subproduct)
#       date: product date
#       product: product description name (for DB insertions)
#       subproducts: list of subproducts to be extracted from the file. Contains dictionaries as described in
#           ingestion() header
#       datasource_descr: from the corresponding DB table (all info on input-file naming)
#       in_files[option]: list of input files
#       echo_query[option]: force print-out from query_db functions
#
#   NOTE: mapset management: mapset is the geo-reference information associated to datasets
#         There is a  'native_mapset' - associated to the input product and
#                     'target_mapset' - defined (optionally) by the user
#
#         'native_mapset': comes from the table -> 'datasource_description'
#                          if it is 'default', they georeferencing is read directly from input file
#
#         'target_mapset": comes from table 'ingestion' ('mapsetcode')
#                          MUST be specified.

    version_undef = 'undefined'
    data_dir_out = es_constants.processing_dir
    my_logger.info("Entering routine %s for product %s - date %s" % ('ingest_file', product['productcode'], in_date))

    # Test the file/files exists  (if the file doesn't exists but if the file list is more than 1 then it proceed to next step
    for infile in interm_files_list:
        if not os.path.isfile(infile) and len(interm_files_list)<=1 :
            my_logger.error('Input file: %s does not exist' % infile)
            return 1

    # Instance metadata object
    sds_meta = metadata.SdsMetadata()

    # Printout list of intermediate files
    readablelist = [' ' + os.path.basename(elem) for elem in interm_files_list]
    my_logger.info('In ingest_file: Intermediate file list: ' + ''.join(map(str, readablelist)))

    # -------------------------------------------------------------------------
    # Loop over 'intermediate files' and perform ingestion
    # Note: interm file MUST contain only 1 raster-band/subdataset
    # -------------------------------------------------------------------------
    ii = 0

    for intermFile in interm_files_list:

        # This case was implemented as the successor of "Test teh file/files exists" since if the file doesnot exist but list is more than 1 we dont throw in the previous case but here that particular error is catched
        if not os.path.isfile(intermFile):     #if intermFile == '/fake_link/':
            ii += 1
            continue

        my_logger.info("Processing intermediate file: %s" % os.path.basename(intermFile))
        tmp_dir = os.path.dirname(intermFile)

        # -------------------------------------------------------------------------
        # Collect info and prepare filenaming
        # -------------------------------------------------------------------------

        # Get information about the dataset
        args = {"productcode": product['productcode'],
                "subproductcode": subproducts[ii]['subproduct'],
                "datasource_descr_id": datasource_descr.datasource_descr_id,
                "version": product['version']}

        # Get information from sub_dataset_source table
        product_in_info = querydb.get_product_in_info(**args)

        # Check if the scaling has been read/save to .tmp dir (MC. 26.7.2016: Issue for MODIS SST .nc files)
        try:
            [in_scale_factor, in_offset] = functions.read_netcdf_scaling(intermFile)
        except:
            # Take from DB
            in_scale_factor = product_in_info.scale_factor
            in_offset = product_in_info.scale_offset

        # See ES2-241 - remove indent to be always applied
        in_scale_type = product_in_info.scale_type

        in_nodata = product_in_info.no_data
        in_mask_min = product_in_info.mask_min
        in_mask_max = product_in_info.mask_max
        in_data_type = product_in_info.data_type_id
        in_data_type_gdal = conv_data_type_to_gdal(in_data_type)

        # Get information from 'product' table
        args = {"productcode": product['productcode'], "subproductcode": subproducts[ii]['subproduct'], "version":product['version']}
        product_info = querydb.get_product_out_info(**args)
        product_info = functions.list_to_element(product_info)

        out_data_type = product_info.data_type_id
        out_scale_factor = product_info.scale_factor
        out_offset = product_info.scale_offset
        out_nodata = product_info.nodata
        out_date_format = product_info.date_format

        # Translate data type for gdal and numpy
        out_data_type_gdal = conv_data_type_to_gdal(out_data_type)
        out_data_type_numpy = conv_data_type_to_numpy(out_data_type)

        # Initialize to error value
        output_date_str = -1

        # Convert the in_date format into a convenient one for DB and file naming
        # (i.e YYYYMMDD or YYYYMMDDHHMM)
        if datasource_descr.date_format == 'YYYYMMDD':
            if functions.is_date_yyyymmdd(in_date):
                output_date_str = in_date
            else:
                output_date_str = -1

        if datasource_descr.date_format == 'YYYYMMDDHHMM':
            if functions.is_date_yyyymmddhhmm(in_date):
                output_date_str = in_date
            else:
                output_date_str = -1

        if datasource_descr.date_format == 'YYYYDOY_YYYYDOY':
            output_date_str = functions.conv_date_yyyydoy_2_yyyymmdd(str(in_date)[0:7])

        if datasource_descr.date_format == 'YYYYMMDD_YYYYMMDD':
            output_date_str = str(in_date)[0:8]
            if not functions.is_date_yyyymmdd(output_date_str):
                output_date_str = -1

        if datasource_descr.date_format == 'YYYYDOY':
            output_date_str = functions.conv_date_yyyydoy_2_yyyymmdd(in_date)

        if datasource_descr.date_format == 'YYYY_MM_DKX':
            output_date_str = functions.conv_yyyy_mm_dkx_2_yyyymmdd(in_date)

        if datasource_descr.date_format == 'YYMMK':
            output_date_str = functions.conv_yymmk_2_yyyymmdd(in_date)

        if datasource_descr.date_format == 'YYYYdMMdK':
            output_date_str = functions.conv_yyyydmmdk_2_yyyymmdd(in_date)

        if datasource_descr.date_format == 'YYYYMMDD_G2':
            # The date (e.g. 20151103) is converted to the dekad it belongs to (e.g. 20151101)
            output_date_str = functions.conv_yyyymmdd_g2_2_yyyymmdd(in_date)

        if datasource_descr.date_format == 'MMDD':
            output_date_str = str(in_date)

        if datasource_descr.date_format == 'YYYYMM':
            # Convert from YYYYMM -> YYYYMMDD
            output_date_str = str(in_date)+'01'

        if output_date_str == -1:
            output_date_str = in_date+'_DATE_ERROR_'
        else:
            if out_date_format == 'YYYYMMDDHHMM':
                if functions.is_date_yyyymmddhhmm(output_date_str):
                    out_date_str_final = output_date_str
                elif  functions.is_date_yyyymmdd(output_date_str):
                    out_date_str_final = output_date_str+'0000'
            elif out_date_format == 'YYYYMMDD':
                if functions.is_date_yyyymmdd(output_date_str):
                    out_date_str_final = output_date_str
                elif  functions.is_date_yyyymmddhhmm(output_date_str):
                    out_date_str_final = output_date_str[0:8]
            elif out_date_format == 'MMDD':
                if functions.is_date_mmdd(output_date_str):
                    out_date_str_final = output_date_str

        # Get only the short_name for output file naming
        mapset_id = subproducts[ii]['mapsetcode']

        # Define output directory and make sure it exists
        output_directory = data_dir_out + functions.set_path_sub_directory(product['productcode'],
                                                                           subproducts[ii]['subproduct'],
                                                                           'Ingest',
                                                                           product['version'],
                                                                           mapset_id,)
        my_logger.debug('Output Directory is: %s' % output_directory)
        try:
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
        except:
            my_logger.error('Cannot create output directory: ' + output_directory)
            return 1

        # Define output filename
        output_filename = output_directory + functions.set_path_filename(out_date_str_final,
                                                                         product['productcode'],
                                                                         subproducts[ii]['subproduct'],
                                                                         mapset_id,
                                                                         product['version'],
                                                                         '.tif')

        # -------------------------------------------------------------------------
        # Manage the geo-referencing associated to input file
        # -------------------------------------------------------------------------

        native_mapset_code = datasource_descr.native_mapset

        init_orig_ds = gdal.Open(intermFile, gdal.GF_Write)  #GA_Update
        if init_orig_ds is None:
            init_orig_ds = gdal.Open(intermFile, gdal.GA_ReadOnly)           # Why in ROnly !??? it generates an error below orig_ds = gdal.Open(intermFile, gdal.GA_Update)
        native_mapset = mapset.MapSet()
        native_mapset.assigndb(native_mapset_code)

        # ES-535  Create a copy to assign projection.
        intermFile_copyname = 'copy_'+os.path.basename(intermFile)
        intermFile_copy = os.path.join(os.path.dirname(intermFile), intermFile_copyname)

        # Prepare output driver
        out_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)

        # Open destination dataset # ES-535
        orig_ds = out_driver.CreateCopy(intermFile_copy, init_orig_ds, 0)

        if not native_mapset.is_wbd():
          if native_mapset_code != 'default':
            orig_cs = osr.SpatialReference(wkt=native_mapset.spatial_ref.ExportToWkt())
            #orig_cs.ImportFromWkt(native_mapset.spatial_ref)                     # ???
            orig_geo_transform = native_mapset.geo_transform
            orig_size_x = native_mapset.size_x
            orig_size_y = native_mapset.size_y

            # Complement orig_ds info (necessary to Re-project)
            try:
                orig_ds.SetGeoTransform(native_mapset.geo_transform)
                orig_ds.SetProjection(orig_cs.ExportToWkt())
            except:
                my_logger.debug('Cannot set the geo-projection .. Continue')
          else:
            try:
                # Read geo-reference from input file
                orig_cs = osr.SpatialReference()
                orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
                orig_geo_transform = orig_ds.GetGeoTransform()
                orig_size_x = orig_ds.RasterXSize
                orig_size_y = orig_ds.RasterYSize
            except:
                my_logger.debug('Cannot read geo-reference from file .. Continue')

        # TODO-M.C.: add a test on the mapset_id in DB table !
        trg_mapset = mapset.MapSet()
        trg_mapset.assigndb(mapset_id)
        logger.debug('Target Mapset is: %s' % mapset_id)

        if trg_mapset.short_name == native_mapset_code:
            reprojection = 0
        else:
            reprojection = 1

        # -------------------------------------------------------------------------
        # Generate the output file
        # -------------------------------------------------------------------------

        merge_existing_output = False
        # Check if the output file already exists
        if os.path.isfile(output_filename) and datasource_descr.area_type in ['tile','region'] and not trg_mapset.is_wbd():

            merge_existing_output = True
            # In case of merge, output_filename is generated first in 'tmp_dir', otherwise in final dir
            my_output_filename = tmp_dir + os.path.sep+os.path.basename(output_filename)

            # Prepare a tmp file in tmp_dir (for merging)
            tmp_output_file = tmp_dir + os.path.sep+os.path.basename(output_filename)+'.tmp'
            sds_meta_old = metadata.SdsMetadata()
            sds_meta_old.read_from_file(output_filename)
            old_file_list = sds_meta_old.get_item('eStation2_input_files')
            sds_meta_old = None
        else:
            my_output_filename = output_filename
            old_file_list = None

        # Do re-projection, or write to GTIFF file
        if not native_mapset.is_wbd():
          if reprojection == 1:

            my_logger.debug('Doing re-projection to target mapset: %s' % trg_mapset.short_name)
            # Get target SRS from mapset
            out_cs = trg_mapset.spatial_ref
            out_size_x = trg_mapset.size_x
            out_size_y = trg_mapset.size_y

            # Create target in memory
            mem_driver = gdal.GetDriverByName('MEM')

            # Assign mapset to dataset in memory
            mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, in_data_type_gdal)
            mem_ds.SetGeoTransform(trg_mapset.geo_transform)
            mem_ds.SetProjection(out_cs.ExportToWkt())
            # Initialize output to Output Nodata value (for PML SST UoG region)
            mem_ds.GetRasterBand(1).Fill(out_nodata)

            # Manage data type - if it is different input/output
            out_ds = mem_driver.Create('', out_size_x, out_size_y, 1, out_data_type_gdal)
            out_ds.SetGeoTransform(trg_mapset.geo_transform)
            out_ds.SetProjection(out_cs.ExportToWkt())

            # Apply Reproject-Image to the memory-driver
            orig_wkt = orig_cs.ExportToWkt()
            res = gdal.ReprojectImage(orig_ds, mem_ds, orig_wkt, out_cs.ExportToWkt(),
                                      es_constants.ES2_OUTFILE_INTERP_METHOD)

            my_logger.debug('Re-projection to target done.')

            # Read from the dataset in memory
            out_data = mem_ds.ReadAsArray()

            # Apply rescale to data
            scaled_data = rescale_data(out_data, in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max,
                                       out_data_type_numpy, out_scale_factor, out_offset, out_nodata, my_logger,
                                       in_scale_type)

            # Create a copy to output_file
            trg_ds = out_driver.CreateCopy(my_output_filename, out_ds, 0, [es_constants.ES2_OUTFILE_OPTIONS])
            trg_ds.GetRasterBand(1).WriteArray(scaled_data)

          else:

            my_logger.debug('Doing only rescaling/format conversion')

            # Read from input file
            band = orig_ds.GetRasterBand(1)
            my_logger.debug('Band Type='+gdal.GetDataTypeName(band.DataType))
            out_data = band.ReadAsArray(0, 0, orig_size_x, orig_size_y)

            # No reprojection, only format-conversion
            trg_ds = out_driver.Create(my_output_filename, orig_size_x, orig_size_y, 1, out_data_type_gdal,
                                       [es_constants.ES2_OUTFILE_OPTIONS])
            trg_ds.SetProjection(orig_ds.GetProjectionRef())
            trg_ds.SetGeoTransform(orig_geo_transform)

            # Apply rescale to data
            scaled_data = rescale_data(out_data, in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max,
                                       out_data_type_numpy, out_scale_factor, out_offset, out_nodata, my_logger,
                                       in_scale_type)
            trg_ds.GetRasterBand(1).WriteArray(scaled_data)

            orig_ds = None

        # else:
        #     # Do only renaming (and exit)
        #     shutil.copy(intermFile,output_filename)
        #     return 0
        # -------------------------------------------------------------------------
        # Assign Metadata to the ingested file
        # -------------------------------------------------------------------------

        sds_meta.assign_es2_version()
        sds_meta.assign_mapset(mapset_id)
        sds_meta.assign_from_product(product['productcode'], subproducts[ii]['subproduct'], product['version'])
        sds_meta.assign_date(out_date_str_final)
        sds_meta.assign_subdir_from_fullpath(output_directory)
        sds_meta.assign_compute_time_now()

        # Check not WD-GEE
        if not trg_mapset.is_wbd():
          # Write metadata, if not merging is needed
          if not merge_existing_output:
            sds_meta.assign_input_files(in_files)
            sds_meta.write_to_ds(trg_ds)

            # Close output file
            trg_ds = None
            out_driver = None
            sds_meta.assign_input_files(in_files)

          else:
            # Close output file
            trg_ds = None
            out_driver = None

            # Merge the old and new output products into a 'tmp' file
            # try:
            #     command = 'gdalwarp '
            #     command += ' -co \"COMPRESS=LZW\"'
            #     command += ' -srcnodata ' + str(out_nodata)
            #     command += ' -dstnodata ' + str(out_nodata) + ' -of GTiff '
            #     command += my_output_filename + ' ' + output_filename+ ' ' + tmp_output_file
            #     my_logger.debug('Command for merging is: ' + command)
            #     os.system(command)
            #     # inter_processed_list.append(clipped_file)
            # except:
            #     pass
            try:
                command = es_constants.gdal_merge + ' -n '+str(out_nodata)
                command += ' -a_nodata '+str(out_nodata)
                command += ' -of GTiff '
                command += ' -co \"compress=lzw\" -o '
                command += tmp_output_file
                command += ' '+ my_output_filename+ ' '+output_filename
                my_logger.debug('Command for merging is: ' + command)
                os.system(command)
            except:
                pass

            # Write metadata to output
            if old_file_list is not None:
                # Merge the old and new file list (note that old list is a string !)
                final_list = sds_meta.merge_input_file_lists(old_file_list, in_files)
                sds_meta.assign_input_files(final_list)
            else:
                sds_meta.assign_input_files(in_files)

            sds_meta.write_to_file(tmp_output_file)

            # Save the .tmp as output
            if os.path.isfile(output_filename):
                os.remove(output_filename)
            shutil.move(tmp_output_file,output_filename)

        # WD-GEE case
        else:
            sds_meta.assign_input_files(in_files)
            sds_meta.assign_input_files(os.path.basename(intermFile))
            sds_meta.write_to_file(intermFile)
            shutil.copy(intermFile,output_filename)

        # -------------------------------------------------------------------------
        # Upsert into DB table 'products_data'
        # -------------------------------------------------------------------------

        filename = os.path.basename(output_filename)
        # Loop on interm_files
        ii += 1


def ingest_file_vers_1_0(input_file, in_date, product_def, target_mapset, my_logger, product_in_info, echo_query=False):
# -------------------------------------------------------------------------------------------------------
#   Convert 1 file from 1.0 to 2.0 eStation format
#   Arguments:
#       input_file: input file full name (1 per subproduct)
#       in_date: product date
#       product_def: definition of the 2.0 product. It contains:
#                   productcode
#                   subproductcode
#                   version
#                   type: Ingest/Derived
#
#       echo_query[option]: force print-out from query_db functions
#
#   NOTE: mapset management: mapset is the geo-reference information associated to datasets
#         The input product is already georeferenced: case 'default'
#         'target_mapset": comes from table 'ingestion' ('mapsetcode')
#                          MUST be specified.

    version_undef = 'undefined'
    my_logger.info("Entering routine %s for product %s - date %s" % ('ingest_file_vers_1_0', product_def['productcode'], in_date))

    # Test the file exists
    if not os.path.isfile(input_file):
        my_logger.error('Input file: %s does not exist' % input_file)
        return 1

    # Instance metadata object
    sds_meta = metadata.SdsMetadata()

    # Printout list of intermediate files
    my_logger.info('In ingest_file_vers_1_0: Input file: %s' % input_file)

    # -------------------------------------------------------------------------
    # Collect info and prepare filenaming
    # -------------------------------------------------------------------------

    # # Get information from product_in_info
    #
    in_scale_factor = product_in_info['scale_factor']
    in_offset = product_in_info['scale_offset']
    in_nodata = product_in_info['no_data']
    in_mask_min = product_in_info['mask_min']
    in_mask_max = product_in_info['mask_max']
    in_data_type = product_in_info['data_type_id']
    in_data_type_gdal = conv_data_type_to_gdal(in_data_type)

    # Get information from 'product' table
    args = {"productcode": product_def['productcode'], "subproductcode": product_def['subproductcode'], "version":product_def['version']}
    product_info = querydb.get_product_out_info(**args)
    product_info = functions.list_to_element(product_info)

    out_data_type = product_info.data_type_id
    out_scale_factor = product_info.scale_factor
    out_offset = product_info.scale_offset
    out_nodata = product_info.nodata
    out_date_format = product_info.date_format

    # Translate data type for gdal and numpy
    out_data_type_gdal = conv_data_type_to_gdal(out_data_type)
    out_data_type_numpy = conv_data_type_to_numpy(out_data_type)

    # Copy the in_date format into a convenient one for DB and file naming
    # No change done FTTB !
    out_date_str_final = in_date

    # Get only the short_name for output file naming
    mapset_id = target_mapset

    # Define output directory and make sure it exists
    output_directory = data_dir_out + functions.set_path_sub_directory(product_def['productcode'],
                                                                       product_def['subproductcode'],
                                                                       product_def['type'],
                                                                       product_def['version'],
                                                                       mapset_id,)
    my_logger.debug('Output Directory is: %s' % output_directory)
    try:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
    except:
        my_logger.error('Cannot create output directory: ' + output_directory)
        return 1

    # Define output filename
    output_filename = output_directory + functions.set_path_filename(out_date_str_final,
                                                                     product_def['productcode'],
                                                                     product_def['subproductcode'],
                                                                     mapset_id,
                                                                     product_def['version'],
                                                                     '.tif')

    # -------------------------------------------------------------------------
    # Manage the geo-referencing associated to input file
    # -------------------------------------------------------------------------

    orig_ds = gdal.Open(input_file, gdal.GA_ReadOnly)

    # Go straight for the case of 'default' mapset
    try:
        # Read geo-reference from input file
        orig_cs = osr.SpatialReference()
        orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
        orig_geo_transform = orig_ds.GetGeoTransform()
        orig_size_x = orig_ds.RasterXSize
        orig_size_y = orig_ds.RasterYSize
    except:
        my_logger.debug('Cannot read geo-reference from file .. Continue')

    # TODO-M.C.: add a test on the mapset id in DB table !
    trg_mapset = mapset.MapSet()
    trg_mapset.assigndb(mapset_id)
    logger.debug('Target Mapset is: %s' % mapset_id)
    reprojection = 0

    # -------------------------------------------------------------------------
    # Generate the output file
    # -------------------------------------------------------------------------
    # Prepare output driver
    out_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)

    # Write to GTIFF file
    try:
        my_logger.debug('Doing only rescaling/format conversion')

        # Read from input file
        band = orig_ds.GetRasterBand(1)
        my_logger.debug('Band Type='+gdal.GetDataTypeName(band.DataType))
        out_data = band.ReadAsArray(0, 0, orig_size_x, orig_size_y)

        # No reprojection, only format-conversion
        trg_ds = out_driver.Create(output_filename, orig_size_x, orig_size_y, 1, out_data_type_gdal,
                                   [es_constants.ES2_OUTFILE_OPTIONS])
        trg_ds.SetProjection(orig_ds.GetProjectionRef())
        trg_ds.SetGeoTransform(orig_geo_transform)

        # Apply rescale to data
        scaled_data = rescale_data(out_data, in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max,
                                   out_data_type_numpy, out_scale_factor, out_offset, out_nodata, my_logger, "linear")

        trg_ds.GetRasterBand(1).WriteArray(scaled_data)

        orig_ds = None

    except:
        my_logger.error('Error in writing output file [%s]' % output_filename)

    # -------------------------------------------------------------------------
    # Assign Metadata to the ingested file
    # -------------------------------------------------------------------------

    sds_meta.assign_es2_version()
    sds_meta.assign_mapset(mapset_id)
    sds_meta.assign_from_product(product_def['productcode'], product_def['subproductcode'], product_def['version'])
    sds_meta.assign_date(out_date_str_final)
    sds_meta.assign_subdir_from_fullpath(output_directory)
    sds_meta.assign_compute_time_now()
    sds_meta.assign_input_files(input_file)

    sds_meta.write_to_ds(trg_ds)
    trg_ds = None
    out_driver = None


def ingest_file_archive(input_file, target_mapsetid, echo_query=False, no_delete=False):
# -------------------------------------------------------------------------------------------------------
#   Ingest a file of type MESA_JRC_
#   Arguments:
#       input_file: input file full name
#       target_mapset: target mapset
#       no_delete: do not delete input file (for external medium)
#
#   Since 30/10/17: manages .zipped files, ending with extension .gz.tif (see ES2-96)
#

    logger.info("Entering routine %s for file %s" % ('ingest_file_archive', input_file))
    extension='.tif'

    # Test the file/files exists
    if not os.path.isfile(input_file):
        logger.error('Input file: %s does not exist' % input_file)
        return 1

    # Create temp output dir for unzipping (since release 2.1.1 - for wd-gee products)
    if re.match(es_constants.es2globals['prefix_eumetcast_files'] + '.*.gz.tif', os.path.basename(input_file)):
        try:
            tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(input_file),
                                      dir=es_constants.base_tmp_dir)
        except:
            logger.error('Cannot create temporary dir ' + es_constants.base_tmp_dir + '. Exit')
            raise NameError('Error in creating tmpdir')

        # unzip the file
        output_filename = os.path.basename(input_file).replace('gz.tif','tif')

        command='gunzip -c '+input_file+' > '+tmpdir+os.path.sep+output_filename
        try:
            os.system(command)
        except:
            logger.error('Cannot gunzip file ' + os.path.basename(input_file) + '. Exit')
            raise NameError('Error in unzipping file')

        my_input_file = tmpdir+os.path.sep+output_filename
        b_unzipped = True
        extension = '.gz.tif'
    else:
        my_input_file = input_file
        b_unzipped = False
        extension = '.tif'

    # Instance metadata object (for output_file)
    sds_meta_out = metadata.SdsMetadata()

    # Read metadata from input_file
    sds_meta_in = metadata.SdsMetadata()
    sds_meta_in.read_from_file(my_input_file)

    # Extract info from input file
    if re.match(es_constants.es2globals['prefix_eumetcast_files']+'.*.tif', os.path.basename(input_file)):
        [str_date, product_code, sub_product_code, mapsetid, version] = functions.get_all_from_filename_eumetcast(my_input_file)
    else:
        [str_date, product_code, sub_product_code, mapsetid, version] = functions.get_all_from_filename(my_input_file)

    # Define output filename
    sub_dir = sds_meta_in.get_item('eStation2_subdir')
    product_type = functions.get_product_type_from_subdir(sub_dir)


    if re.match(es_constants.es2globals['prefix_eumetcast_files'] + '.*.tif', os.path.basename(input_file)):
        output_file = es_constants.es2globals['processing_dir']+ \
                          functions.convert_name_from_eumetcast(my_input_file, product_type, with_dir=True, new_mapset=target_mapsetid)
    else:
        output_file = es_constants.es2globals['processing_dir'] + \
                      functions.convert_name_from_archive(my_input_file, product_type, with_dir=True,
                                                            new_mapset=target_mapsetid)

    # make sure output dir exists
    output_dir = os.path.split(output_file)[0]
    functions.check_output_dir(output_dir)

    # Compare input-target mapset
    if target_mapsetid==mapsetid:

        # Check if the target file exist ... and delete it in case
        if os.path.isfile(output_file):
            os.remove(output_file)
        # Copy file to output
        shutil.copyfile(my_input_file,output_file)
        # Open output dataset for writing metadata
        #trg_ds = gdal.Open(output_file)

    else:

        # -------------------------------------------------------------------------
        # Manage the geo-referencing associated to input file
        # -------------------------------------------------------------------------
        orig_ds = gdal.Open(my_input_file, gdal.GA_ReadOnly)

        # Read the data type
        band = orig_ds.GetRasterBand(1)
        out_data_type_gdal = band.DataType
        try:
            # Read geo-reference from input file
            orig_cs = osr.SpatialReference()
            orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
            orig_geo_transform = orig_ds.GetGeoTransform()
            orig_size_x = orig_ds.RasterXSize
            orig_size_y = orig_ds.RasterYSize
        except:
            logger.debug('Cannot read geo-reference from file .. Continue')

        # TODO-M.C.: add a test on the mapset-id in DB table !
        trg_mapset = mapset.MapSet()
        trg_mapset.assigndb(target_mapsetid)
        logger.debug('Target Mapset is: %s' % target_mapsetid)

        # -------------------------------------------------------------------------
        # Generate the output file
        # -------------------------------------------------------------------------
        # Prepare output driver
        out_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)

        logger.debug('Doing re-projection to target mapset: %s' % trg_mapset.short_name)
        # Get target SRS from mapset
        out_cs = trg_mapset.spatial_ref
        out_size_x = trg_mapset.size_x
        out_size_y = trg_mapset.size_y

        # Create target in memory
        mem_driver = gdal.GetDriverByName('MEM')

        # Assign mapset to dataset in memory
        mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, out_data_type_gdal)

        mem_ds.SetGeoTransform(trg_mapset.geo_transform)
        mem_ds.SetProjection(out_cs.ExportToWkt())

        # Apply Reproject-Image to the memory-driver
        orig_wkt = orig_cs.ExportToWkt()
        res = gdal.ReprojectImage(orig_ds, mem_ds, orig_wkt, out_cs.ExportToWkt(),
                                      es_constants.ES2_OUTFILE_INTERP_METHOD)

        logger.debug('Re-projection to target done.')

        # Read from the dataset in memory
        out_data = mem_ds.ReadAsArray()

        # Write to output_file
        trg_ds = out_driver.CreateCopy(output_file, mem_ds, 0, [es_constants.ES2_OUTFILE_OPTIONS])
        trg_ds.GetRasterBand(1).WriteArray(out_data)

    # -------------------------------------------------------------------------
    # Assign Metadata to the ingested file
    # -------------------------------------------------------------------------
    # Close dataset
    trg_ds = None
    out_driver = None

    sds_meta_out.assign_es2_version()
    sds_meta_out.assign_mapset(target_mapsetid)
    sds_meta_out.assign_from_product(product_code, sub_product_code, version)
    sds_meta_out.assign_date(str_date)
    sds_meta_out.assign_subdir_from_fullpath(output_dir)
    sds_meta_out.assign_compute_time_now()
    sds_meta_out.assign_input_files(my_input_file)

    # Write metadata to file
    sds_meta_out.write_to_file(output_file)

    # -------------------------------------------------------------------------
    # Create a file for deleting from ingest (at the end)
    # -------------------------------------------------------------------------

    working_dir=es_constants.es2globals['base_tmp_dir']+os.path.sep+'ingested_files'
    functions.check_output_dir(working_dir)
    if no_delete == False:
        trace_file=working_dir+os.path.sep+os.path.basename(input_file)+'.tbd'
        logger.debug('Trace for deleting ingested file %s' % trace_file)
        with open(trace_file, 'a'):
            os.utime(trace_file, None)
    else:
        logger.debug('Do not delete ingest file.')

    # Remove temp dir
    if b_unzipped:
        shutil.rmtree(tmpdir)


def write_ds_to_geotiff(dataset, output_file):
#
#   Writes to geotiff file an osgeo.gdal.Dataset object
#   Args:
#       dataset: osgeo.gdal dataset (open and georeferenced)
#       output_file: target output file
#   Usage: e.g. for converting MODIS HDF4 tiled SDS to temporary  geotiff files
#
#   TODO-M.C.: add checks on the input dataset
#
    # Read from input ds
    orig_cs = osr.SpatialReference()
    orig_cs.ImportFromWkt(dataset.GetProjectionRef())
    orig_geo_transform = dataset.GetGeoTransform()
    orig_size_x = dataset.RasterXSize
    orig_size_y = dataset.RasterYSize
    band = dataset.GetRasterBand(1)
    data = band.ReadAsArray(0, 0, orig_size_x, orig_size_y)
    # Read the native data type of the band
    in_data_type = band.DataType
    gdt_type = conv_data_type_to_gdal(in_data_type)

    # Create and write output file
    output_driver = gdal.GetDriverByName('GTiff')
    output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
    output_ds.SetProjection(dataset.GetProjectionRef())
    output_ds.SetGeoTransform(orig_geo_transform)
    output_ds.GetRasterBand(1).WriteArray(data)

    output_ds = None


def write_ds_and_mapset_to_geotiff(dataset, mapset, output_file):
#
#   Writes to geotiff file an osgeo.gdal.Dataset object
#   Args:
#       dataset: osgeo.gdal dataset (open and georeferenced)
#       mapset: 'native' mapset to be assigned to the output
#       output_file: target output file
#
#   Usage: e.g. for 'geo-referencing' TAMSAT data, while writing them to geotiff format
#
#
    # Read info from input mapset
    orig_geo_transform = mapset.geo_transform
    orig_size_x = mapset.size_x
    orig_size_y = mapset.size_y

    # Read data from dataset
    band = dataset.GetRasterBand(1)
    data = band.ReadAsArray(0, 0, orig_size_x, orig_size_y)

    # Read the native data type of the band
    in_data_type = band.DataType

    # Create and write output file
    output_driver = gdal.GetDriverByName('GTiff')
    output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
    output_ds.SetProjection(mapset.spatial_ref.ExportToWkt())
    output_ds.SetGeoTransform(orig_geo_transform)
    output_ds.GetRasterBand(1).WriteArray(data)

    output_ds = None
    dataset = None


def mosaic_lsasaf_msg(in_files, output_file, format):
#
#   Puts together the LSASAF regions (in the original 'disk' projection)
#   Args:
#       in_files: input filenames
#       output_file: target output file
#
   # Note: noData==-1 for LSASAF Products (both ET and LST)
    NO_DATA_LSASAF_PRODS = -1

    # definitions: Euro, NAfr, SAfr, Same -> MUST match with filenaming
    # as defined in SAF/LAND/MF/PUM_AL/1.4, version 1.4, date 15/12/2006
    # on table 4, page 33
    # positions in the array start counting at 1
    # TODO-LinkIT: improve efficiency

    regions_rois = {'Euro': [1550, 3250, 50, 700],
                    'NAfr': [1240, 3450, 700, 1850],
                    'SAfr': [2140, 3350, 1850, 3040],
                    'Same': [40, 740, 1460, 2970],
                    'MSG-Disk': [1, 3712, 1, 3712]}

    pattern = 'Euro|NAfr|SAfr|Same|MSG-Disk'

    roi_view = [1, 3712, 1, 3712]
    out_ns = roi_view[1] - roi_view[0] + 1
    out_nl = roi_view[3] - roi_view[2] + 1

    # open files
    fid = []
    regions = []
    data_type_ref = None

    for ifile in in_files:
        if ifile != '':
            # Open and append to list
            fidin = gdal.Open(ifile, gdal.GA_ReadOnly)
            fid.append(fidin)
            # Find the region and append to list
            region = re.search(pattern, ntpath.basename(ifile))
            regions.append(region.group(0))
            # Check data type
            dataType = fidin.GetRasterBand(1).DataType
            if data_type_ref is None:
                data_type_ref = dataType
            elif data_type_ref != dataType:
                print ("Files do not have the same type!")
                return 1

    # output matrix dimensions
    dataOut = N.zeros((out_ns, out_nl)) + NO_DATA_LSASAF_PRODS

    # total lines
    totallines = 0
    for ii in fid:
        totallines = totallines + ii.GetRasterBand(1).YSize
    accumlines = 0

    for ii in range(len(fid)):
        ipos = ifile[ii]
        inH = fid[ii].GetRasterBand(1)
        dataIn = inH.ReadAsArray(0, 0, inH.XSize, inH.YSize)
        my_roi = regions_rois[regions[ii]]
        logger.debug('Processing Region: ' + regions[ii])

        initCol = my_roi[0] - 1
        lastCol = my_roi[1] - 1
        initLine = my_roi[2] - 1
        lastLine = my_roi[3] - 1

        for il in range(inH.YSize):
            for ix in range(inH.XSize):
                try:
                    dataOut[initLine + il][initCol + ix] = dataIn[il][ix]
                except:
                    print((initCol + ix, initLine + il))

        accumlines = accumlines + inH.YSize

    # instantiate output file
    out_driver = gdal.GetDriverByName('GTiff')
    out_ds = out_driver.Create(output_file, out_ns, out_nl, 1, dataType, [es_constants.ES2_OUTFILE_OPTIONS])

    # assume only 1 band
    outband = out_ds.GetRasterBand(1)
    outband.WriteArray(N.array(dataOut), 0, 0)


def rescale_data(in_data, in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max, out_data_type,
                 out_scale_factor, out_offset, out_nodata, my_logger, in_scale_type):
#
#   Format/scale the output data taking into account input/output properties
#   Args:
#       in_data: input data array (numpy array)
#       in_scale_factor: scale factor to be applied to input data
#       in_offset: offset to be applied to input data
#           Note: PhysVal = DN * scale_factor + offset
#
#       in_nodata: nodata value applied to input data
#       in_mask_min: min range of values not to be converted to physical values
#                    In the output, it is converted to nodata
#       in_mask_max: max range of values not to be converted to physical values
#                    In the output, it is converted to nodata
#       out_data_type: output data type (byte, int16, uint16, ...)
#       out_scale_factor: scale factor applied to the output
#       out_offset: offset applied to the output -> should be 0
#           Note: PhysVal = NumValue * scale_factor + offset
#
#       out_nodata: output nodata (should depend on out_data_type only)
#
#   Returns: output data
#

    # Check input
    if not isinstance(in_data, N.ndarray):
        my_logger.error('Input argument must be a numpy array. Exit')
        return 1

    # Create output array
    trg_data = N.zeros(in_data.shape, dtype=out_data_type)

    # Get position of input nodata
    if in_nodata is not None:
        idx_nodata = (in_data == in_nodata)
    else:
        idx_nodata = N.zeros(1, dtype=bool)

    # Get position of values exceeding in_mask_min value
    if in_mask_min is not None:
        idx_mask_min = (in_data <= in_mask_min)
    else:
        idx_mask_min = N.zeros(1, dtype=bool)

    # Get position of values below in_mask_max value
    if in_mask_max is not None:
        idx_mask_max = (in_data >= in_mask_max)
    else:
        idx_mask_max = N.zeros(1, dtype=bool)

    # # ES2-385 If input scale factor , offset and output scale factor, offsets are the same then return trg_data as in_data
    if in_scale_factor == out_scale_factor and in_offset == out_offset:
        trg_data = in_data
        my_logger.info('Skip rescaling because input scale factor , offset and output scale factor, offsets are the same')

        # Assign output nodata to in_nodata and mask range
        if idx_nodata.any():
            trg_data[idx_nodata] = out_nodata

        if idx_mask_min.any():
            trg_data[idx_mask_min] = out_nodata

        if idx_mask_max.any():
            trg_data[idx_mask_max] = out_nodata

        return trg_data

    # Check if input rescaling has to be done
    if in_scale_factor != 1 or in_offset != 0:
        phys_value = in_data * in_scale_factor + in_offset
    else:
        phys_value = in_data

    if in_scale_type=='log10':
        phys_value =  N.power(10,phys_value)

    # Assign to the output array
    # Option 2: ES2-385 Check if Output rescaling has to be done
    if out_scale_factor != 1 or out_offset != 0:
        # trg_data = old_div((phys_value - out_offset), out_scale_factor)
        trg_data = (phys_value - out_offset)/ out_scale_factor
    else:
        trg_data = phys_value

    # Assign output nodata to in_nodata and mask range
    if idx_nodata.any():
        trg_data[idx_nodata] = out_nodata

    if idx_mask_min.any():
        trg_data[idx_mask_min] = out_nodata

    if idx_mask_max.any():
        trg_data[idx_mask_max] = out_nodata

    # Return the output array

    return trg_data

#
# Converts the string data type to numpy types
# type: "data type in wkt-estation format (inherited from 1.X)"
# Refs. see e.g. http://docs.scipy.org/doc/numpy/user/basics.types.html
#
def conv_data_type_to_numpy(type):
    if type == 'Byte':
        return 'int8'
    elif type == 'Int16':
        return 'int16'
    elif type == 'UInt16':
        return 'uint16'
    elif type == 'Int32':
        return 'int32'
    elif type == 'UInt32':
        return 'uint32'
    elif type == 'Float32':
        return 'float32'
    elif type == 'Float64':
        return 'float64'
    elif type == 'CFloat64':
        return 'complex64'
    else:
        return 'int16'

#
#   Converts the string data type to GDAL types
#   type: data type in wkt-estation format (inherited from 1.X)
#   Refs. see: http://www.gdal.org/gdal_8h.html
#
def conv_data_type_to_gdal(type):
    if type == 'Byte':
        return gdal.GDT_Byte
    elif type == 'Int16':
        return gdal.GDT_Int16
    elif type == 'UInt16':
        return gdal.GDT_UInt16
    elif type == 'Int32':
        return gdal.GDT_Int32
    elif type == 'UInt32':
        return gdal.GDT_UInt32
    elif type == 'Float32':
        return gdal.GDT_Float32
    elif type == 'Float64':
        return gdal.GDT_Float64
    elif type == 'CFloat64':
        return gdal.GDT_CFloat64
    else:
        return gdal.GDT_Int16

