#
#	purpose: Define the ingest service
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 20.02.2014
#   descr:	 Process input files into the specified 'mapset'
#	history: 1.0
#
#   TODO-LinkIT: for MCD45monthly aborts for out-of-memory in re-scaling data ! FTTB ingest only 2 windows

# source eStation2 base definitions
import locals

# import standard modules
import re
import tempfile
import zipfile
import bz2
import glob
import ntpath

# import eStation2 modules
import database.crud as crud
import database.querydb as querydb
import lib.python.functions as func
from lib.python import es_logging as log
from lib.python.mapset import *
from lib.python.metadata import *
from config.es_constants import *

import pygrib
from osgeo import gdal

logger = log.my_logger(__name__)

ingest_dir_in = locals.es2globals['ingest_dir']
data_dir_out= locals.es2globals['data_dir']

def drive_ingestion():
#    Driver of the ingestion process
#    Reads configuration from the database
#    Reads the list of files existing in input directory
#    Loops over file and call the ingestion script
#

    logger.info("Entering routine %s" % 'drive_ingestion')
    echo_query = False

    # get all active product ingestion records with a subproduct count.
    active_product_ingestions = querydb.get_ingestion_product(allrecs=True, echo=echo_query)

    for active_product_ingest in active_product_ingestions:

        logger.info("Ingestion active for product: [%s] subproduct N. %s" % (active_product_ingest[0],
                                                                             active_product_ingest[2]))
        productcode = active_product_ingest[0]
        productversion = active_product_ingest[1]

        # For the current active product ingestion: get all
        product = {"productcode": productcode,
                   "version": productversion}
        logger.debug("Processing product: %s" % productcode)

        # Get the list of acquisition sources that are defined for this ingestion 'trigger'
        # (i.e. prod/version)
        # TODO-M.C.: test the case of more mapsets for the same prod/subprod/version -> pb. in file deletion ?
        # NOTE: the following implies there is 1 and only 1 '_native' subproduct associated to a 'subproduct';
        native_product = {"productcode": productcode,
                          "subproductcode": productcode + "_native",
                          "version": productversion}

        sources_list = querydb.get_product_sources(echo=echo_query, **native_product)

        logger.debug("For product [%s] N. %s  source is/are found" % (productcode,len(sources_list)))

        for source in sources_list:

            logger.debug("Processing Source type [%s] with id [%s]" % (source.type, source.data_source_id))
            # Get the 'filenaming' info (incl. 'area-type') from the acquisition source
            if source.type == 'EUMETCAST':
                for eumetcast_filter, datasource_descr in querydb.get_datasource_descr(echo=echo_query,
                                                                                       source_type=source.type,
                                                                                       source_id=source.data_source_id):

                    # TODO-M.C.: replace with a glob function ? this loop can be very long ...
                    files = [f for f in os.listdir(ingest_dir_in) if re.match(str(eumetcast_filter), f)]
                    #files = glob.glob(ingest_dir_in+eumetcast_filter)

            if source.type == 'INTERNET':
                # Implement file name filtering for INTERNET data source.
                for internet_filter, datasource_descr in querydb.get_datasource_descr(echo=echo_query,
                                                                                      source_type=source.type,
                                                                                      source_id=source.data_source_id):
                # TODO-Jurvtk: complete/verified
                    temp_internet_filter = internet_filter.include_files_expression
                    # TODO-M.C.: replace with a glob function ? this loop can be very long ...
                    files = [f for f in os.listdir(ingest_dir_in) if re.match(temp_internet_filter, f)]
                    #files = glob.glob(ingest_dir_in+temp_internet_filter)

            logger.info("Number of files found for product [%s] is: %s" % (active_product_ingest[0], len(files)))

            ingestions = querydb.get_ingestion_subproduct(allrecs=False, echo=echo_query, **product)
            # Loop over ingestion triggers
            subproducts = list()
            for ingest in ingestions:
                logger.debug(" --> processing subproduct: %s" % ingest.subproductcode)
                args = {"productcode": product['productcode'],
                        "subproductcode": ingest.subproductcode,
                        "datasource_descr_id": datasource_descr.datasource_descr_id,
                        "version": product['version']}
                product_in_info = querydb.get_product_in_info(echo=echo_query, **args)
                re_process = product_in_info.re_process
                re_extract = product_in_info.re_extract
                sprod = {'subproduct': ingest.subproductcode,
                         'mapsetcode': ingest.mapsetcode,
                         're_extract': re_extract,
                         're_process': re_process}
                subproducts.append(sprod)

            # Get the list of unique dates by extracting the date from all files.
            dates_list = []
            for filename in files:
                date_position = int(datasource_descr.date_position)
                if datasource_descr.format_type == 'delimited':
                    # splitted_fn = re.split(r'[datasource_descr.delimiter\s]\s*', filename) ???? What is that for ?
                    splitted_fn = re.split(datasource_descr.delimiter, filename)
                    dates_list.append(splitted_fn[date_position])
                else:
                    dates_list.append(filename[date_position:date_position + len(datasource_descr.date_type)])

            dates_list = set(dates_list)
            dates_list = sorted(dates_list, reverse=False)

            # Loop over dates and get list of files (considering mapset ?)
            for in_date in dates_list:
                logger.debug("     --> processing date, in native format: %s" % in_date)
                # Get the list of existing files for that date
                regex = re.compile(".*(" + in_date + ").*")
                date_fileslist = [ingest_dir_in + m.group(0) for l in files for m in [regex.search(l)] if m]

                # Pass list of files to ingestion routine
                ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, echo_query=echo_query)

