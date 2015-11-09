# Helpers for the processing.py and processing_..py

# import standard modules
import datetime
import os
from osgeo import gdal, osr

# import eStation2 modules
from database import querydb
from apps.productmanagement import datasets
from apps.productmanagement import products
from config import es_constants
from lib.python import metadata
from lib.python import functions
from lib.python import mapset
from lib.python import es_logging as log

######################################################################################
#
#   Purpose: for a prod/subprod/version returns a list of date adapted to its frequency and dateformat, and
#
#            start_date |-| end_date        [if both are provided]
#            start_date  -> today           [if only start is provided]
#            None                           [if none is provided]
#
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/02/15
#   Inputs:
#   Output: none
#

def get_list_dates_for_dataset(product_code, sub_product_code, version, start_date=None, end_date=None):

    # Manage the dates
    if (start_date != None) or (end_date != None):
        # Get the frequency from product table
        product_info = querydb.get_product_out_info(productcode=product_code, subproductcode=sub_product_code, version=version)
        frequency_id = product_info[0].frequency_id
        dateformat = product_info[0].date_format
        cDataset = datasets.Dataset(product_code, sub_product_code,'',version=version)
        cFrequency = cDataset.get_frequency(frequency_id, dateformat)

        # Build the list of dates
        date_start = cFrequency.extract_date(str(start_date))
        if (end_date != '' and end_date is not None):
            date_end = cFrequency.extract_date(str(end_date))
        else:
            date_end = datetime.date.today()

        list_dates = cFrequency.get_internet_dates(cFrequency.get_dates(date_start, date_end),'%Y%m%d')
    else:
        list_dates = None

    return list_dates

######################################################################################
#
#   Purpose: for a prod/subprod/version/mapset creates the permanently missing files
#            within the period:
#            start_date |-| end_date                     [if both are provided]
#            start_date  -> last_existing_date           [if only start is provided]
#            first_existing_date |-| last_existing_date  [if none is provided]
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/05/15
#   Inputs:
#   Output: none
#

def create_permanently_missing_for_dataset(product_code, sub_product_code, version, mapset_code, start_date=None, end_date=None):

    # Get the existing dates for the dataset
    product = products.Product(product_code,version=version)
    missing_filenames = product.get_missing_filenames({'product':product_code, 'version':version})

    # Manage the dates
    if (start_date != None) or (end_date != None):
        # Get the frequency from product table
        product_info = querydb.get_product_out_info(productcode=product_code, subproductcode=sub_product_code, version=version)
        frequency_id = product_info[0].frequency_id
        dateformat = product_info[0].date_format
        cDataset = datasets.Dataset(product_code, sub_product_code,'',version=version)
        cFrequency = cDataset.get_frequency(frequency_id, dateformat)

        # Build the list of dates
        date_start = cFrequency.extract_date(str(start_date))
        if (end_date != '' and end_date is not None):
            date_end = cFrequency.extract_date(str(end_date))
        else:
            date_end = datetime.date.today()

        list_dates = cFrequency.get_internet_dates(cFrequency.get_dates(date_start, date_end),'%Y%m%d')
    else:
        list_dates = None

    return list_dates

######################################################################################
#
#   Purpose: ensure the subproducts are present in the products.product table
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/05/15
#   Inputs:
#   Output: none
#

def upsert_database(product_code, version, proc_lists, input_product_info):

    # Get the existing dates for the dataset
    product = products.Product(product_code,version=version)
    missing_filenames = product.get_missing_filenames({'product':product_code, 'version':version})

    return status
######################################################################################
#
#   Purpose: reproject a file to a different mapset
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/05/15
#   Inputs: input_file (an eStation 2.0 GTIFF file)
#           target_mapset: the target mapset of reprojection
#   Output: output_file
#

def reproject_output(input_file, native_mapset_id, target_mapset_id, logger=None):

    # Check logger
    if logger is None:
        logger = log.my_logger(__name__)

    # Get the existing dates for the dataset
    logger.info("Entering routine %s for file %s" % ('reproject_output', input_file))
    ext=es_constants.ES2_OUTFILE_EXTENSION

    # Test the file/files exists
    if not os.path.isfile(input_file):
        logger.error('Input file: %s does not exist' % input_file)
        return 1

    # Instance metadata object (for output_file)
    sds_meta_out = metadata.SdsMetadata()

    # Read metadata from input_file
    sds_meta_in = metadata.SdsMetadata()
    sds_meta_in.read_from_file(input_file)

    # Extract info from input file
    str_date = sds_meta_in.get_item('eStation2_date')
    product_code = sds_meta_in.get_item('eStation2_product')
    sub_product_code = sds_meta_in.get_item('eStation2_subProduct')
    version = sds_meta_in.get_item('eStation2_product_version')

    # Define output filename
    sub_dir = sds_meta_in.get_item('eStation2_subdir')
    product_type = functions.get_product_type_from_subdir(sub_dir)

    out_prod_ident = functions.set_path_filename_no_date(product_code, sub_product_code, target_mapset_id, version, ext)
    output_subdir  = functions.set_path_sub_directory   (product_code, sub_product_code, product_type, version, target_mapset_id)

    output_file = es_constants.es2globals['processing_dir']+\
                  output_subdir +\
                  str_date +\
                  out_prod_ident

    # make sure output dir exists
    output_dir = os.path.split(output_file)[0]
    functions.check_output_dir(output_dir)

    # -------------------------------------------------------------------------
    # Manage the geo-referencing associated to input file
    # -------------------------------------------------------------------------
    orig_ds = gdal.Open(input_file, gdal.GA_Update)

    # Read the data type
    band = orig_ds.GetRasterBand(1)
    out_data_type_gdal = band.DataType

    if native_mapset_id != 'default':
        native_mapset = mapset.MapSet()
        native_mapset.assigndb(native_mapset_id)
        orig_cs = osr.SpatialReference(wkt=native_mapset.spatial_ref.ExportToWkt())

        # Complement orig_ds info (necessary to Re-project)
        try:
            #orig_ds.SetGeoTransform(native_mapset.geo_transform)
            orig_ds.SetProjection(orig_cs.ExportToWkt())
        except:
            logger.debug('Cannot set the geo-projection .. Continue')
    else:
        try:
            # Read geo-reference from input file
            orig_cs = osr.SpatialReference()
            orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
        except:
            logger.debug('Cannot read geo-reference from file .. Continue')

    # TODO-M.C.: add a test on the mapset-id in DB table !
    trg_mapset = mapset.MapSet()
    trg_mapset.assigndb(target_mapset_id)
    logger.debug('Target Mapset is: %s' % target_mapset_id)

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
    sds_meta_out.assign_mapset(target_mapset_id)
    sds_meta_out.assign_from_product(product_code, sub_product_code, version)
    sds_meta_out.assign_date(str_date)
    sds_meta_out.assign_subdir_from_fullpath(output_dir)
    sds_meta_out.assign_comput_time_now()
    sds_meta_out.assign_input_files(input_file)

    # Write metadata to file
    sds_meta_out.write_to_file(output_file)
