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

python_version = sys.version_info[0]

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
        subproduct = subproducts[ii]['subproduct']
        # Get only the short_name for output file naming
        mapset_id = subproducts[ii]['mapsetcode']
        # Get information from sub_dataset_source table
        product_in_info = get_product_in_info(product, subproduct, datasource_descr.datasource_descr_id, my_logger)

        # Check if the scaling has been read/save to .tmp dir (MC. 26.7.2016: Issue for MODIS SST .nc files)
        try:
            [in_scale_factor, in_offset] = functions.read_netcdf_scaling(intermFile)
        except:
            # Take from DB
            in_scale_factor = product_in_info.scale_factor
            in_offset = product_in_info.scale_offset

        in_data_type_gdal = conv_data_type_to_gdal(product_in_info.data_type_id)

        # Get information from 'product' table
        product_out_info = get_product_out_info(product, subproduct, my_logger)

        # Translate data type for gdal and numpy
        out_data_type_gdal = conv_data_type_to_gdal(product_out_info.data_type_id)
        out_data_type_numpy = conv_data_type_to_numpy(product_out_info.data_type_id)
        out_date_str_final = define_output_data_format(datasource_descr, in_date, product_out_info.date_format)

        # Define outputfilename, output directory and make sure it exists
        output_directory, output_filename = define_output_dir_filename(product, subproduct, mapset_id, out_date_str_final, my_logger)
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

        # Only_metadata_naming= only_metadata_naming()
        if not native_mapset.is_wbd():
          #   Get Georeferencing parameters
          orig_cs, orig_geo_transform, orig_size_x, orig_size_y = get_geo_ref_parameters(native_mapset_code, native_mapset, orig_ds, my_logger)

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
        merge_existing_output = os.path.isfile(output_filename) and datasource_descr.area_type in ['tile','region'] and not trg_mapset.is_wbd()
        my_output_filename = output_filename   #This means you are creating files directly on the file dir
        old_file_list = None
        tmp_output_file = None
        # Get old_file list
        if merge_existing_output:
            old_file_list = get_old_file_list(output_filename, my_logger)
            # In case of merge, output_filename is generated first in 'tmp_dir', otherwise in final dir
            my_output_filename = tmp_dir + os.path.sep + os.path.basename(output_filename)
            # Prepare a tmp file in tmp_dir (for merging)
            tmp_output_file = tmp_dir + os.path.sep + os.path.basename(output_filename) + '.tmp'
        # Do re-projection, or write to GTIFF file
        if not native_mapset.is_wbd():
          if reprojection == 1:
            # Do Reprojection
            out_data, out_ds = do_reprojection(trg_mapset, in_data_type_gdal, product_out_info.nodata, out_data_type_gdal, orig_cs, orig_ds, my_logger)

            # Apply rescale to data
            scaled_data = rescale_data(out_data, in_scale_factor, in_offset, product_in_info, product_out_info, out_data_type_numpy, my_logger)

            # Create a copy to output_file
            trg_ds = out_driver.CreateCopy(my_output_filename, out_ds, 0, [es_constants.ES2_OUTFILE_OPTIONS])
            trg_ds.GetRasterBand(1).WriteArray(scaled_data)
            trg_ds = None
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
            scaled_data = rescale_data(out_data, in_scale_factor, in_offset, product_in_info, product_out_info, out_data_type_numpy, my_logger)
            trg_ds.GetRasterBand(1).WriteArray(scaled_data)

            orig_ds = None
            trg_ds = None

        out_driver = None
        # Check not WD-GEE
        if not trg_mapset.is_wbd():
            # Write metadata, if not merging is needed
            if not merge_existing_output:
                final_list_files = in_files
                file_write_metadata = my_output_filename

            else:
                final_list_files = merge_files_to_existings(in_files, product_out_info.nodata, old_file_list, tmp_output_file, my_output_filename, output_filename, my_logger)
                # Save the .tmp as output
                if os.path.isfile(output_filename):
                    os.remove(output_filename)
                shutil.move(tmp_output_file, output_filename)
                file_write_metadata = output_filename
        # WD-GEE case
        else:
            final_list_files = in_files         #+ [intermFile]       #[in_files, os.path.basename(intermFile)]
            file_write_metadata = output_filename
            shutil.move(intermFile,output_filename)  # TODO why just copy? should be move like in other cases


        # -------------------------------------------------------------------------
        # Assign Metadata to the ingested file
        # -------------------------------------------------------------------------
        # Instance metadata object

        assign_metadata_generic(product, subproduct, mapset_id, out_date_str_final, output_directory, final_list_files, file_write_metadata,my_logger)

        # -------------------------------------------------------------------------
        # Upsert into DB table 'products_data'
        # -------------------------------------------------------------------------

        filename = os.path.basename(output_filename)
        # Loop on interm_files
        ii += 1

