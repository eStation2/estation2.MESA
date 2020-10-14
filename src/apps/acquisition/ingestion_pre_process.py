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
import zipfile
import bz2
import glob
import ntpath
import os
import time, datetime
import numpy as N
import shutil
import gzip
import csv
import sys
import tarfile

# import h5py

from multiprocessing import *

# import eStation2 modules
from lib.python import functions
from lib.python import es_logging as log
from lib.python import mapset
from config import es_constants

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

    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_msg_mpe ')
        raise NameError('Error in Preprocessing pre_process_msg_mpe ')


def pre_process_mpe_umarf (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process msg_mpe files in UMARF format
#   Typical filename is MSG3-SEVI-MSGMPEG-0100-0100-20160331234500.000000000Z-20160331235848-1193222.grb.gz
#   Returns: pre_processed_list -> list of preprocessed files (to go on with ingestion)
#            Raise Exception: something went wrong (move existing files to /data/ingest.wrong)

    # Output list of pre-processed files
    pre_processed_list = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_mpe_umarf ')
        raise NameError('Error in Preprocessing pre_process_mpe_umarf ')

def pre_process_modis_hdf4_tile (subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process MODIS HDF4 tiled files
#
#   TODO-M.C.: add a mechanism to check input_files vs. mapsets ??
#              Optimize by avoiding repetition of the gdal_merge for the same sub_product, different mapset ?
#
    # Prepare the output file list
    pre_processed_list = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_modis_hdf4_tile ')
        raise NameError('Error in Preprocessing pre_process_modis_hdf4_tile ')


def pre_process_merge_tile(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process Merge tiled files from PROBAV 100 and 300 meters
#   Uses Gdal_merge to merge the file and gdal_translate to compress the file and assign BIGTIFF NO
#
    # Prepare the output file list
    pre_processed_list = []
    inter_processed_list = []
    try:
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
            output_file         = tmpdir+os.path.sep + 'merge_output.tif'
            output_file_vrt = tmpdir + os.path.sep + 'merge_output_rescaled.vrt'
            output_file_compressed  = tmpdir+os.path.sep + 'merge_output_compressed.tif'

            # -------------------------------------------------------------------------
            # STEP 1: Merge all input products into a 'tmp' file
            # -------------------------------------------------------------------------
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

    except:
        my_logger.error('Error in Preprocessing pre_process_merge_tile ')
        raise NameError('Error in Preprocessing pre_process_merge_tile ')


def pre_process_retile_vito (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process Merge tiled files
#
#   TODO-M.C.: add a mechanism to check input_files vs. mapsets ??
#              Optimize by avoiding repetition of the gdal_merge for the same sub_product, different mapset ?
#
    # Prepare the output file list
    pre_processed_list = []
    try:
    # # Build a list of subdatasets to be extracted
        # Check at least 1 file is reprojected file is there
        if len(input_files) == 0:
            my_logger.debug('No files. Return')
            return -1

        # args = {"productcode": product['productcode'],
        #         "subproductcode": subproducts[ii]['subproduct'],
        #         "datasource_descr_id": datasource_descr.datasource_descr_id,
        #         "version": product['version']}
        #
        # # Get information from sub_dataset_source table
        # product_in_info = querydb.get_product_in_info(**args)

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

    except:
        my_logger.error('Error in Preprocessing pre_process_retile_vito ')
        raise NameError('Error in Preprocessing pre_process_retile_vito ')



def drive_pre_process_lsasaf_hdf5(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Drive the Pre-process LSASAF HDF5 files
#
    # This is a quick fix of the gdal 1.9.2 bug on closing HDF files (see http://trac.osgeo.org/gdal/ticket/5103)
    # Since the files cannot be closed, and end up in reaching the max-number of open files (1024) we
    # call the routine as a detached process
    # pre_processed_list = '1'
    try:
        module_name = 'ingestion_pre_process'
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

    except:
        my_logger.error('Error in calling pre_process_lsasaf_hdf5')
        raise NameError('Error in calling pre_process_lsasaf_hdf5')

    # finally:
    #     return pre_processed_list

def pre_process_lsasaf_hdf5(subproducts, tmpdir , input_files, my_logger, out_queue):
# -------------------------------------------------------------------------------------------------------
#   Pre-process LSASAF HDF5 files
#
    # It receives in input the list of the (.bz2) files (e.g. NAfr, SAfr)
    # It unzips the files to tmpdir, extracts relevant sds from hdf, does the merging in original proj.
    # Note that it 'replicates' the file_list for each target mapset

    pre_processed_files = []
    unzipped_input_files = []
    try:
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
                sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
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

    except:
        my_logger.error('Error in Preprocessing pre_process_lsasaf_hdf5 ')
        raise NameError('Error in Preprocessing pre_process_lsasaf_hdf5 ')


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
    try:
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
                command = es_constants.gdal_merge + ' -init '+ str(nodata_value)+' -co \"compress=lzw\"  -of GTiff -ot Float32 -o '
                command += out_tmp_file_gtiff
                for file_add in geotiff_files:
                    command += ' '
                    command += file_add
                my_logger.info('Command for merging is: ' + command)
                os.system(command)
                pre_processed_list.append(out_tmp_file_gtiff)

        return pre_processed_list

    except:
        my_logger.error('Error in Preprocessing pre_process_pml_netcdf ')
        raise NameError('Error in Preprocessing pre_process_pml_netcdf ')


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
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_netcdf ')
        raise NameError('Error in Preprocessing pre_process_netcdf ')


def pre_process_unzip(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process ZIPPED files
#
    out_tmp_gtiff_file = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_unzip ')
        raise NameError('Error in Preprocessing pre_process_unzip ')


def pre_process_tarzip(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process .tgz files (e.g. WD-GEE)
#
    out_tmp_gtiff_file = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_tarzip ')
        raise NameError('Error in Preprocessing pre_process_tarzip ')


def pre_process_tarzip_wd_gee(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process .tgz files (e.g. WD-GEE)
#
    out_tmp_gtiff_file = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_tarzip_wd_gee ')
        raise NameError('Error in Preprocessing pre_process_tarzip_wd_gee ')

def pre_process_bzip2 (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process bzip2 files
#
    interm_files_list = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_bzip2 ')
        raise NameError('Error in Preprocessing pre_process_bzip2 ')


def pre_process_gzip (subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process gzip files
#
    interm_files_list = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_gzip ')
        raise NameError('Error in Preprocessing pre_process_gzip ')


def pre_process_bz2_hdf4(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF4 files bz2 zipped
#   First unzips, then extract relevant subdatasets

    # prepare the output as an empty list
    interm_files_list = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_bz2_hdf4 ')
        raise NameError('Error in Preprocessing pre_process_bz2_hdf4 ')


def pre_process_georef_netcdf(subproducts, native_mapset_code, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Convert netcdf to GTIFF (and assign geo-referencing)
#   This is treated as a special case, being not possible to 'update' geo-ref info in the netcdf

    # prepare the output as an empty list
    interm_files_list = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_georef_netcdf ')
        raise NameError('Error in Preprocessing pre_process_georef_netcdf ')

def pre_process_hdf5_zip(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF5 zipped files (e.g. g2_biopar products)
#   Only one zipped file is expected, containing more files (.h5, .xls, .txt, .xml, ..)
#   Only the .h5 is normally extracted. Then, the relevant SDSs extracted and converted to geotiff.
#

    # prepare the output as an empty list
    interm_files_list = []
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_hdf5_zip ')
        raise NameError('Error in Preprocessing pre_process_hdf5_zip ')

def pre_process_hdf5_gls(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF5 zipped files (specifically for g_cls files from VITO)
#   Only one zipped file is expected, containing more files (.nc, .xls, .txt, .xml, ..)
#   Only the .nc is normally extracted. Then, the relevant SDSs extracted and converted to geotiff.
#

    # prepare the output as an empty list
    interm_files_list = []
    try:
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
                my_sds_hdf='HDF5:'+my_unzip_file+'://'+output_sds
                sds_in = gdal.Open(my_sds_hdf)

                outputfile = tmpdir + os.path.sep + filename + '.tif'
                write_ds_to_geotiff(sds_in, outputfile)
                sds_in = None
                interm_files_list.append(outputfile)

        return interm_files_list

    except:
        my_logger.error('Error in Preprocessing pre_process_hdf5_gls ')
        raise NameError('Error in Preprocessing pre_process_hdf5_gls ')

def pre_process_hdf5_gls_nc(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process HDF5 non-zipped files (specifically for g_cls files from VITO)
#   It is the 'simplified' version of the pre_process_hdf5_gls method above, for the 'Global' files
#

    # prepare the output as an empty list
    interm_files_list = []
    try:
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
                my_sds_hdf='HDF5:'+input_file+'://'+output_sds
                sds_in = gdal.Open(my_sds_hdf)

                outputfile = tmpdir + os.path.sep + os.path.basename(input_file) + '.tif'
                write_ds_to_geotiff(sds_in, outputfile)
                sds_in = None
                interm_files_list.append(outputfile)

        return interm_files_list

    except:
        my_logger.error('Error in Preprocessing pre_process_hdf5_gls_nc ')
        raise NameError('Error in Preprocessing pre_process_hdf5_gls_nc ')


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
    try:
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
            # outFile.write('        <OGRVRTLayer name="firms_file" />\n')
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
        if python_version == 2:
            command = 'ogr2ogr -f "ESRI Shapefile" ' + file_shp + ' '+file_vrt
        elif python_version == 3:
            command = 'ogr2ogr -s_srs EPSG:4326 -t_srs EPSG:4326 -oo X_POSSIBLE_NAMES=Lon* -oo Y_POSSIBLE_NAMES=Lat* -f "ESRI Shapefile" '+ file_shp + ' '+file_csv

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

    except:
        my_logger.error('Error in Preprocessing pre_process_nasa_firms ')
        raise NameError('Error in Preprocessing pre_process_nasa_firms ')

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
    try:
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
            #For Other region
            date = input_file_name.split('_')[2]  # 0601-0000000000-0000000000.tif
            #For ECOWAS
            # date = input_file_name.split('_')[1]
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
        output_file         = tmpdir+os.path.sep + 'merge_output.tif'
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
                command += ' '+file

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

    except:
        my_logger.error('Error in Preprocessing pre_process_wdb_gee ')
        raise NameError('Error in Preprocessing pre_process_wdb_gee ')


def pre_process_ecmwf_mars(subproducts, tmpdir , input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process SPIRITS ECMWF files
#
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_ecmwf_mars ')
        raise NameError('Error in Preprocessing pre_process_ecmwf_mars ')


def pre_process_envi_to_geotiff(subproducts, tmpdir, input_files, my_logger):
# -------------------------------------------------------------------------------------------------------
#   Pre-process ENVI files
#
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_envi_to_geotiff ')
        raise NameError('Error in Preprocessing pre_process_envi_to_geotiff ')

# -------------------------------------------------------------------------------------------------------
#   Pre-process CPC files TYPE (binary, 720 x 360, global at 0.5 degree resolution)
#   See: http://www.cpc.ncep.noaa.gov/soilmst/leaky_glb.htm
def pre_process_cpc_binary(subproducts, tmpdir , input_files, my_logger):

    logger.debug('Unzipping/processing: CPC_BINARY case')
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_cpc_binary ')
        raise NameError('Error in Preprocessing pre_process_cpc_binary ')


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
    try:
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

    except:
        my_logger.error('Error in Preprocessing pre_process_gsod ')
        raise NameError('Error in Preprocessing pre_process_gsod ')


def pre_process_netcdf_s3_wrr(subproducts, tmpdir, input_files, my_logger, in_date=None, data_format='TAR'):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Sentinel 3 Level 2 product from OLCI - WRR
#   Returns -1 if nothing has to be done on the passed files
##   Description: the current implementation is based on GPT, and includes the following steps
#       1. Unzip or untar or just copy files into a temp dir
#       2. Write a 'subset' graph xml in order to:
#           a. Subset geographically:
#           b. Band subset (depends on subdatasource)
#           c. Apply a flag (band math)
#       3. Write a reprojection ..
#       4. Merge by applying input and output nodata (-n -54.53 -a_nodata -32768)
#   NOTE: now we mask by using l2p_flags_cloud ('True' means cloud detected -> reject)
#
    # Prepare the output file list
    pre_processed_list = []
    list_input_files = []

    try:
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

            if data_format == 'ZIP':
                # Unzip the .tar file in 'tmpdir'
                command = 'unzip ' + input_file + ' -d ' + tmpdir + os.path.sep  # ' --strip-components 1'
                print (command)
                status = os.system(command)

            elif data_format == 'TAR':
                # Unzip the .tar file in 'tmpdir'
                command = 'tar -xvf ' + input_file + ' -C ' + tmpdir + os.path.sep  # ' --strip-components 1'
                print(command)
                status = os.system(command)

            # JEODPP EOS data: In this case we just need to copy the folder tmp dir and remaining process is carried out asusal
            else:
                tmp_img_file_path = tmpdir + os.path.sep + os.path.basename(input_file)
                shutil.copytree(input_file, tmp_img_file_path)

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
                    # print(command_reproject)
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

    except:
        my_logger.error('Error in Preprocessing pre_process_netcdf_s3_wrr ')
        raise NameError('Error in Preprocessing pre_process_netcdf_s3_wrr ')


def pre_process_snap_subset_nc(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the netcdf using snap - subset and merge the tiles
#   Returns -1 if nothing has to be done on the passed files
#
    # Prepare the output file list
    pre_processed_list = []
    list_input_files = []
    try:
        # Make sure input is a list (if only a string is received, it loops over chars)
        if isinstance(input_files, list):
            temp_list_input_files = input_files
        else:
            temp_list_input_files = []
            temp_list_input_files.append(input_files)

        # Check at least 1 day-time file is there
        if len(temp_list_input_files) == 0:
            my_logger.debug('No any file captured during the day. Return')
            return -1

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

    except:
        my_logger.error('Error in Preprocessing pre_process_snap_subset_nc ')
        raise NameError('Error in Preprocessing pre_process_snap_subset_nc ')

#Currently not used since E1 DRO providing the files as Geotiff
def pre_process_snap_band_select_nc(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the netcdf using snap - subset and merge the tiles
#   Returns -1 if nothing has to be done on the passed files
#
    # Prepare the output file list
    pre_processed_list = []
    list_input_files = []
    try:
        # Make sure input is a list (if only a string is received, it loops over chars)
        if isinstance(input_files, list):
            temp_list_input_files = input_files
        else:
            temp_list_input_files = []
            temp_list_input_files.append(input_files)
        # Check at least 1 day-time file is there
        if len(temp_list_input_files) == 0:
            my_logger.debug('No any file captured. Return')
            return -1

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
                # Loop over bands to extract 3 dekad
                for dekad in range(3):
                    subband_name =  bandname + '_time'+str(count)
                    tmpdir_output = tmpdir + os.path.sep + subband_name
                    os.makedirs(tmpdir_output)
                    # ------------------------------------------------------------------------------------------
                    # Write a graph xml and select product for specific band
                    # ------------------------------------------------------------------------------------------
                    functions.write_graph_xml_bandselect(input_file=input_file, output_dir=tmpdir_output, band_name=subband_name)
                    #functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process)


                    graph_xml_subset = tmpdir_output  + os.path.sep + 'graph_xml_subset.xml'
                    output_subset_tif = tmpdir_output + os.path.sep + subband_name+ '.tif'

                    command = es_constants.gpt_exec+' '+ graph_xml_subset   #es_constants.gpt_exec
                    status=os.system(command)

                    # # ToDo : check the status or use try/except
                    if os.path.exists(output_subset_tif):
                        interm_files_list.append(output_subset_tif)
                        count = count + 1
                    else:
                        #check to stop the count loop
                        continue

            # Check at least 1 file is reprojected file is there
            if len(interm_files_list) == 0:
                my_logger.debug('No files. Return')
                return -1

        return pre_processed_list

    except:
        my_logger.error('Error in Preprocessing pre_process_snap_band_select_nc ')
        raise NameError('Error in Preprocessing pre_process_snap_band_select_nc ')
#
# def pre_process_CGLS_Resample_300_1km(subproducts, tmpdir, input_files, my_logger, in_date=None):
# # -------------------------------------------------------------------------------------------------------
# #   Pre-process the netcdf using snap - subset and merge the tiles
# #   Returns -1 if nothing has to be done on the passed files
# #
#     # Prepare the output file list
#     pre_processed_list = []
#     list_input_files = []
#
#     # Make sure input is a list (if only a string is received, it loops over chars)
#     if isinstance(input_files, list):
#         temp_list_input_files = input_files
#     else:
#         temp_list_input_files = []
#         temp_list_input_files.append(input_files)
#
#     # Check at least 1 day-time file is there
#     if len(temp_list_input_files) == 0:
#         my_logger.debug('No any file captured. Return')
#         return -1
#
#     # Loop over subproducts and extract associated files. In case of more Mapsets, more sprods exist
#     for sprod in subproducts:
#         interm_files_list = []
#         # In each unzipped folder pre-process the dataset and store the list of files to be merged
#         count =  1
#         # for input_file in temp_list_input_files:
#
#         # Define the re_expr for extracting files
#         bandname = sprod['re_extract']
#         # re_process = sprod['re_process']
#
#         output_resampled_tif = tmpdir + os.path.sep + 'resampled.nc'
#
#         # -----------------------------------------------------------------------------------------
#         # Resample 300m to  1Km using  PL code
#         # ------------------------------------------------------------------------------------------
#         from apps.tools import CGLS_ResampleTool
#
#         CGLS_ResampleTool.preprocess_CGLS_resampling(temp_list_input_files[0], tmpdir)
#
#         # # ToDo : check the status or use try/except
#         if not os.path.exists(output_resampled_tif):
#             my_logger.debug('Error in resampling. Return')
#             return -1
#
#         pre_processed_list.append(output_resampled_tif)
#         # # Check at least 1 file is reprojected file is there
#         # if len(interm_files_list) == 0:
#         #     my_logger.debug('No any file overlapping the ROI. Return')
#         #     return -1
#         #
#         # if len(interm_files_list) > 1 :
#         #     out_tmp_file_gtiff = tmpdir + os.path.sep + re_process+'_merged.tif'
#         #     input_files_str = ''
#         #     for file_add in interm_files_list:
#         #         input_files_str += ' '
#         #         input_files_str += file_add
#         #     command = 'gdalwarp -srcnodata "{}" -dstnodata "{}" -ot Float32 {} {}'.format(int(no_data), int(no_data),
#         #          input_files_str, out_tmp_file_gtiff)
#         #     # command = 'gdalwarp -srcnodata "103.69266" -dstnodata "1000" -s_srs "epsg:4326" -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
#         #     #     input_files_str, out_tmp_file_gtiff)
#         #     my_logger.info('Command for merging is: ' + command)
#         #     os.system(command)
#         #     pre_processed_list.append(out_tmp_file_gtiff)
#         # else:
#         #     pre_processed_list.append(interm_files_list[0])
#
#     return pre_processed_list

def pre_process_netcdf_VGT300(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the PROBV300 product from VGT
#   Returns -1 if nothing has to be done on the passed files
#
    # Prepare the output file list
    pre_processed_list = []
    list_input_files = []
    try:
        # Make sure input is a list (if only a string is received, it loops over chars)
        if isinstance(input_files, list):
            temp_list_input_files = input_files
        else:
            temp_list_input_files = []
            temp_list_input_files.append(input_files)
        # Check at least 1 day-time file is there
        if len(temp_list_input_files) == 0:
            my_logger.debug('No any file captured during the day. Return')
            return -1

        # Loop over subproducts and extract associated files. In case of more Mapsets, more sprods exist
        for sprod in subproducts:
            interm_files_list = []
            # In each unzipped folder pre-process the dataset and store the list of files to be merged
            for input_file in temp_list_input_files:

                # Define the re_expr for extracting files
                bandname = sprod['re_extract']
                re_process = sprod['re_process']
                subproductcode = sprod['subproduct']
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

        return pre_processed_list

    except:
        my_logger.error('Error in Preprocessing pre_process_netcdf_VGT300 ')
        raise NameError('Error in Preprocessing pre_process_netcdf_VGT300 ')


def pre_process_netcdf_s3_wst(subproducts, tmpdir, input_files, my_logger, in_date=None, data_format='TAR'):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Sentinel 3 Level 2 product from SLSTR - WST
#
#   Description: the current implementation is based on GPT, and includes the following steps
#
#       1. Unzip or untar or just copy files into a temp dir
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

    try:
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

            if data_format == 'ZIP':
                # Unzip the .tar file in 'tmpdir'
                command = 'unzip ' + input_file + ' -d ' + tmpdir + os.path.sep  # ' --strip-components 1'
                print (command)
                status = os.system(command)

            elif data_format == 'TAR':
                # Unzip the .tar file in 'tmpdir'
                command = 'tar -xvf ' + input_file + ' -C ' + tmpdir + os.path.sep  # ' --strip-components 1'
                print (command)
                status = os.system(command)

            # JEODPP EOS data: In this case we just need to copy the folder tmp dir and remaining process is carried out asusal
            else:
                tmp_img_file_path = tmpdir + os.path.sep + os.path.basename(input_file)
                shutil.copytree(input_file, tmp_img_file_path)

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
                functions.write_graph_xml_band_math_subset(output_dir=tmpdir_untar, band_name=re_process, expression='(quality_level_acceptable_quality or quality_level_best_quality) ? sea_surface_temperature : NaN')
                graph_xml_subset = tmpdir_untar_band + os.path.sep + 'graph_xml_subset.xml'
                output_subset_tif = tmpdir_untar_band + os.path.sep + 'band_subset.tif'

                command = es_constants.gpt_exec+' '+ graph_xml_subset
                print(command)
                os.system(command)

                if os.path.exists(output_subset_tif):
                    # subset_files_list.append(output_subset_tif)
                    functions.write_graph_xml_reproject(output_dir=tmpdir_untar_band, nodata_value=scaled_no_data)
                    graph_xml_reproject = tmpdir_untar_band + os.path.sep + 'graph_xml_reproject.xml'
                    output_reproject_tif = tmpdir_untar_band + os.path.sep + 'reprojected.tif'
                    command_reproject = es_constants.gpt_exec + ' ' + graph_xml_reproject
                    print(command_reproject)
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
                command = es_constants.gdal_merge + ' -of GTiff ' + '-n ' + scaled_no_data + ' -a_nodata ' + str(int(no_data)) + ' -ot Float32 ' + ' -o '  # -co \"compress=lzw\" -ot Float32  -n -32768 -a_nodata -32768

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

    except:
        my_logger.error('Error in Preprocessing pre_process_netcdf_s3_wst ')
        raise NameError('Error in Preprocessing pre_process_netcdf_s3_wst ')


def pre_process_oilspill_detection_sentinel1(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Sentinel 1 GRD product IW VV
#   Returns -1 if nothing has to be done on the passed files
#

    # Prepare the output file list
    pre_processed_list = []
    try:
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

                my_logger.info('Command for merging is: ' + command)
                os.system(command)
                pre_processed_list.append(out_tmp_file_gtiff)
            else:
                pre_processed_list.append(interm_files_list[0])

        return pre_processed_list

    except:
        my_logger.error('Error in Preprocessing pre_process_oilspill_detection_sentinel1 ')
        raise NameError('Error in Preprocessing pre_process_oilspill_detection_sentinel1 ')


def pre_process_aviso_mwind(subproducts, tmpdir, input_files, my_logger, in_date=None):
# -------------------------------------------------------------------------------------------------------
#   Pre-process the Aviso Mwind
#
    interm_files_list = []
    try:
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
                    filename = os.path.basename(input_file) + '.geotiff'
                    myfile_path = os.path.join(tmpdir, filename)
                    write_ds_to_geotiff(netcdf, myfile_path)
                    geotiff_files.append(myfile_path)

                netcdf = None

        return geotiff_files

    except:
        my_logger.error('Error in Preprocessing pre_process_oilspill_detection_sentinel1 ')
        raise NameError('Error in Preprocessing pre_process_oilspill_detection_sentinel1 ')


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
#           NETCDF_S3_WRR: TAR data format - S3A OLCI WRR data treatment using SNAP-GPT to do band subset, reproject.
#           NETCDF_S3_WRR_JEODPP :JEODPP EOS data format: S3A OLCI WRR data treatment using SNAP-GPT to do band subset, reproject.
#           NETCDF_S3_WRR_ZIP :ZIP data format  3A OLCI WRR data treatment using SNAP-GPT to do band subset, reproject.
#           NETCDF_S3_WST: TAR data format - S3A SLSTR WST data treatment using SNAP-GPT to do band subset, reproject.
#           NETCDF_S3_WST_ZIP: ZIP data format - S3A SLSTR WST data treatment using SNAP-GPT to do band subset, reproject.
#           NETCDF_S3_WST_JEODPP: JEODPP- FOLDER - FORMAT : S3A SLSTR WST data treatment using SNAP-GPT to do band subset, reproject.
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
            interm_files = pre_process_georef_netcdf(subproducts, native_mapset_code, tmpdir, input_files, my_logger)
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
            interm_files = pre_process_netcdf_s3_wrr(subproducts, tmpdir, input_files, my_logger, in_date=in_date, data_format='ZIP')

        elif preproc_type == 'NETCDF_S3_WRR':
            interm_files = pre_process_netcdf_s3_wrr(subproducts, tmpdir, input_files, my_logger, in_date=in_date, data_format='TAR')

        # JEODPP EOS data: In this case we just need to copy the folder tmp dir and remaining process is carried out asusal
        elif preproc_type == 'NETCDF_S3_WRR_JEODPP':
            interm_files = pre_process_netcdf_s3_wrr(subproducts, tmpdir, input_files, my_logger, in_date=in_date, data_format='FOLDER')

        elif preproc_type == 'NETCDF_GPT_SUBSET':
            interm_files = pre_process_netcdf_VGT300(subproducts, tmpdir, input_files, my_logger, in_date=in_date)

        elif preproc_type == 'NETCDF_S3_WST':
            interm_files = pre_process_netcdf_s3_wst(subproducts, tmpdir, input_files, my_logger, in_date=in_date, data_format='TAR')

        elif preproc_type == 'NETCDF_S3_WST_ZIP':
            interm_files = pre_process_netcdf_s3_wst(subproducts, tmpdir, input_files, my_logger, in_date=in_date, data_format='ZIP')

        elif preproc_type == 'NETCDF_S3_WST_JEODPP':
            interm_files = pre_process_netcdf_s3_wst(subproducts, tmpdir, input_files, my_logger, in_date=in_date, data_format='FOLDER')

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
        # elif preproc_type == 'CGLS_Resample_300_1Km':
        #     interm_files = pre_process_CGLS_Resample_300_1km(subproducts, tmpdir, input_files, my_logger, in_date=in_date)

        elif preproc_type == 'SNAP_BAND_SELECT_NC':
            interm_files = pre_process_snap_band_select_nc(subproducts, tmpdir, input_files, my_logger, in_date=in_date)

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

    set_geoTransform_projection(native_mapset_code, georef_already_done, list_interm_files, my_logger)
    # # Create native mapset (or assign as empty string)
    # if native_mapset_code != 'default' and (not georef_already_done):
    #
    #     # Create Mapset object and test
    #     native_mapset = mapset.MapSet()
    #     native_mapset.assigndb(native_mapset_code)
    #     my_logger.debug('Native mapset IS passed: ' + native_mapset.short_name)
    #
    #     if native_mapset.validate():
    #         my_logger.error('Native mapset passed is invalid: ' + native_mapset.short_name)
    #         return 1
    #     # Loop over interm_files and assign mapset
    #     for intermFile in list_interm_files:
    #         my_logger.debug('Intermediate file: ' + intermFile)
    #
    #         # Open input dataset in update mode
    #         orig_ds = gdal.Open(intermFile, gdal.GA_Update)
    #
    #         # Test result: in case of error (e.g. for nc files, it does not raise exception)
    #         # If wrong -> Open input dataset in read-only
    #         if orig_ds is None:
    #             orig_ds = gdal.Open(intermFile, gdal.GA_ReadOnly)
    #
    #         # Otherwise read from native_mapset, and assign to ds
    #         orig_cs = native_mapset.spatial_ref
    #         orig_geo_transform = native_mapset.geo_transform
    #         orig_size_x = native_mapset.size_x
    #         orig_size_y = native_mapset.size_y
    #
    #         orig_ds.SetGeoTransform(native_mapset.geo_transform)
    #         orig_ds.SetProjection(native_mapset.spatial_ref.ExportToWkt())
    # #         TODO orig_ds = None needed?

    return list_interm_files

def set_geoTransform_projection(native_mapset_code, georef_already_done, list_interm_files, my_logger):
    try:
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
                # TODO I guess this is useless here?
                # orig_cs = native_mapset.spatial_ref
                # orig_geo_transform = native_mapset.geo_transform
                # orig_size_x = native_mapset.size_x
                # orig_size_y = native_mapset.size_y

                orig_ds.SetGeoTransform(native_mapset.geo_transform)
                orig_ds.SetProjection(native_mapset.spatial_ref.ExportToWkt())
                #         TODO orig_ds = None needed?
                # orig_ds = None
    except:
        my_logger.error('Error in assigning geotransform projection. Exit')
        raise NameError('Error in assigning geotransform projection')

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
    try:
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

    except:
        # my_logger.error('Error in subprocess of preprocess write_ds_to_geotiff ')
        raise NameError('Error in subprocess of preprocess write_ds_to_geotiff ')


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
    try:
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

    except:
        # my_logger.error('Error in subprocess of preprocess write_ds_and_mapset_to_geotiff ')
        raise NameError('Error in subprocess of preprocess write_ds_and_mapset_to_geotiff ')

def mosaic_lsasaf_msg(in_files, output_file, format):
#
#   Puts together the LSASAF regions (in the original 'disk' projection)
#   Args:
#       in_files: input filenames
#       output_file: target output file
#
   # Note: noData==-1 for LSASAF Products (both ET and LST)
    NO_DATA_LSASAF_PRODS = -1
    try:
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

    except:
        # my_logger.error('Error in subprocess of preprocess write_ds_and_mapset_to_geotiff ')
        raise NameError('Error in subprocess of preprocess mosaic_lsasaf_msg ')
#
#   Converts the string data type to numpy types
#   \type: data type in wkt-estation format (inherited from 1.X)
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
#   \type: data type in wkt-estation format (inherited from 1.X)
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