def ingestion(input_files, in_date, product, subproducts, datasource_descr, echo_query=False):
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
#       mapset: output mapset to be applied
#       datasource_descr: datasource description object (incl. native_mapset, compose_area_method, ..)
#
#      TODO-M.C.: change compose_area_type to preproc_type in the table and associated structure
#
    logger.info("Entering routine %s for prod: %s and date: %s" % ('ingestion', product['productcode'], in_date))

    preproc_type =  datasource_descr.compose_area_type
    native_mapset_code = datasource_descr.native_mapset

    do_preprocess = 0

    if preproc_type != '':
        do_preprocess = 1

    if do_preprocess == 1:
        logger.debug("Calling routine %s" % 'preprocess_files')
        composed_file_list = pre_process_inputs(preproc_type, native_mapset_code, subproducts, input_files)
    else:
        composed_file_list = input_files

    ingest_file(composed_file_list, in_date, product, subproducts, datasource_descr, in_files=input_files,
                echo_query=echo_query)

def pre_process_msg_mpe (tmpdir , input_files):
# -------------------------------------------------------------------------------------------------------
#   Pre-process msg_mpe files
#   4 expected segments as input
#

    # Test the files exist
    for ifile in input_files:
        if not os.path.isfile(ifile):
            logger.error('Input file does not exist')
            return 1

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

    # Read the .grb and convert to gtiff (GDAL dose not do it properly)
    grbs = pygrib.open(out_tmp_grib_file)
    grb = grbs.select(name='Instantaneous rain rate')[0]
    data = grb.values
    output_driver = gdal.GetDriverByName(ES2_OUTFILE_FORMAT)
    output_ds = output_driver.Create(out_tmp_tiff_file, 3712, 3712, 1, GDT_Float64)
    output_ds.GetRasterBand(1).WriteArray(data)

    return out_tmp_tiff_file

def pre_process_modis_hdf4_tile (subproducts, tmpdir , input_files):
# -------------------------------------------------------------------------------------------------------
#   Pre-process MODIS HDF4 tiled files
#

    # Build a list of subdatasets to be extracted
    list_to_extr = []
    for sprod in subproducts:
        if sprod != 0:
            list_to_extr.append(sprod['re_extract'])

    # Variable number of expected input file: loop over
    for index, ifile in enumerate(input_files):

        # Test the file exists
        if not os.path.isfile(ifile):
            logger.error('Input file does not exist ' + ifile)
            return 1

        # Test the hdf file and read list of datasets
        hdf = gdal.Open(ifile)
        sdsdict = hdf.GetMetadata('SUBDATASETS')
        sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]

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
            out_tmp_file_gtiff = tmpdir + os.path.sep + id_subproduct + '_merged.tif'

            file_to_merge = glob.glob(tmpdir + os.path.sep + id_subproduct + '*')
            # TODO-M.C.: How to locate gdal_merge.py ???
            command = '/usr/bin/gdal_merge.py -init 9999 -co \"compress=lzw\" -o '
            command += out_tmp_file_gtiff
            for file_add in file_to_merge:
                command += ' '
                command += file_add
            logger.debug('Command for merging is: ' + command)
            os.system(command)

    return out_tmp_file_gtiff