def get_product_in_info(product, subproduct, datasource_descr_id, my_logger):
    try:
        # Get information about the dataset
        args = {"productcode": product['productcode'],
                "subproductcode": subproduct,
                "datasource_descr_id": datasource_descr_id,
                "version": product['version']}

        # Get information from sub_dataset_source table
        product_in_info = querydb.get_product_in_info(**args)

        return product_in_info
    except:
        my_logger.error('Error defining Input product info ')


def get_product_out_info(product, subproduct, my_logger):
    try:
        # Get information from 'product' table
        args = {"productcode": product['productcode'], "subproductcode": subproduct, "version":product['version']}
        product_out_info = querydb.get_product_out_info(**args)
        product_out_info = functions.list_to_element(product_out_info)
        return product_out_info
    except:
        my_logger.error('Error defining Output product info ')

def define_output_dir_filename(product, subproduct, mapset_id, out_date_str_final, my_logger):
    try:
        output_directory = data_dir_out + functions.set_path_sub_directory(product['productcode'],
                                                                           subproduct,
                                                                           'Ingest',
                                                                           product['version'],
                                                                           mapset_id, )
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
                                                                         subproduct,
                                                                         mapset_id,
                                                                         product['version'],
                                                                         '.tif')
        return output_directory, output_filename

    except:
        my_logger.error('Error defining output filename and directory ')
        return 1

def get_geo_ref_parameters(native_mapset_code, native_mapset, orig_ds, my_logger):
    try:
        if native_mapset_code != 'default':
          orig_cs = osr.SpatialReference(wkt=native_mapset.spatial_ref.ExportToWkt())
          #orig_cs.ImportFromWkt(native_mapset.spatial_ref)                     # ???
          orig_geo_transform = native_mapset.geo_transform
          orig_size_x = native_mapset.size_x
          orig_size_y = native_mapset.size_y
          #
          # # Complement orig_ds info (necessary to Re-project)
          # try:
          #     orig_ds.SetGeoTransform(native_mapset.geo_transform)
          #     orig_ds.SetProjection(orig_cs.ExportToWkt())
          # except:
          #     my_logger.debug('Cannot set the geo-projection .. Continue')
          # my_logger.debug('Not assigning native mapset here')
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

        return orig_cs, orig_geo_transform, orig_size_x, orig_size_y
    except:
        my_logger.debug('Error in getting or assigning geo-reference parameters')

def get_old_file_list(output_filename, my_logger):
    try:
        # Check if the output file already exists
        sds_meta_old = metadata.SdsMetadata()
        sds_meta_old.read_from_file(output_filename)
        old_file_list = sds_meta_old.get_item('eStation2_input_files')
        sds_meta_old = None
        return old_file_list

    except:
        my_logger.debug('Error in getting old file metadata ')

# Merge to existing file if any return and return the final list of files used to write to metadata.
def merge_files_to_existings(in_files, out_nodata, old_file_list, tmp_output_file, my_output_filename, output_filename, my_logger):
    final_list = in_files
    # Merge the old and new output products into a 'tmp' file
    try:
        command = es_constants.gdal_merge + ' -n ' + str(out_nodata)
        command += ' -a_nodata ' + str(out_nodata)
        command += ' -of GTiff '
        command += ' -co \"compress=lzw\" -o '
        command += tmp_output_file
        command += ' ' + my_output_filename + ' ' + output_filename
        my_logger.debug('Command for merging is: ' + command)
        os.system(command)
    except:
        pass  # TODO Should change this approach

    # Write metadata to output
    if old_file_list is not None:
        # Merge the old and new file list (note that old list is a string !)
        final_list = merge_input_file_lists(old_file_list, in_files)

    return final_list


# TODO Should move it to functions
def merge_input_file_lists(old_list, input_files):
    #   Merge new list to the existing one (which is a string)

    true_list = old_list.split(';')
    true_list_not_empty = []
    for elem in true_list:
        if elem != '':
            true_list_not_empty.append(os.path.basename(elem))
    for infile in input_files:
        if not infile in true_list_not_empty:
            true_list_not_empty.append(os.path.basename(infile))
    return true_list_not_empty

def define_output_data_format(datasource_descr, in_date, out_date_format):
    # Convert the in_date format into a convenient one for DB and file naming
    # (i.e YYYYMMDD or YYYYMMDDHHMM)
    # Initialize to error value
    output_date_str = -1

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
        output_date_str = str(in_date) + '01'

    if datasource_descr.date_format == 'YYYY_DK':
        # The date (e.g. 2020_36) is converted to the dekad it belongs to (e.g. 20201221)
        output_date_str = functions.conv_yyyydk_2_yyyymmdd(in_date)

    if output_date_str == -1:
        out_date_str_final = in_date + '_DATE_ERROR_'
    else:
        if out_date_format == 'YYYYMMDDHHMM':
            if functions.is_date_yyyymmddhhmm(output_date_str):
                out_date_str_final = output_date_str
            elif functions.is_date_yyyymmdd(output_date_str):
                out_date_str_final = output_date_str + '0000'
        elif out_date_format == 'YYYYMMDD':
            if functions.is_date_yyyymmdd(output_date_str):
                out_date_str_final = output_date_str
            elif functions.is_date_yyyymmddhhmm(output_date_str):
                out_date_str_final = output_date_str[0:8]
        elif out_date_format == 'MMDD':
            if functions.is_date_mmdd(output_date_str):
                out_date_str_final = output_date_str

    return out_date_str_final

