from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
#
#	purpose: Define the ingest service
#	author:  Vijay Charan & M.Clerici & Jurriaan van't Klooster
#	date:	 September 2020
#   descr:
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
import glob
import os
import time, datetime
import time
import shutil
import sys
# import eStation2 modules
from database import querydb
from lib.python import functions
from lib.python import es_logging as log

from config import es_constants
from apps.processing import proc_functions
from apps.productmanagement import products

logger = log.my_logger(__name__)

ingest_dir_in = es_constants.ingest_dir
ingest_error_dir = es_constants.ingest_error_dir
data_dir_out = es_constants.processing_dir

python_version = sys.version_info[0]

def loop_ingestion(dry_run=False, test_one_product=None):

#    Driver of the ingestion process
#    Reads configuration from the database
#    Reads the list of files existing in input directory
#    Loops over file and call the ingestion script
#    Arguments: dry_run -> if 1, read tables and report activity ONLY

    logger.info("Entering routine %s" % 'drive_ingestion')

    while True:

        # Manage the ingestion of Historical Archives (e.g. eStation prods disseminated via EUMETCast - MESA_JRC_*.tif)
        # try:
        #     status = ingest_archives_eumetcast(dry_run=dry_run)
        # except:
        #     logger.error("Error in executing ingest_archives_eumetcast")
        loop_ingestion_drive(dry_run=False, test_one_product=None)

        # Wait at the end of the loop
        logger.info("Entering sleep time of  %s seconds" % str(10))
        time.sleep(10)