def pre_process_lsasaf_hdf5 (subproducts, tmpdir , input_files):
# -------------------------------------------------------------------------------------------------------
#   Pre-process LSASAF HDF5 files
#
    # It receives in input the list of the (.bz2) files (NAfr,SAfr)
    # It unzips the files to tmpdir, extracts relevant sds from hdf, does the merging in original proj.
    unzipped_input_files = []

    # Loop over input files and unzips
    for index, ifile in enumerate(input_files):
        logger.debug('Processing input file  ' + ifile)
        # Test the file exists
        if not os.path.isfile(ifile):
            logger.error('Input file does not exist ' + ifile)
            return 1
        # Unzip to tmpdir and add to list
        if re.match('.*\.bz2', ifile):
            logger.debug('Decompressing bz2 file: ' + ifile)
            bz2file = bz2.BZ2File(ifile)                    # Create ZipFile object
            data = bz2file.read()                           # Get the list of its contents
            filename = os.path.basename(ifile)
            filename = filename.replace('.bz2', '')
            myfile_path = os.path.join(tmpdir, filename)
            myfile = open(myfile_path, "wb")
            myfile.write(data)
            myfile.close()
            bz2file.close()

            unzipped_input_files.append(myfile_path)

    # Build a list of subdatasets to be extracted
    list_to_extr = []
    for sprod in subproducts:
        if sprod != 0:
            list_to_extr.append(sprod['re_extract'])

    # Loop over unzipped files and extract relevant SDSs
    for index, unzipped_file in enumerate(unzipped_input_files):
        logger.debug('Processing unzipped file: ' + unzipped_file)
        # Identify the region from filename
        region = unzipped_file.split('_')[-2]
        logger.debug('Region of unzipped file is :' + region)
        # Test the file exists
        if not os.path.isfile(unzipped_file):
            logger.error('Input file does not exist ' + unzipped_file)
            return 1

        # Test the hdf file and read list of datasets
        hdf = gdal.Open(unzipped_file)
        sdsdict = hdf.GetMetadata('SUBDATASETS')
        sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]

        # Loop over datasets and check if they have to be extracted
        for subdataset in sdslist:
            id_subdataset = subdataset.split(':')[-1]
            id_subdataset = id_subdataset.replace('//', '')
            if id_subdataset in list_to_extr:
                outputfile = tmpdir + os.path.sep + id_subdataset + '_' + region + '.tif'
                sds_tmp = gdal.Open(subdataset)
                write_ds_to_geotiff(sds_tmp, outputfile)
                sds_tmp = None

    # For each dataset, merge the files, by using the dedicated function
    for id_subdataset in list_to_extr:
        files_to_merge = glob.glob(tmpdir + os.path.sep + id_subdataset + '*.tif')

        output_file = tmpdir + os.path.sep + id_subdataset + '.tif'

    mosaic_lsasaf_msg(files_to_merge, output_file, '')
    logger.debug('Output file generated: ' + output_file)

    return output_file

def pre_process_pml_netcdf (subproducts, tmpdir , input_files):
# -------------------------------------------------------------------------------------------------------
#   Pre-process PML NETCDF files
#
    # It receives in input the list of the (.bz2) files (windows)
    # It unzips the files to tmpdir and does the merging in original proj.
    if isinstance(subproducts, list):
        if len(subproducts) > 1:
            logger.error('Only 1 subproducts can be extracted from PML_NETCDF files')
            return 1

    subproduct = subproducts[0]
    unzipped_input_files = []

    # Loop over input files and unzips
    for index, ifile in enumerate(input_files):
        logger.debug('Processing input file  ' + ifile)
        # Test the file exists
        if not os.path.isfile(ifile):
            logger.error('Input file does not exist ' + ifile)
            return 1

        # Unzip to tmpdir and add to list
        if re.match('.*\.bz2', ifile):
            logger.debug('Decompressing bz2 file: ' + ifile)
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

    id_subproduct = subproduct['re_extract']

    geotiff_files = []
    # Loop over unzipped files and extract the relevant sds to tmp geotiffs
    for input_file in unzipped_input_files:

        # Test the. nc file and read list of datasets
        netcdf = gdal.Open(input_file)
        sdslist = netcdf.GetSubDatasets()

        # Loop over datasets and extract the one from each unzipped
        for subdataset in sdslist:
            netcdf_subdataset = subdataset[0]
            id_subdataset = netcdf_subdataset.split(':')[-1]

            if id_subdataset == id_subproduct:
                selected_sds = 'NETCDF:' + input_file + ':' + id_subdataset
                sds_tmp = gdal.Open(selected_sds)
                filename = os.path.basename(input_file) + '.geotiff'
                myfile_path = os.path.join(tmpdir, filename)
                write_ds_to_geotiff(sds_tmp, myfile_path)
                sds_tmp = None
                geotiff_files.append(myfile_path)


        # Merge temporary geotiff to a single one
        out_tmp_gtiff_file = tmpdir + os.path.sep + id_subproduct + '_merged.tif'

    # TODO-M.C.: How to locate gdal_merge.py ???
    command = '/usr/bin/gdal_merge.py -init 9999 -co \"compress=lzw\" -o '
    command += out_tmp_gtiff_file
    for file_add in geotiff_files:
        command += ' '
        command += file_add
    logger.info('Command for merging is: ' + command)
    os.system(command)

    return out_tmp_gtiff_file