# -------------------------------------------------------------------------
# Do Reprojection
# -------------------------------------------------------------------------
def do_reprojection(trg_mapset, in_data_type_gdal, out_nodata, out_data_type_gdal, orig_cs,orig_ds, my_logger):
    try:
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
        # mem_ds.GetRasterBand(1).Fill(in_nodata)  #ES2-595
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
        # # Apply rescale to data
        # scaled_data = rescale_data(out_data, in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max,
        #                            out_data_type_numpy, out_scale_factor, out_offset, out_nodata, my_logger,
        #                            in_scale_type)
        #
        # # Create a copy to output_file
        # trg_ds = out_driver.CreateCopy(my_output_filename, out_ds, 0, [es_constants.ES2_OUTFILE_OPTIONS])
        # trg_ds.GetRasterBand(1).WriteArray(scaled_data)
        return out_data, out_ds
    except:
        my_logger.debug('Error in Reprojection')


# -------------------------------------------------------------------------
# Assign generic Metadata to the ingested file  TODO can we generate these parameters from the full file name with dir
# -------------------------------------------------------------------------
def assign_metadata_generic(product, subproduct, mapset_id, out_date_str_final, output_directory, final_list_files,file_write_metadata, my_logger):
    try:
        sds_meta = metadata.SdsMetadata()
        sds_meta.assign_es2_version()
        sds_meta.assign_mapset(mapset_id)
        sds_meta.assign_from_product(product['productcode'], subproduct, product['version'])
        sds_meta.assign_date(out_date_str_final)
        sds_meta.assign_subdir_from_fullpath(output_directory)
        sds_meta.assign_compute_time_now()

        sds_meta.assign_input_files(final_list_files)
        sds_meta.write_to_file(file_write_metadata)
    except:
        my_logger.debug('Cannot read geo-reference from file .. Continue')

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

    sds_meta_out.assign_es2_version()
    sds_meta_out.assign_mapset(target_mapsetid)
    sds_meta_out.assign_from_product(product_code, sub_product_code, version)
    sds_meta_out.assign_date(str_date)
    sds_meta_out.assign_subdir_from_fullpath(output_dir)
    sds_meta_out.assign_comput_time_now()
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


def rescale_data(in_data, in_scale_factor, in_offset, product_in_info, product_out_info, out_data_type, my_logger):
#
#   Format/scale the output data taking into account input/output properties
#   Args:
#       in_data: input data array (numpy array)
#       in_scale_factor: scale factor to be applied to input data
#       in_offset: offset to be applied to input data
#           Note: PhysVal = DN * scale_factor + offset
#       product_in_info  --
#       product_out_info
#       in_nodata: nodata value applied to input data   New approach - obtained from product_in_info
#       in_mask_min: min range of values not to be converted to physical values   New approach - obtained from product_in_info
#                    In the output, it is converted to nodata
#       in_mask_max: max range of values not to be converted to physical values   New approach - obtained from product_in_info
#                    In the output, it is converted to nodata
#       out_data_type: output data type (byte, int16, uint16, ...) New approach - obtained from product_out_info
#       out_scale_factor: scale factor applied to the output    New approach - obtained from product_out_info
#       out_offset: offset applied to the output -> should be 0  New approach - obtained from product_out_info
#           Note: PhysVal = NumValue * scale_factor + offset
#
#       out_nodata: output nodata (should depend on out_data_type only)
#
#   Returns: output data
#
    in_scale_type = product_in_info.scale_type
    in_nodata = product_in_info.no_data
    in_mask_min = product_in_info.mask_min
    in_mask_max = product_in_info.mask_max
    in_data_type = product_in_info.data_type_id

    # out_data_type = product_out_info.data_type_id
    out_scale_factor = product_out_info.scale_factor
    out_offset = product_out_info.scale_offset
    out_nodata = product_out_info.nodata
    out_date_format = product_out_info.date_format

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
        trg_data = (phys_value - out_offset) / out_scale_factor
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
#   Converts the string data type to numpy types
#  \ type: data type in wkt-estation format (inherited from 1.X)
#   Refs. see e.g. http://docs.scipy.org/doc/numpy/user/basics.types.html
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