def loop_ingestion_drive(dry_run=False, test_one_product=None):
    echo_query = False
    # Get all active product ingestion records with a subproduct count.
    active_product_ingestions = querydb.get_ingestion_product(allrecs=True)

    for active_product_ingest in active_product_ingestions:

        productcode = active_product_ingest[0]
        productversion = active_product_ingest[1]

        # Verify the test-one-product case
        do_ingest_product = is_test_one_product(test_one_product, productcode)

        if do_ingest_product:
            logger.info("Ingestion active for product: [%s] subproduct N. %s" % (active_product_ingest[0],
                                                                                 active_product_ingest[2]))
            # For the current active product ingestion: get all
            product = {"productcode": productcode,
                       "version": productversion}
            logger.debug("Processing product: %s - version %s" % (productcode, productversion))

            # Get the list of acquisition sources that are defined for this ingestion 'trigger'
            # (i.e. prod/version)
            # NOTE: the following implies there is 1 and only 1 '_native' subproduct associated to a 'product';
            native_product = {"productcode": productcode,
                              "subproductcode": productcode + "_native",
                              "version": productversion}

            sources_list = querydb.get_product_sources(**native_product)

            logger.debug("For product [%s] N. %s  source is/are found" % (productcode, len(sources_list)))

            systemsettings = functions.getSystemSettings()

            for source in sources_list:

                logger_spec = log.my_logger('apps.ingestion.' + productcode + '.' + productversion)
                logger.debug("Processing Source type [%s] with id [%s]" % (source.type, source.data_source_id))
                # Re-initialize the datasource_descr
                # datasource_descr = None

                # Get datasource desctiption
                datasource_descr = querydb.get_datasource_descr(source_type=source.type,
                                                                source_id=source.data_source_id)
                datasource_descr = datasource_descr[0]
                # TODO optimize this in order to get direct file filter expression
                my_filter_expr = get_filenaming_info(source, datasource_descr)

                files = get_files_matching_with_file_expression(my_filter_expr)

                # See ES2-204
                logger_spec.debug(
                    "Number of files found for product [%s] is: %s" % (active_product_ingest[0], len(files)))
                if len(files) > 0:
                    # Get list of ingestions triggers [prod/subprod/mapset]
                    ingestions = querydb.get_ingestion_subproduct(allrecs=False, **product)

                    # Loop over ingestion triggers
                    subproducts = list()
                    for ingest in ingestions:
                        # TODO if one ingest gives true and another false?
                        dates_not_in_filename = is_date_not_in_filename(ingest.input_to_process_re)
                        logger.debug(" --> processing subproduct: %s" % ingest.subproductcode)

                        args = {"productcode": product['productcode'],
                                "subproductcode": ingest.subproductcode,
                                "datasource_descr_id": datasource_descr.datasource_descr_id,
                                "version": product['version']}
                        product_in_info = querydb.get_product_in_info(**args)
                        # TODO verify the approach Should we get subproduct from single query
                        subproduct = get_subproduct(ingest, product_in_info, datasource_descr.datasource_descr_id)
                        if subproduct is not None:
                            subproducts.append(subproduct)

                    if subproducts is None:
                        #TODO what to do?
                        logger.error("For current active ingestion No subproducts for Product [%s] " % (productcode))

                    # Get the list of unique dates by extracting the date from all files.
                    dates_list = get_list_unique_dates(datasource_descr, files, dates_not_in_filename, product_in_info, ingest.mapsetcode)

                    # Loop over dates and get list of files
                    for in_date in dates_list:
                        date_fileslist = get_dates_file_list(dates_not_in_filename, files, my_filter_expr, in_date, logger_spec)
                        # Pass list of files to ingestion routine
                        if (not dry_run):
                            try:
                                result = ingestion(date_fileslist, in_date, product, subproducts, datasource_descr,
                                                   logger_spec, echo_query=echo_query)
                            except:
                                logger.error(
                                    "Error in ingestion of file [%s] " % (functions.conv_list_2_string(date_fileslist)))
                            else:
                                # Result is None means we are still waiting for some files to be received. Keep files in /data/ingest
                                # dates_not_in_filename means the input files contains many dates (e.g. GSOD precip)
                                if result is not None and not dates_not_in_filename:
                                    if source.store_original_data or systemsettings['type_installation'] == 'Server':
                                        store_native_files(product, date_fileslist, logger_spec)
                                    else:
                                        delete_files(date_fileslist, logger_spec)

                        else:
                            time.sleep(10)

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
        composed_file_list = ingestion_pre_process(preproc_type, native_mapset_code, subproducts, input_files, tmpdir, my_logger, in_date, product,
                                                   test_mode)
        # TODO alter this area
        # Error occurred and was detected in pre_process routine
        if str(composed_file_list) == '1':
            my_logger.warning("Error in ingestion for prod: %s and date: %s" % (product['productcode'], in_date))
            # Move files to 'error/storage' directory
            if not test_mode:
                for error_file in input_files:
                    if os.path.isfile(ingest_error_dir + os.path.basename(error_file)):
                        shutil.os.remove(ingest_error_dir + os.path.basename(error_file))
                    try:
                        shutil.move(error_file, ingest_error_dir)
                    except:
                        my_logger.warning("Error in moving file: %s " % error_file)

            shutil.rmtree(tmpdir)
            raise NameError('Detected Error in preprocessing routine')
    else:
        composed_file_list = input_files

    # -------------------------------------------------------------------------
    # Ingest_file
    # -------------------------------------------------------------------------
    ingestion_ingest_file(composed_file_list, in_date, product, subproducts, datasource_descr, my_logger, input_files,
                          echo_query, test_mode, tmpdir)
    # -------------------------------------------------------------------------
    # Remove the Temp working directory
    # -------------------------------------------------------------------------
    try:
        shutil.rmtree(tmpdir)
    except:
        logger.error('Error in removing temporary directory. Continue')
        raise NameError('Error in removing tmpdir')

    return 0