def pre_process_unzip (subproducts, tmpdir , input_files):
# -------------------------------------------------------------------------------------------------------
#   Pre-process ZIPPED files
#
    out_tmp_gtiff_file = []
    #  zipped files containing one or more HDF4
    if isinstance(input_files, list):
        if len(input_files) > 1:
            logger.error('Only 1 file expected. Exit')
            return 1
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
            logger.debug('Re_expression: ' + re_extract + ' to match sprod ' + sprod['subproduct'])

            for files in zip_list:
                logger.debug('File in the .zip archive is: ' + files)
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
        logger.error("File %s is not a valid zipfile. Exit", input_files)
        return 1

        # TODO-M.C.:Check all datasets have been found (len(intermFile) ==len(subprods)))
        # Remove tempDir -> not here: tmpfile still to be used
        # shutil.rmtree(tmp_dir)

    return out_tmp_gtiff_file

def pre_process_bzip2 (tmpdir, input_files):
# -------------------------------------------------------------------------------------------------------
#   Pre-process bzip2 files
#
    interm_files_list = []

    # Make sure it is a list (if only a string is returned, it loops over chars)
    if isinstance(input_files,list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    for input_file in list_input_files:
        logger.info('Unzipping/processing: .bz2 case')
        bz2file = bz2.BZ2File(input_file)               # Create ZipFile object
        data = bz2file.read()                            # Get the list of its contents
        filename = os.path.basename(input_file)
        filename = filename.replace('.bz2', '')
        myfile_path = os.path.join(tmpdir, filename)
        myfile = open(myfile_path, "wb")
        myfile.write(data)
        myfile.close()
        bz2file.close()

        interm_files_list.append(myfile_path)

    return interm_files_list

def pre_process_bz2_hdf4 (subproducts, tmpdir, input_files):
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
    if isinstance(input_files,list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    # Bz2 unzips to my_bunzip2_file (TODO-M.C.: re-use the method above ??)
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
        sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]

        # Loop over datasets and extract the one in the list
        for subdataset in sdslist:
            id_subdataset = subdataset.split(':')[-1]
            if id_subdataset in list_to_extr:
                outputfile = tmpdir + os.path.sep + filename + "_" + id_subdataset + '_' + '.tif'
                sds_tmp = gdal.Open(subdataset)
                write_ds_to_geotiff(sds_tmp, outputfile)
                sds_tmp = None

                interm_files_list.append(outputfile)

    return interm_files_list

def pre_process_georef_netcdf (native_mapset_code, tmpdir, input_files):
# -------------------------------------------------------------------------------------------------------
#   Convert netcdf to GTIFF (and assign geo-referencing)
#   This is treated as a special case, being not possible to 'update' geo-ref info in the netcdf

    # prepare the output as an empty list
    interm_files_list = []

    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files,list):
        list_input_files = input_files
    else:
        list_input_files = []
        list_input_files.append(input_files)

    # Create native mapset object
    native_mapset = MapSet()
    native_mapset.assigndb(native_mapset_code)

    # Convert netcdf to GTIFF
    for input_file in list_input_files:
        outputfile = tmpdir + os.path.sep +  os.path.basename(input_file) + '_' + '.tif'
        dataset = gdal.Open(input_file)
        write_ds_and_mapset_to_geotiff(dataset, native_mapset, outputfile)
        interm_files_list.append(outputfile)

    return interm_files_list

def pre_process_hdf5_zip (subproducts, tmpdir, input_files):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF5 files zipped (g2_biopar products)
#   First unzips (only 1 unzip h5 file expected), then extract relevant subdatasets (1+)
#

    # prepare the output as an empty list
    interm_files_list = []

    # Build a list of subdatasets to be extracted
    sds_to_process = []
    for sprod in subproducts:
       # if sprod != 0:
            sds_to_process.append(sprod['re_process'])
    print sds_to_process
    # Make sure input is a list (if only a string is received, it loops over chars)
    if isinstance(input_files,list):
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
                logger.debug('Re_expression: ' + re_extract + ' to match sprod ' + sprod['subproduct'])

                for files in zip_list:
                    logger.debug('File in the .zip archive is: ' + files)
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
            logger.error("File %s is not a valid zipfile. Exit", input_files)
            return 1

        # Test the hdf file and read list of datasets
        hdf = gdal.Open(my_unzip_file)
        sdsdict = hdf.GetMetadata('SUBDATASETS')
        sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]

        # Loop over datasets and extract the one in the list
        for subdataset in sdslist:
            id_subdataset = subdataset.split(':')[-1]
            id_subdataset=id_subdataset.replace('/','')
            if id_subdataset in sds_to_process:
                outputfile = tmpdir + os.path.sep + filename + "_" + id_subdataset + '.tif'
                sds_tmp = gdal.Open(subdataset)
                write_ds_to_geotiff(sds_tmp, outputfile)
                sds_tmp = None

                interm_files_list.append(outputfile)

    return interm_files_list


def pre_process_inputs(preproc_type, native_mapset_code, subproducts, input_files):
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
#
#       native_mapset_code: id code of the native mapset (from datasource_descr)
#       subproducts: list of subproducts to be extracted from the file. Contains dictionaries such as:
#           see ingestion() for full description
#       input_files: list of input files
#   Returned:
#       output_file: temporary created output file[s]

    logger.info("Input files pre-processing by using method: %s" % preproc_type)

    # Create temp output dir
    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(input_files[0]),
                                  dir=locals.es2globals['temp_dir'])
    except IOError:
        logger.error('Cannot create temporary dir ' + locals.es2globals['temp_dir'] + '. Exit')
        return 1

    georef_already_done = False

    if preproc_type == 'MSG_MPE':
        interm_files = pre_process_msg_mpe (tmpdir , input_files)

    if preproc_type == 'MODIS_HDF4_TILE':
        interm_files = pre_process_modis_hdf4_tile (subproducts, tmpdir, input_files)

    if preproc_type == 'LSASAF_HDF5':
        interm_files = pre_process_lsasaf_hdf5 (subproducts, tmpdir, input_files)

    if preproc_type == 'PML_NETCDF':
        interm_files = pre_process_pml_netcdf (subproducts, tmpdir, input_files)

    if preproc_type == 'UNZIP':
        interm_files = pre_process_unzip (subproducts, tmpdir, input_files)

    if preproc_type == 'BZIP2':
        interm_files = pre_process_bzip2 (tmpdir, input_files)

    if preproc_type == 'GEOREF_NETCDF':
        interm_files = pre_process_georef_netcdf(native_mapset_code, tmpdir, input_files)
        georef_already_done = True

    if preproc_type == 'BZ2_HDF4':
        interm_files = pre_process_bz2_hdf4 (subproducts, tmpdir, input_files)

    if preproc_type == 'HDF5_ZIP':
        interm_files = pre_process_hdf5_zip (subproducts, tmpdir, input_files)

    # Make sure it is a list (if only a string is returned, it loops over chars)
    if isinstance(interm_files,list):
        list_interm_files = interm_files
    else:
        list_interm_files = []
        list_interm_files.append(interm_files)

    # Create native mapset (or assign as empty string)
    if native_mapset_code != 'default' and (not georef_already_done):

        # Create Mapset object and test
        native_mapset = MapSet()
        native_mapset.assigndb(native_mapset_code)
        logger.debug('Native mapset IS passed: ' + native_mapset.short_name)

        if native_mapset.validate():
            logger.error('Native mapset passed is invalid: ' + native_mapset.short_name)
            return 1
        # Loop over interm_files and assign mapset
        for intermFile in list_interm_files:
            logger.debug('Intermediate file: ' + intermFile)

            # Open input dataset in update mode
            orig_ds = gdal.Open(intermFile, GA_Update)

            # Test result: in case of error (e.g. for nc files, it does not raise exception)
            # If wrong -> Open input dataset in read-only
            if orig_ds is None:
                orig_ds = gdal.Open(intermFile, GA_ReadOnly)

            # Otherwise read from native_mapset, and assign to ds
            orig_cs = native_mapset.spatial_ref
            orig_geo_transform = native_mapset.geo_transform
            orig_size_x = native_mapset.size_x
            orig_size_y = native_mapset.size_y

            orig_ds.SetGeoTransform(native_mapset.geo_transform)
            orig_ds.SetProjection(native_mapset.spatial_ref.ExportToWkt())


    return list_interm_files