def ingestion_ingest_file(composed_file_list, in_date, product, subproducts, datasource_descr, my_logger, input_files,
                          echo_query, test_mode, tmpdir):
    try:
        from apps.acquisition import ingestion_ingest_file
        ingestion_ingest_file.ingest_file(composed_file_list, in_date, product, subproducts, datasource_descr, my_logger, in_files=input_files,
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

def ingestion_pre_process(preproc_type, native_mapset_code, subproducts, input_files, tmpdir, my_logger, in_date, product, test_mode):
    my_logger.debug("Calling routine %s" % 'preprocess_files')
    try:
        from apps.acquisition import ingestion_pre_process
        composed_file_list = ingestion_pre_process.pre_process_inputs(preproc_type, native_mapset_code, subproducts,
                                                                      input_files, tmpdir,
                                                                      my_logger, in_date=in_date)

        # Pre-process returns None if there are not enough files for continuing
        if composed_file_list is None:
            logger.debug('Waiting for additional files to be received. Return')
            shutil.rmtree(tmpdir)
            return None

        # Check if -1 is returned, i.e. nothing to do on the passed files (e.g. S3A night-files)
        elif composed_file_list is -1:
            logger.debug('Nothing to do on the passed files. Return')
            shutil.rmtree(tmpdir)
            return -1
        # TODO check if this place is fine
        else:
            return composed_file_list
    except:
        # Error occurred and was NOT detected in pre_process routine
        my_logger.warning("Error in ingestion for prod: %s and date: %s" % (product['productcode'], in_date))
        # Move files to 'error/storage' directory (ingest.wrong)
        if not test_mode:
            for error_file in input_files:
                if os.path.isfile(ingest_error_dir + os.path.basename(error_file)):
                    shutil.os.remove(ingest_error_dir + os.path.basename(error_file))
                try:
                    shutil.move(error_file, ingest_error_dir)
                except:
                    my_logger.warning("Error in moving file: %s " % error_file)

        shutil.rmtree(tmpdir)
        raise NameError('Caught Error in preprocessing routine')

def is_date_not_in_filename(input_to_process_re):
    dates_not_in_filename = False
    if input_to_process_re == 'dates_not_in_filename':
        dates_not_in_filename = True

    return dates_not_in_filename

def is_test_one_product(test_one_product=None, productcode=None):

    # Verify the test-one-product case
    do_ingest_source = True
    if test_one_product:
        if productcode != test_one_product:
            do_ingest_source = False

    return do_ingest_source

def get_filenaming_info(source, datasource_descr):
    # Get the 'filenaming' info (incl. 'area-type') from the acquisition source
    if source.type == 'EUMETCAST':

        my_filter_expr = datasource_descr.filter_expression_jrc
        # for eumetcast_filter, datasource_descr in querydb.get_datasource_descr(source_type=source.type,
        #                                                                        source_id=source.data_source_id):
        logger.info("Eumetcast Source: looking for files in %s - named like: %s" % (
            ingest_dir_in, my_filter_expr))

    elif source.type == 'INTERNET':
        # Implement file name filtering for INTERNET data source.
        # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type=source.type,
        #                                                                       source_id=source.data_source_id):
        my_filter_expr = datasource_descr.files_filter_expression
        logger.info("Internet Source: looking for files in %s - named like: %s" % (
            ingest_dir_in, my_filter_expr))

    return my_filter_expr

def get_files_matching_with_file_expression(my_filter_expr):
    files = []
    # Get the 'filenaming' info (incl. 'area-type') from the acquisition source
    files = [os.path.basename(f) for f in glob.glob(ingest_dir_in + '*') if
             re.match(my_filter_expr, os.path.basename(f))]
    return files

#########################################################################################################
###################### Get Subproducts associated with ingestion and datasource #########################
## Goes in error if specific datasource is not associated with subproducts eg. WSI crop & Pasture #######
#########################################################################################################
def get_subproduct(ingest, product_in_info, datasource_descr_id):
    sprod=None
    try:
        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        nodata_value = product_in_info.no_data
        sprod = {'subproduct': ingest.subproductcode,
                 'mapsetcode': ingest.mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': nodata_value}
        # subproducts.append(sprod)
        return sprod
    except:
        # What to return here?
        logger.warning("Subproduct %s not defined for source %s" % (
            ingest.subproductcode, datasource_descr_id))
    finally:
        return sprod

#################################################
#######   Get list unique dates   ###############
#################################################
def get_list_unique_dates(datasource_descr, files, dates_not_in_filename, product_in_info, ingest_mapsetcode ):
    #   Check the case 'dates_not_in_filename' (e.g. GSOD -> yearly files continuously updated)
    dates_list = []
    if dates_not_in_filename:
        # Build the list of dates from datasource description
        dates_list = build_date_list_from_datasource(datasource_descr, product_in_info, ingest_mapsetcode)
    else:
        # Build the list of dates from filenames
        dates_list = build_date_list_from_filenames(files, datasource_descr)

    return dates_list

def get_dates_file_list(dates_not_in_filename, files, my_filter_expr, in_date, logger_spec):
    date_fileslist = []
    if dates_not_in_filename:
        date_fileslist = [ingest_dir_in + l for l in files]
    else:
        # Refresh the files list (some files have been deleted)
        files = [os.path.basename(f) for f in glob.glob(ingest_dir_in + '*') if
                 re.match(my_filter_expr, os.path.basename(f))]
        logger_spec.debug("     --> processing date, in native format: %s" % in_date)
        # Get the list of existing files for that date
        regex = re.compile(".*(" + in_date + ").*")
        date_fileslist = [ingest_dir_in + m.group(0) for l in files for m in [regex.search(l)] if m]

    return date_fileslist

#########################################################################################
#######Build the list of dates from datasource description & Product info ###############
#########################################################################################
def build_date_list_from_datasource(datasource_descr, product_in_info, ingest_mapset):
    dates_list = []

    start_datetime = datetime.datetime.strptime(str(datasource_descr.start_date), "%Y%m%d")
    if datasource_descr.end_date is None:
        end_datetime = datetime.date.today()
    else:
        end_datetime = datetime.datetime.strptime(str(datasource_descr.end_date), "%Y%m%d")

    all_starting_dates = proc_functions.get_list_dates_for_dataset(product_in_info.productcode, \
                                                                   product_in_info.subproductcode, \
                                                                   product_in_info.version, \
                                                                   start_date=datasource_descr.start_date,
                                                                   end_date=datasource_descr.end_date)

    my_dataset = products.Dataset(product_in_info.productcode,
                                  product_in_info.subproductcode,
                                  ingest_mapset,
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

    return dates_list

#########################################################################################
#######      Build the list of dates from datasource description & files  ###############
#########################################################################################
def build_date_list_from_filenames(files, datasource_descr):
    dates_list = []
    for filename in files:
        date_position = int(datasource_descr.date_position)
        if datasource_descr.format_type == 'delimited':
            splitted_fn = re.split(datasource_descr.delimiter, filename)
            date_string = splitted_fn[date_position]
            if len(date_string) > len(datasource_descr.date_format):
                date_string = date_string[0:len(datasource_descr.date_format)]
            dates_list.append(date_string)
        else:
            dates_list.append(
                filename[date_position:date_position + len(datasource_descr.date_format)])

    dates_list = set(dates_list)
    dates_list = sorted(dates_list, reverse=False)

    return dates_list

def store_native_files(product, date_fileslist, logger_spec):
    # Special case for mesa-proc @ JRC
    # Copy to 'Archive' directory
    output_directory = data_dir_out + functions.set_path_sub_directory(
        product['productcode'], None, 'Native', product['version'], 'dummy_mapset_arg')
    functions.check_output_dir(output_directory)
    # Archive the files
    for file_to_move in date_fileslist:
        logger_spec.debug("     --> now archiving input files: %s" % file_to_move)
        new_location = output_directory + os.path.basename(file_to_move)
        try:
            if os.path.isfile(file_to_move):
                shutil.move(file_to_move, new_location)
            else:
                logger_spec.debug("     --> file to be archived cannot be found: %s" % file_to_move)
        except:
            logger_spec.debug("     --> error in archiving file: %s" % file_to_move)

def delete_files(date_fileslist, logger_spec):
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