def ingest_file(interm_files_list, in_date, product, subproducts, datasource_descr, in_files='', echo_query=False):
# -------------------------------------------------------------------------------------------------------
#   Ingest one or more files (a file for each subproduct)
#   Arguments:
#       interm_files_list: input file full name (1 per subproduct )
#       date: product date
#       product: product description name (for DB insertions)
#       subproducts: list of subproducts to be extracted from the file. Contains dictionaries such as:
#           see ingestion() for full description
#       datasource_descr: from the corresponding DB table (all info on in-file naming)
#       in_files[option]: list of input files
#       echo_query[option]: force print-out from query_db funtions
#

    # TODO-M.C.: manage version
    version_undef='undefined'
    logger.info("Entering routine %s for product %s - date %s" % ('ingest_file', product['productcode'], in_date))

    # Test the file/files exists
    for infile in interm_files_list:
        if not os.path.isfile(infile):
            logger.error('Input file: %s does not exist' % infile)
            return 1

    # Instance metadata object
    sds_meta = SdsMetadata()

    # -------------------------------------------------------------------------
    # Assign dir-name
    # -------------------------------------------------------------------------

    readablelist = [' ' + os.path.basename(elem) for elem in interm_files_list]
    logger.info('In ingest_file: Intermediate file list: ' + ''.join(map(str, readablelist)))

    # -------------------------------------------------------------------------
    # Loop over 'intermediate files' and perform ingestion
    # Note: interm file MUST contain only 1 raster-band/subdataset
    # -------------------------------------------------------------------------
    ii = 0

    for intermFile in interm_files_list:

        logger.info("Processing intermediate file: %s" % os.path.basename(intermFile))

        # -------------------------------------------------------------------------
        # Collect info and prepare filenaming
        # -------------------------------------------------------------------------

        # Get information about the dataset
        args = {"productcode": product['productcode'],
                "subproductcode": subproducts[ii]['subproduct'],
                "datasource_descr_id": datasource_descr.datasource_descr_id,
                "version": product['version']}

        # Get information from sub_dataset_source table
        product_in_info = querydb.get_product_in_info(echo=echo_query, **args)

        in_scale_factor = product_in_info.scale_factor
        in_offset = product_in_info.scale_offset
        in_nodata = product_in_info.no_data
        in_mask_min = product_in_info.mask_min
        in_mask_max = product_in_info.mask_max
        in_data_type = product_in_info.data_type_id

        # Get information from 'product' table
        args = {"productcode": product['productcode'], "subproductcode": subproducts[ii]['subproduct'], "version":product['version']}
        product_info = querydb.get_product_out_info(echo=echo_query, **args)
        out_data_type = product_info.data_type_id
        out_scale_factor = product_info.scale_factor
        out_offset = product_info.scale_offset
        out_nodata = product_info.nodata

        # Translate data type for gdal and numpy
        out_data_type_gdal = conv_data_type_to_gdal(out_data_type)
        out_data_type_numpy = conv_data_type_to_numpy(out_data_type)

        mapset = MapSet()
        mapset.assigndb(subproducts[ii]['mapsetcode'])
        # Check target-mapset
        if mapset == '':
            logger.debug('Target mapset NOT passed: keep the native one.')
            mapset_id = 'native'
        else:
            mapset_id = mapset.short_name
            logger.debug('Target mapset IS passed: ' + mapset_id)

        # Convert the in_date format into a convenient one for DB and file naming
        # (i.e YYYYMMDD or YYYYMMDDHHMM)
        if datasource_descr.date_type == 'YYYYMMDD':
            if func.is_date_yyyymmdd(in_date):
                output_date_str = in_date
            else:
                output_date_str = -1

        if datasource_descr.date_type == 'YYYYMMDDHHMM':
            if func.is_date_yyyymmddhhmm(in_date):
                output_date_str = in_date
            else:
                output_date_str = -1

        if datasource_descr.date_type == 'YYYYDOY_YYYYDOY':
            output_date_str = func.conv_date_yyyydoy_2_yyyymmdd(str(in_date)[0:7])

        if datasource_descr.date_type == 'YYYYMMDD_YYYYMMDD':
            output_date_str = str(in_date)[0:8]
            if not func.is_date_yyyymmdd(output_date_str):
                output_date_str = -1

        if datasource_descr.date_type == 'YYYYDOY':
            output_date_str = func.conv_date_yyyydoy_2_yyyymmdd(in_date)

        if datasource_descr.date_type == 'YYYY_MM_DKX':
            output_date_str = func.conv_yyyy_mm_dkx_2_yyyymmdd(in_date)

        if datasource_descr.date_type == 'YYMMK':
            output_date_str = func.conv_yymmk_2_yyyymmdd(in_date)

        if output_date_str == -1:
            output_date_str = in_date+'_DATE_ERROR_'
            year = None
            month = None
            day = None
            hour = None
        else:
            year = int(output_date_str[0:4])
            month = int(output_date_str[4:6])
            day = int(output_date_str[6:8])
            if datasource_descr.date_type == 'YYYYMMDDHHMM':
                hour = int(output_date_str[8:12])
            else:
                hour = None

        # Define output directory and make sure it exists
        output_directory = data_dir_out+ func.set_path_sub_directory(product['productcode'],subproducts[ii]['subproduct'],
                                                                'Ingest', version_undef, mapset_id)
        try:
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
        except:
            logger.error('Cannot create output directory: ' + output_directory)
            return 1

        # Define output filename
        output_filename = output_directory + func.set_path_filename(output_date_str,
                                                               product['productcode'],
                                                               subproducts[ii]['subproduct'],
                                                               mapset_id,
                                                               '.tif')

        # -------------------------------------------------------------------------
        # Manage IN/OUT mapset and assess if re-projection has to be done
        # -------------------------------------------------------------------------

        native_mapset_code = datasource_descr.native_mapset
        if native_mapset_code != 'default':
            native_mapset = MapSet()
            native_mapset.assigndb(native_mapset_code)
        else:
            native_mapset = ''

        native_mapset_code != 'default'
        # Open input dataset in read-only
        orig_ds = gdal.Open(intermFile, GA_ReadOnly)

        # Import CoordSys from file
        orig_cs = osr.SpatialReference()
        orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
        orig_geo_transform = orig_ds.GetGeoTransform()
        orig_size_x = orig_ds.RasterXSize
        orig_size_y = orig_ds.RasterYSize

        # Check if re-projection has to be done
        reprojection = 1
        # If no target mapset
        if mapset == '':
            reprojection = 0
        else:
            # .. OR if both defined, and equal
            if native_mapset != '':
                if mapset.short_name == native_mapset.short_name:
                    reprojection = 0

        # -------------------------------------------------------------------------
        # Generate the output file
        # -------------------------------------------------------------------------
        # Prepare output driver
        out_driver = gdal.GetDriverByName(ES2_OUTFILE_FORMAT)

        if reprojection == 1:

            logger.debug('Doing re-projection to target mapset: %s' % mapset.short_name)
            # Get target SRS from mapset
            out_cs = mapset.spatial_ref
            out_size_x = mapset.size_x
            out_size_y = mapset.size_y

            # Create target in memory
            mem_driver = gdal.GetDriverByName('MEM')

            # Assign mapset to dataset in memory
            mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, out_data_type_gdal)
            mem_ds.SetGeoTransform(mapset.geo_transform)
            mem_ds.SetProjection(out_cs.ExportToWkt())

            # Apply Reproject-Image to the memory-driver
            res = gdal.ReprojectImage(orig_ds, mem_ds, orig_cs.ExportToWkt(), out_cs.ExportToWkt(),
                                      ES2_OUTFILE_INTERP_METHOD)

            logger.debug('Re-projection to target done.')

            # Read from the dataset in memory
            out_data = mem_ds.ReadAsArray()

            # Apply rescale to data
            scaled_data = rescale_data(out_data, in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max,
                                       out_data_type_numpy, out_scale_factor, out_offset, out_nodata)

            # Create a copy to output_file
            trg_ds = out_driver.CreateCopy(output_filename, mem_ds, 0, [ES2_OUTFILE_OPTIONS])
            trg_ds.GetRasterBand(1).WriteArray(scaled_data)

        else:
            logger.debug('Doing only rescaling/format conversion')

            # Read from input file
            band = orig_ds.GetRasterBand(1)
            logger.debug('Band Type='+gdal.GetDataTypeName(band.DataType))
            out_data = band.ReadAsArray(0, 0, orig_size_x, orig_size_y)

            # No reprojection, only format-conversion
            trg_ds = out_driver.Create(output_filename, orig_size_x, orig_size_y, 1, out_data_type_gdal,
                                       [ES2_OUTFILE_OPTIONS])
            trg_ds.SetProjection(orig_ds.GetProjectionRef())
            trg_ds.SetGeoTransform(orig_geo_transform)

            # Apply rescale to data
            scaled_data = rescale_data(out_data, in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max,
                                       out_data_type_numpy, out_scale_factor, out_offset, out_nodata)

            trg_ds.GetRasterBand(1).WriteArray(scaled_data)

            orig_ds = None

        # -------------------------------------------------------------------------
        # Assign Metadata to the ingested file
        # -------------------------------------------------------------------------

        sds_meta.assign_es2_version()
        sds_meta.assign_mapset(mapset_id)
        sds_meta.assign_from_product(product['productcode'], subproducts[ii]['subproduct'], product['version'])
        sds_meta.assign_date(output_date_str)
        sds_meta.assign_subdir_from_fullpath(output_directory)
        sds_meta.assign_comput_time_now()
        sds_meta.assign_input_files(in_files)

        sds_meta.write_to_ds(trg_ds)

        trg_ds = None

        # -------------------------------------------------------------------------
        # Upsert into DB table 'products_data'
        # -------------------------------------------------------------------------

        filename = os.path.basename(output_filename)

        # TODO-M.C.: completely remove ???
        # cruddb = crud.CrudDB()
        # recordkey = {'productcode': product['productcode'],
        #              'subproductcode': subproducts[ii]['subproduct'],
        #              'version': product['version'],
        #              'mapsetcode': subproducts[ii]['mapsetcode'],
        #              'product_datetime': output_date_str}
        #
        # record = {'productcode': product['productcode'],
        #           'subproductcode': subproducts[ii]['subproduct'],
        #           'version': product['version'],
        #           'mapsetcode': subproducts[ii]['mapsetcode'],
        #           'product_datetime': output_date_str,
        #           'directory': output_directory,
        #           'filename': filename,
        #           'year': year,
        #           'month': month,
        #           'day': day,
        #           'hour': hour,
        #           'file_role': 'active',
        #           'file_type': 'GTiff'}
        # if len(cruddb.read('products.products_data', **recordkey)) > 0:
        #     logger.debug('Updating products_data record: ' + str(recordkey))
        #     cruddb.update('products.products_data', record)
        # else:
        #     cruddb.create('products.products_data', record)

        #,'creation_datetime': 'now()'

        # Loop on interm_files
        ii += 1


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
    dataset = None

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

    # definitions: Euro, NAfr, SAfr, Same -> MUST match with filenaming
    # as defined in SAF/LAND/MF/PUM_AL/1.4, version 1.4, date 15/12/2006
    # on table 4, page 33
    # positions in the array start counting at 1
    # TODO-LinkIT: improve efficiency

    regions_rois = {'Euro': [1550, 3250, 50, 700],
                    'NAfr': [1240, 3450, 700, 1850],
                    'SAfr': [2140, 3350, 1850, 3040],
                    'Same': [40, 740, 1460, 2970]}

    pattern = 'Euro|NAfr|SAfr|Same'

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
            fidin = gdal.Open(ifile, GA_ReadOnly)
            fid.append(fidin)
            # Find the region and append to list
            region = re.search(pattern, ntpath.basename(ifile))
            regions.append(region.group(0))
            # Check data type
            dataType = fidin.GetRasterBand(1).DataType
            if data_type_ref is None:
                data_type_ref = dataType
            elif data_type_ref != dataType:
                print "Files do not have the same type!"
                return 1

    # output matrix dimensions
    dataOut = N.ones((out_ns, out_nl))          #TODO-M.C.: * nodata TO BE MANAGED

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
                    print initCol + ix, initLine + il

        accumlines = accumlines + inH.YSize

    # instantiate output file
    out_driver = gdal.GetDriverByName('GTiff')
    out_ds = out_driver.Create(output_file, out_ns, out_nl, 1, dataType, [ES2_OUTFILE_OPTIONS])

    # assume only 1 band
    outband = out_ds.GetRasterBand(1)
    outband.WriteArray(N.array(dataOut), 0, 0)


def rescale_data(in_data,
                 in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max,
                 out_data_type, out_scale_factor, out_offset, out_nodata):
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
        logger.error('Input argument must be a numpy array. Exit')
        return 1

    #print mem_usage('Entering rescale')
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

    # Check if input rescaling has to be done
    if in_scale_factor != 1 or in_offset != 0:
        phys_value = in_data * in_scale_factor + in_offset
    else:
        phys_value = in_data

    # Assign to the output array
    trg_data = (phys_value - out_offset) / out_scale_factor

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
#   type: data type in wkt-estation format (inherited from 1.X)
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
        return GDT_Byte
    elif type == 'Int16':
        return GDT_Int16
    elif type == 'UInt16':
        return GDT_UInt16
    elif type == 'Int32':
        return GDT_Int32
    elif type == 'UInt32':
        return GDT_UInt32
    elif type == 'Float32':
        return GDT_Float32
    elif type == 'Float64':
        return GDT_Float64
    elif type == 'CFloat64':
        return GDT_CFloat64
    else:
        return GDT_Int16

