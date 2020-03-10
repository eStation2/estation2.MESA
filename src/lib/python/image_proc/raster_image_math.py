from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from past.utils import old_div
__author__ = 'clerima'
#
#	purpose: Define a set of simple mathematical functions for processing raster images
#	author:  M.Clerici
#	date:	 17.06.2014
#   descr:	 Define a set of simple mathematical functions for processing images, mainly derived for the
#            dedicated functions implemented in eStation 1.0 (e.g. avg.py).
#            Images are simply treated as arrays (no any geo-processing)
#	history: 1.0
#   common args:    input_files     -> one or more inputs (single file in internally forced to a list type)
#                   output_files    -> one (or more?) outputs
#
#   common options: input_nodata    -> value to be considered as nodata in input_files
#                   output_nodata   -> value to be considered as nodata in output_files
#                   format          -> file format (default: GTIFF)
#                   output_type     -> data type in output (as input, if missing)
#
#   contents:       do_avg_image()  -> compute avg over list of images
#                   do_min_image()  -> compute min over list of images (TODO-M.C.: implement 'update' option)
#                   do_max_image()  -> compute max over list of images (TODO-M.C.: implement 'update' option)
#
#   General Notes on 'nodata':  they might be different in input and output files, at least for functions that
#                               create the output file(s) every time (no upgrade).
#                               E.g. -9999 in the input file might be recoded to -10000 in the output
#
#                               Nevertheless if input_nodata is <def> and output_nodata is <undef> the latter is assigned
#                               to the value of inputs.
#
#                               In functions like <min>, <max> in the loop over files we update an output if we find
#                               a <valid> data to replace a <nodata>
#

# import standard modules
import math
# Import eStation lib modules
from lib.python import es_logging as log
from lib.python import metadata
from lib.python import mapset
from lib.python import functions
from config import es_constants
from database import querydb

# Import third-party modules
from osgeo.gdalconst import *
from osgeo import gdal, osr
import numpy as N
import copy
import os, re, os.path, time, sys
# import pymorph
import tempfile
import shutil
# Jur: not working in windows version. Conflict with scipy version 1.1.0 and its ndimage functionality.
# I tried to install scipy version 0.15.1 but need older numpy version 1.19.2 (numpy 1.11.0 is installed)
# installing numpy 1.19.2 gives problems with installed gdal version 2.1.2)
# scipy for chla gradient computation
# TODO: On reference machines it has to be -> from scipy import ndimage ! Not on our development VMs!
# TODO: Change to  if sys.platform == 'win32':
# if sys.platform == 'win32':
#     import scipy
# else:
#     from scipy import ndimage

logger = log.my_logger(__name__)


# _____________________________
def do_avg_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
                 output_type=None, options='', output_stddev=None):
    # Note: no 'update' functionality is foreseen -> creates output EVERY TIME
    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Force input to be a list
        input_list = return_as_list(input_file)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_list[0]):
                input_nodata=float(sds_meta.get_nodata_value(input_list[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Get info from first file
        fidT = gdal.Open(input_list[0], GA_ReadOnly)
        nb = fidT.RasterCount
        ns = fidT.RasterXSize
        nl = fidT.RasterYSize
        dataType = fidT.GetRasterBand(1).DataType
        geotransform = fidT.GetGeoTransform()
        projection = fidT.GetProjection()
        driver_type = fidT.GetDriver().ShortName

        # manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output/sll
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetProjection(projection)
        outDS.SetGeoTransform(geotransform)

        if output_stddev != None:
            outStd = gdal.GetDriverByName(output_format)
            stdDs = outStd.Create(output_stddev, ns, nl, nb, outType, options_list)
            stdDs.SetProjection(projection)
            stdDs.SetGeoTransform(geotransform)

        # pre-open input files
        rangenl = list(range(nl))
        rangeFile = list(range(len(input_list)))
        fid = []
        for ifid in rangeFile:
            fid.append(gdal.Open(input_list[ifid], GA_ReadOnly))

        # Loop over bands
        for ib in range(nb):
            outband = outDS.GetRasterBand(ib + 1)

            # parse image by line
            for il in rangenl:
                counter = N.zeros(ns)
                accum = N.zeros(ns)
                # for all files:
                for ifile in rangeFile:
                    data = N.ravel(fid[ifile].GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1).astype(float))

                    # variable initialization
                    if (ifile == 0):
                        if input_nodata is None:
                            avgData = data
                            stdData = N.multiply(data, data)
                            counter[:] = 1.0
                        else:
                            wts = (data != input_nodata)
                            avgData = N.zeros(data.shape)
                            stdData = N.zeros(data.shape)
                            if wts.any():
                                counter[wts] = 1.0
                                avgData[wts] = data[wts]
                                stdData[wts] = N.multiply(data[wts], data[wts])

                    else:
                        if input_nodata is None:
                            avgData = avgData + data
                            counter = counter + 1.0
                            stdData = stdData + N.multiply(data, data)
                        else:
                            wts = (data != input_nodata)
                            if wts.any():
                                avgData[wts] = avgData[wts] + data[wts]
                                counter[wts] = counter[wts] + 1.0
                                stdData[wts] = stdData[wts] + N.multiply(data[wts], data[wts])

                wnz = (counter != 0)
                outData = N.zeros(ns)
                if wnz.any():
                    outData[wnz] = old_div(avgData[wnz], (counter[wnz]))

                if output_nodata != None:
                    wzz = (counter == 0)
                    if wzz.any():
                        outData[wzz] = output_nodata

                # Check if stddev also required
                if output_stddev != None:
                    outDataStd = N.zeros(ns)
                    if wnz.any():
                        outDataStd[wnz] = N.sqrt(old_div(stdData[wnz], (counter[wnz])) - N.multiply(outData[wnz], outData[wnz]))
                    if output_nodata != None:
                        wzz = (counter == 0)
                        if wzz.any():
                            outDataStd[wzz] = output_nodata

                    outDataStd.shape = (1, -1)
                    stdDs.GetRasterBand(ib + 1).WriteArray(N.array(outDataStd), 0, il)

                # reshape before writing
                outData.shape = (1, -1)
                outband.WriteArray(N.array(outData), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None

        #   Writes metadata to output
        assign_metadata_processing(input_list, output_file)

    except:
        logger.warning('Error in do_avg_image. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
        if output_stddev != None:
            if os.path.isfile(output_stddev):
                os.remove(output_stddev)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_stddev_image(input_file='', avg_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', output_stddev=''):

    # Note: no 'update' functionality is foreseen -> creates output EVERY TIME
    # In this method make sure you pass the output_file as avg_file and output_stddev as output file to ease calculation
    # The method is corrected on 27.06.19 (see ES2-400) with the following logic:
    #   1. LTA is passed as mandatory input and it is used for the computation
    #   2. The original procedure is changed, since the upper-rounding of the LTA leads to negative values in the term:
    #      stdData[wnz]/(counter[wnz]) - N.multiply(avgVal[wnz],avgVal[wnz]) !!!

    # debug = True
    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_stddev),
                                  dir=es_constants.base_tmp_dir)
        # Force input to be a list
        input_list = return_as_list(input_file)

        output_file_final =  output_stddev
        output_stddev = tmpdir + os.sep +os.path.basename(output_stddev)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # get infos from the last file (to manage case of 'upgraded' DataType - e.g. FEWSNET).
        nFiles = len(input_list)
        fidT = gdal.Open(input_list[nFiles - 1], GA_ReadOnly)
        nb = fidT.RasterCount
        ns = fidT.RasterXSize
        nl = fidT.RasterYSize
        dataType = fidT.GetRasterBand(1).DataType
        geotransform = fidT.GetGeoTransform()
        projection = fidT.GetProjection()
        driver_type = fidT.GetDriver().ShortName

        # Get info from avg file
        if avg_file is not None and os.path.exists(avg_file):
                avgFID = gdal.Open(avg_file, GA_ReadOnly)
        else:
            logger.error('Avg file does not existing: cannot proceed. Exit')
            return

        # manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # Instanciate output for STD
        outStd = gdal.GetDriverByName(output_format)
        stdDs = outStd.Create(output_stddev, ns, nl, nb, outType, options_list)
        stdDs.SetProjection(projection)
        stdDs.SetGeoTransform(geotransform)

        # pre-open files, to speed up processing
        fid = []
        for ii in range(len(input_file)):
            fid.append(gdal.Open(input_file[ii], GA_ReadOnly))
        # pre-open input files
        rangenl = list(range(nl))
        rangeFile = list(range(len(input_file)))

        # Loop over bands
        for ib in range(nb):
            inavg = avgFID.GetRasterBand(ib+1)

            # parse image by line
            for il in rangenl:
                counter = N.zeros(ns)
                # for all files:
                for ifile in rangeFile:
                    data = N.ravel(fid[ifile].GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1).astype(float))
                    # if debug:  print data[ipix]  # debug only
                    avgVal = N.ravel(inavg.ReadAsArray(0, il, inavg.XSize, 1).astype(float))
                    # if debug:  print avgVal[ipix] # debug only
                    # variable initialization
                    if (ifile == 0):
                        if input_nodata is None:
                            stdData = N.multiply(data , data)
                            counter[:] = 1.0
                        else:
                            wts = (data != input_nodata) *  (avgVal != input_nodata)
                            stdData = N.zeros(data.shape)
                            if wts.any():
                                counter[wts] = 1.0
                                stdData[wts] = N.multiply(data[wts] - avgVal[wts], data[wts]- avgVal[wts])

                    else:
                        if input_nodata is None:
                            counter = counter + 1.0
                            stdData = stdData + N.multiply(data, data)
                        else:
                            wts = (data != input_nodata) * (avgVal != input_nodata)
                            if wts.any():
                                counter[wts] = counter[wts] + 1.0
                                stdData[wts] = stdData[wts] + N.multiply(data[wts] - avgVal[wts], data[wts]- avgVal[wts])

                wnz = (counter != 0)
                outData = N.zeros(ns)

                if output_nodata != None:
                    wzz = (counter == 0)
                    if wzz.any():
                        outData[wzz] = output_nodata

                # Check if stddev also required
                outDataStd = N.zeros(ns)
                outDataStd_2 = N.zeros(ns)
                if wnz.any():
                    outDataStd_2[wnz] = old_div(stdData[wnz],(counter[wnz]))
                    neg_val = (outDataStd < 0.0)
                    if neg_val.any():
                        logger.error('Unconsistent results. Check AVG is up-to-date. Continue')
                    outDataStd[wnz] = N.sqrt(outDataStd_2[wnz])

                    # if debug: print stdData[ipix], counter[ipix], avgVal[ipix], outDataStd[ipix]
                if output_nodata != None:
                    wzz = (counter == 0)
                    if wzz.any():
                        outDataStd[wzz] = output_nodata

                outDataStd.shape = (1, -1)
                stdDs.GetRasterBand(ib+1).WriteArray(N.array(outDataStd), 0, il)

                # reshape before writing
                # outData.shape = (1, -1)
                # outband.WriteArray(N.array(outData), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outStd = None
        stdDs = None

        #   Writes metadata to output
        assign_metadata_processing(input_file, output_stddev)

    except:
        logger.warning('Error in do_stddev_image. Remove outputs')
        # if os.path.isfile(output_file):
        #     os.remove(output_file)
        # if output_stddev != None:
        if os.path.isfile(output_stddev):
            os.remove(output_stddev)

    else:
        shutil.move(output_stddev, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_min_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
                 output_type=None, options='', index_file=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    #       'The optional index file will store the file index (position in input-list) used for the minimum.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Force input to be a list
        input_list = return_as_list(input_file)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # get infos from the last file (to manage case of 'upgraded' DataType - e.g. FEWSNET).
        nFiles = len(input_list)
        f1Fid = gdal.Open(input_list[nFiles - 1], GA_ReadOnly)
        nb = f1Fid.RasterCount
        ns = f1Fid.RasterXSize
        nl = f1Fid.RasterYSize
        dataType = f1Fid.GetRasterBand(1).DataType
        geoTransform = f1Fid.GetGeoTransform()
        projection = f1Fid.GetProjection()
        driver_type = f1Fid.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_list[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_list[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output(s)
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)
        if (index_file is None):
            indexDS = None
        else:
            indexDrv = gdal.GetDriverByName(outFormat)
            indexDS = outDrv.Create(index_file, ns, nl, nb, GDT_Int16, options_list)
            indexDS.SetGeoTransform(geoTransform)
            indexDS.SetProjection(projection)

        # pre-open files, to speed up processing
        fidList = []
        for ii in range(len(input_file)):
            fidList.append(gdal.Open(input_file[ii], GA_ReadOnly))

        for ib in range(nb):
            outband = outDS.GetRasterBand(ib + 1)
            if index_file is not None:
                indexBand = indexDS.GetRasterBand(ib + 1)

            for il in range(nl):

                for ifile in range(len(input_file)):
                    fid = fidList[ifile]
                    data = N.ravel(fid.GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1).astype(float))

                    if (ifile == 0):
                        # initial value set on first file
                        minData = data
                        if (input_nodata is None):
                            indexData = N.zeros(ns)
                        else:
                            indexData = N.zeros(ns) - 1
                            wtp = (minData != input_nodata)
                            if wtp.any():
                                indexData[wtp] = ifile

                    else:
                        if (input_nodata is None):
                            wtp = (data < minData)
                            if wtp.any():
                                minData[wtp] = data[wtp]
                                indexData[wtp] = ifile

                        else:
                            wtp = (data < minData) * (data != input_nodata)
                            # can we find a value to replace a no data?
                            wtf = (minData == output_nodata) * (data != input_nodata)

                            if wtp.any():
                                minData[wtp] = data[wtp]
                                indexData[wtp] = ifile

                            if wtf.any():
                                minData[wtf] = data[wtf]
                                indexData[wtf] = ifile

                minData.shape = (1, -1)
                indexData.shape = (1, -1)

                outband.WriteArray(N.array(minData), 0, il)
                if indexDS is not None:
                    # indexBand.WriteArray(gdalnumeric.array(indexData), 0, il)
                    indexBand.WriteArray(N.array(indexData), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None
        #   Writes metadata to output
        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_min_image. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_max_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
                 output_type=None, options='', index_file=None, min_num_valid=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    #       'The optional index file will store the file index (position in input-list) used for the minimum.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Force input to be a list
        input_list = return_as_list(input_file)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # get infos from the last file (to manage case of 'upgraded' DataType - e.g. FEWSNET).
        nFiles = len(input_list)
        f1Fid = gdal.Open(input_list[nFiles - 1], GA_ReadOnly)
        nb = f1Fid.RasterCount
        ns = f1Fid.RasterXSize
        nl = f1Fid.RasterYSize
        dataType = f1Fid.GetRasterBand(1).DataType
        geoTransform = f1Fid.GetGeoTransform()
        projection = f1Fid.GetProjection()
        driver_type = f1Fid.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_list[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_list[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output(s)
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)
        if (index_file is None):
            indexDS = None
        else:
            indexDrv = gdal.GetDriverByName(outFormat)
            indexDS = outDrv.Create(index_file, ns, nl, nb, GDT_Int16, options_list)
            indexDS.SetGeoTransform(geoTransform)
            indexDS.SetProjection(projection)

        # pre-open files, to speed up processing
        fidList = []
        for ii in range(len(input_file)):
            fidList.append(gdal.Open(input_file[ii], GA_ReadOnly))

        for ib in range(nb):
            outband = outDS.GetRasterBand(ib + 1)
            if index_file is not None:
                indexBand = indexDS.GetRasterBand(ib + 1)

            for il in range(nl):
                counter = N.zeros(ns)
                for ifile in range(len(input_file)):
                    fid = fidList[ifile]
                    data = N.ravel(fid.GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1).astype(float))

                    if (ifile == 0):
                        maxData = data
                        if (input_nodata is None):
                            indexData = N.zeros(ns)
                            counter[:] = 1.0
                        else:
                            indexData = N.zeros(ns) - 1
                            wtp = (maxData != input_nodata)
                            if wtp.any():
                                indexData[wtp] = ifile
                                counter[wtp] = 1.0
                    else:
                        if (input_nodata is None):
                            wtp = (data > maxData)
                            counter[:] = counter[:] + 1.0

                            if wtp.any():
                                maxData[wtp] = data[wtp]
                                indexData[wtp] = ifile

                        else:
                            wtp = (data > maxData) * (data != input_nodata)
                            # replace nodata with data
                            wtf = (maxData == input_nodata) * (data != input_nodata)
                            if wtp.any():
                                maxData[wtp] = data[wtp]
                                indexData[wtp] = ifile
                            if wtf.any():
                                maxData[wtf] = data[wtf]
                                indexData[wtf] = ifile
                            # add valid pixels to count
                            wts = (data != input_nodata)
                            if wts.any():
                                counter[wts] = counter[wts] + 1.0

                # manage 'minvalid' option
                if min_num_valid is not None:
                    wtb = (counter < min_num_valid)
                    if wtb.any():
                        maxData[wtb] = output_nodata

                maxData.shape = (1, -1)
                indexData.shape = (1, -1)
                outband.WriteArray(N.array(maxData), 0, il)
                if indexDS is not None:
                    indexBand.WriteArray(N.array(indexData), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None
        #   Writes metadata to output
        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_max_image. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)
#   _____________________________
def do_med_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
                 output_type=None, options='', min_num_valid=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??
    # TODO-M.C.: : NODATA now are considered as 'normal' values ... should be removed !

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Force input to be a list
        input_list = return_as_list(input_file)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # get infos from the last file (to manage case of 'upgraded' DataType - e.g. FEWSNET).
        nFiles = len(input_list)
        f1Fid = gdal.Open(input_list[nFiles - 1], GA_ReadOnly)
        nb = f1Fid.RasterCount
        ns = f1Fid.RasterXSize
        nl = f1Fid.RasterYSize
        dataType = f1Fid.GetRasterBand(1).DataType
        geoTransform = f1Fid.GetGeoTransform()
        projection = f1Fid.GetProjection()
        driver_type = f1Fid.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_list[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_list[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output(s)
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # pre-open files, to speed up processing
        fidList = []
        for ii in range(len(input_list)):
            fidList.append(gdal.Open(input_file[ii], GA_ReadOnly))

        for ib in range(nb):
            outband = outDS.GetRasterBand(ib + 1)

            # Do a line at a time ...
            for il in range(nl):

                accum = N.zeros((len(input_list), ns))

                for ifile in range(len(input_file)):
                    fid = fidList[ifile]
                    data = N.ravel(fid.GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1).astype(float))

                    accum[ifile, :] = data

                try:
                    medianOut = N.median(accum, axis=0)
                except:
                    medianOut = N.median(accum)

                # # manage 'minvalid' option
                # if min_num_valid is not None:
                #     wtb = (counter < min_num_valid)
                #     if wtb.any():
                #         maxData[wtb] = output_nodata

                medianOut.shape = (1, -1)
                outband.WriteArray(N.array(medianOut), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None
        #   Writes metadata to output
        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_med_image. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_oper_subtraction(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
                        output_type=None, options=''):
    #
    # Notes:'The command expects exactly 2 files in input.'

    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Open input files
        fid0 = gdal.Open(input_file[0], GA_ReadOnly)
        fid1 = gdal.Open(input_file[1], GA_ReadOnly)

        # Read info from file1
        nb = fid0.RasterCount
        ns = fid0.RasterXSize
        nl = fid0.RasterYSize
        dataType = fid0.GetRasterBand(1).DataType
        geoTransform = fid0.GetGeoTransform()
        projection = fid0.GetProjection()
        driver_type = fid0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # manage out_type (take the input one as default, but ensure a SIGNED type is used)
        if output_type is None:
            if dataType == GDT_Byte:
                outType = GDT_Int16
            elif dataType == GDT_UInt16:
                outType = GDT_Int16
            elif dataType == GDT_UInt32:
                outType = GDT_Int32
            else:
                outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        for ib in range(nb):
            for il in range(nl):
                data0 = N.ravel(fid0.GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1)).astype(float)
                data1 = N.ravel(fid1.GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1)).astype(float)

                if input_nodata is None:
                    dataout = data0 - data1
                else:
                    if input_nodata is None:
                        dataout = N.zeros(ns)
                    else:
                        dataout = N.zeros(ns) + output_nodata

                    wtc = (data0 != input_nodata) * (data1 != input_nodata)
                    if wtc.any():
                        dataout[wtc] = data0[wtc] - data1[wtc]

                dataout.shape = (1, -1)
                outDS.GetRasterBand(ib + 1).WriteArray(N.array(dataout), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None
        #   Writes metadata to output
        assign_metadata_processing(input_file, output_file)

    except:
        logger.warning('Error in do_oper_subtraction. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_oper_division_perc(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
                          output_type=None, options=''):
    # Returns the IN1/IN2 * 100; IN1/IN2 might have various datatype (int, float, ...) but internally treated as float
    # Notes:'The command expects exactly 2 files in input.'
    epsilon = 1e-10

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Open input files
        fid0 = gdal.Open(input_file[0], GA_ReadOnly)
        fid1 = gdal.Open(input_file[1], GA_ReadOnly)

        # Read info from file1
        nb = fid0.RasterCount
        ns = fid0.RasterXSize
        nl = fid0.RasterYSize
        dataType = fid0.GetRasterBand(1).DataType
        geoTransform = fid0.GetGeoTransform()
        projection = fid0.GetProjection()
        driver_type = fid0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        # TODO-M.C. Replace by calling ReturnNoData
        if input_nodata is None:
            input_nodata = -32768.0

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        for ib in range(nb):
            for il in range(nl):
                data0 = N.ravel(fid0.GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1)).astype(float)
                data1 = N.ravel(fid1.GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1)).astype(float)

                if input_nodata is None:
                    wtc = (N.abs(data1) > epsilon)
                else:
                    wtc = (data0 != input_nodata) * (data1 != input_nodata) * (N.abs(data1) > epsilon)

                # TODO-M.C.: check this assignment is done for the other functions as well
                dataout = N.zeros(ns).astype(float)
                if output_nodata is not None:
                    dataout = N.zeros(ns).astype(float) + output_nodata

                if wtc.any():
                    dataout[wtc] = data0[wtc]*100.00/data1[wtc]
                    # dataout[wtc] = dataout[wtc]


                dataout = dataout.round()
                dataout.shape = (1, -1)
                outDS.GetRasterBand(ib + 1).WriteArray(N.array(dataout), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None
        #   Writes metadata to output
        assign_metadata_processing(input_file, output_file)
    except:
        logger.warning('Error in do_oper_division_perc. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)
# _____________________________
def do_oper_scalar_multiplication(input_file='', output_file='', scalar=1, input_nodata=None, output_nodata=None,
                                  output_format=None,
                                  output_type=None, options=''):
    #
    # Notes:'The command expects exactly 1 file in input.'

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Open input file
        fid0 = gdal.Open(input_file[0], GA_ReadOnly)

        # Read info from file
        nb = fid0.RasterCount
        ns = fid0.RasterXSize
        nl = fid0.RasterYSize
        dataType = fid0.GetRasterBand(1).DataType
        geoTransform = fid0.GetGeoTransform()
        projection = fid0.GetProjection()
        driver_type = fid0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        scalarArray = N.zeros(ns) + scalar

        for ib in range(nb):
            for il in range(nl):
                data0 = N.ravel(fid0.GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1)).astype(float)

                if input_nodata is None:
                    dataout = data0 * scalarArray
                else:
                    wtc = (data0 != input_nodata)
                    dataout = N.zeros(ns)
                    if input_nodata is not None:
                        dataout = N.zeros(ns) + output_nodata
                    if wtc.any():
                        dataout[wtc] = data0[wtc] * scalarArray[wtc]

                dataout.shape = (1, -1)
                outDS.GetRasterBand(ib + 1).WriteArray(N.array(dataout), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None
        #   Writes metadata to output
        assign_metadata_processing(input_file, output_file)
    except:
        logger.warning('Error in do_oper_scalar_multiplication. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_make_vci(input_file='', min_file='', max_file='', output_file='', input_nodata=None, output_nodata=None,
                output_format=None,
                output_type=None, options=''):
    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # open files
        fileFID = gdal.Open(input_file, GA_ReadOnly)
        minFID = gdal.Open(min_file, GA_ReadOnly)
        maxFID = gdal.Open(max_file, GA_ReadOnly)

        # Read info from file
        nb = fileFID.RasterCount
        ns = fileFID.RasterXSize
        nl = fileFID.RasterYSize
        dataType = fileFID.GetRasterBand(1).DataType
        geoTransform = fileFID.GetGeoTransform()
        projection = fileFID.GetProjection()
        driver_type = fileFID.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file):
                input_nodata = float(sds_meta.get_nodata_value(input_file))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        indata = fileFID.GetRasterBand(1)
        inmin = minFID.GetRasterBand(1)
        inmax = maxFID.GetRasterBand(1)

        for il in range(fileFID.RasterYSize):
            data = N.ravel(indata.ReadAsArray(0, il, indata.XSize, 1))
            minVal = N.ravel(inmin.ReadAsArray(0, il, inmin.XSize, 1))
            maxVal = N.ravel(inmax.ReadAsArray(0, il, inmax.XSize, 1))

            datatype = data.dtype
            if input_nodata is None:
                dataout = N.zeros(ns)
            else:
                dataout = N.zeros(ns) + output_nodata

            if input_nodata is not None:
                wtp = (minVal != output_nodata) * (maxVal != output_nodata) * (maxVal != minVal)
            else:
                wtp = (maxVal != minVal)

            vci = N.zeros(indata.XSize)

            if output_nodata is not None:
                vci = vci + output_nodata

            if wtp.any():
                vci[wtp] = old_div(100.0 * (1.0 * data[wtp] - 1.0 * minVal[wtp]), (1.0 * maxVal[wtp] - 1.0 * minVal[wtp]))

            vci = vci.round()
            vci.shape = (1, -1)
            vciout = N.array(vci).astype(int)

            outband.WriteArray(vciout, 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Writes metadata to output
        input_list = []
        input_list.append(input_file)
        input_list.append(min_file)
        input_list.append(max_file)
        #   Close outputs
        outDrv = None
        outDS = None
        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_make_vci. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_make_baresoil(input_file='', avg_file='', min_file='', max_file='', output_file='', input_nodata=None,
                     output_nodata=None, output_format=None,
                     output_type=None, options='', delta_ndvi_max=0.15, ndvi_max=0.14):
    #
    #   Compute a mask for identifying 'baresoil' from a single NDVI image and LT stats
    #
    #   Conditions for classification as baresoil are:
    #
    #   1. curr_NDVI < NDVImax
    #   2. deltaNDVI < deltaNDVImax
    #   3. meanNDVI  < NDVImax
    #
    #   Condition 1. apply always, 2. if min/max files are provided, and 3. if avg file is provided
    #   Conditions apply in AND, e.g. if avg is provided (standard case) baresoil is identified where:
    #
    #               curr_NDVI < NDVImax  AND meanNDVI  < NDVImax
    #
    #   leading to a less extended baresoil region, so that more anomalies are identified.
    #
    #   Output: 0 (or output_nodata)-> baresoil/no-data, 1 -> vegetated
    #   Note: nodata are considered only in the NDVIcurr file (NOT in min/max).
    #
    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # open files
        fileFID = gdal.Open(input_file, GA_ReadOnly)
        if min_file != '' and max_file != '':
            minFID = gdal.Open(min_file, GA_ReadOnly)
            maxFID = gdal.Open(max_file, GA_ReadOnly)

        if avg_file != '':
            avgFID = gdal.Open(avg_file, GA_ReadOnly)

        # Read info from file
        nb = fileFID.RasterCount
        ns = fileFID.RasterXSize
        nl = fileFID.RasterYSize
        dataType = fileFID.GetRasterBand(1).DataType
        geoTransform = fileFID.GetGeoTransform()
        projection = fileFID.GetProjection()
        driver_type = fileFID.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file):
                input_nodata = float(sds_meta.get_nodata_value(input_file))
                [scaling_factor, scaling_offset] = sds_meta.get_scaling_values(input_file)
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Convert the physical thresholds (ndvi_max, delta_ndvi_max) in DN equivalent
        if os.path.exists(input_file):
            input_nodata = float(sds_meta.get_nodata_value(input_file))
            [scaling_factor, scaling_offset] = sds_meta.get_scaling_values(input_file)
            ndvi_max_dn = old_div((ndvi_max - scaling_offset), scaling_factor)
            delta_ndvi_max_dn = old_div((delta_ndvi_max - scaling_offset), scaling_factor)

        else:
            logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        indata = fileFID.GetRasterBand(1)
        if min_file != '' and max_file != '':
            inmin = minFID.GetRasterBand(1)
            inmax = maxFID.GetRasterBand(1)
            logger.info('Using NDVI val and NDVI-delta')

        if avg_file != '':
            inavg = avgFID.GetRasterBand(1)
            logger.info('Using NDVI val and NDVI-average')

        for il in range(fileFID.RasterYSize):
            data = N.ravel(indata.ReadAsArray(0, il, indata.XSize, 1))
            if min_file != '' and max_file != '':
                minVal = N.ravel(inmin.ReadAsArray(0, il, inmin.XSize, 1))
                maxVal = N.ravel(inmax.ReadAsArray(0, il, inmax.XSize, 1))
                deltaVal = maxVal - minVal

            if avg_file != '':
                avgVal = N.ravel(inavg.ReadAsArray(0, il, inavg.XSize, 1))

            datatype = data.dtype
            if input_nodata is None:
                dataout = N.zeros(ns)
            else:
                dataout = N.zeros(ns) + output_nodata

            # Identify 'bare' pixels (or nodata)
            if min_file != '' and max_file != '':
                w_bare = (data < ndvi_max_dn) * (deltaVal < delta_ndvi_max_dn)
            elif avg_file != '':
                w_bare = (data < ndvi_max_dn) * (avgVal < ndvi_max_dn)
            else:
                w_bare = (data < ndvi_max_dn)

            if input_nodata is not None:
                w_nodata = (data == input_nodata)

            # Initializa output to 1 (vgt)
            mask = N.ones(indata.XSize)

            if output_nodata is not None:
                output_value = output_nodata
            else:
                output_value = 1

            if w_bare.any():
                mask[w_bare] = output_value

            if input_nodata is not None:
                if w_nodata.any():
                    mask[w_nodata] = output_value

            mask.shape = (1, -1)
            maskout = N.array(mask).astype(int)
            outband.WriteArray(mask, 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Writes metadata to output
        input_list = []
        input_list.append(input_file)
        if min_file != '':
            input_list.append(min_file)
        if max_file != '':
            input_list.append(max_file)
        #   Close outputs
        outDrv = None
        outDS = None

        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_make_baresoil. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_mask_image(input_file='', mask_file='', output_file='', output_format=None,
                  output_type=None, options='', mask_value=1, out_value=0):
    # _____________________________
    #
    #   Copy input to output, by setting to out_value all pixel where mask=mask_value
    #

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # open files
        fileFID = gdal.Open(input_file, GA_ReadOnly)
        maskFID = gdal.Open(mask_file, GA_ReadOnly)

        # Read info from file
        nb = fileFID.RasterCount
        ns = fileFID.RasterXSize
        nl = fileFID.RasterYSize
        dataType = fileFID.GetRasterBand(1).DataType
        geoTransform = fileFID.GetGeoTransform()
        projection = fileFID.GetProjection()
        driver_type = fileFID.GetDriver().ShortName

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        indata = fileFID.GetRasterBand(1)
        inmask = maskFID.GetRasterBand(1)

        for il in range(fileFID.RasterYSize):
            data = N.ravel(indata.ReadAsArray(0, il, indata.XSize, 1))
            maskVal = N.ravel(inmask.ReadAsArray(0, il, inmask.XSize, 1))

            datatype = data.dtype

            wtp = (maskVal == mask_value)

            output = data
            if wtp.any():
                output[wtp] = out_value

            output.shape = (1, -1)

            outband.WriteArray(output, 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Writes metadata to output
        input_list = []
        input_list.append(input_file)
        input_list.append(mask_file)
        #   Close outputs
        outDrv = None
        outDS = None
        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_mask_image. Remove outputs')
        if os.path.isfile(output_file):
            outDrv = None
            outDS = None
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_cumulate(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
                output_type=None, options='', output_stddev=None, scale_factor=None):
    # Notes:'The command expects exactly 1 file in input.'

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Open input file
        fid0 = gdal.Open(input_file[0], GA_ReadOnly)

        # Read info from file
        nb = fid0.RasterCount
        ns = fid0.RasterXSize
        nl = fid0.RasterYSize
        dataType = fid0.GetRasterBand(1).DataType
        geoTransform = fid0.GetGeoTransform()
        projection = fid0.GetProjection()
        driver_type = fid0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate outputs
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetProjection(projection)
        outDS.SetGeoTransform(geoTransform)

        # TODO-M.C.: is that to be implemented ? ever used ?
        # if statusmapOut is not None:
        #     outSMDrv = gdal.GetDriverByName(format)
        #     smDs = outSMDrv.Create(statusmapOut, ns, nl, nb, ParseType('UInt16'), options)
        #     smDs.SetProjection(projection)
        #     smDs.SetGeoTransform(geotransform)

        # pre-open the files
        rangenl = list(range(nl))
        rangeFile = list(range(len(input_file)))
        fid = []
        for ifid in rangeFile:
            fid.append(gdal.Open(input_file[ifid], GA_ReadOnly))

        for ib in range(nb):
            outband = outDS.GetRasterBand(ib + 1)

            # parse image by line
            for il in rangenl:
                counter = N.zeros(ns)

                # for all files:
                for ifile in rangeFile:
                    data = N.ravel(fid[ifile].GetRasterBand(ib + 1).ReadAsArray(0, il, ns, 1).astype(float))

                    if (ifile == 0):
                        cumData = data
                        if input_nodata is None:
                            counter[:] = 1.0
                        else:
                            wts = (data != input_nodata)
                            cumData = N.zeros(ns)
                            if wts.any():
                                counter[wts] = 1.0
                                cumData[wts] = data[wts]

                    else:
                        if input_nodata is None:
                            cumData = cumData + data
                            counter = counter + 1.0
                        else:
                            wts = (data != input_nodata)
                            if wts.any():
                                cumData[wts] = cumData[wts] + data[wts]
                                counter[wts] = counter[wts] + 1.0

                wnz = (counter != 0)
                outData = N.zeros(ns)
                if wnz.any():
                    if scale_factor is None:
                        outData[wnz] = cumData[wnz]
                    else:
                        outData[wnz] = cumData[wnz] * float(scale_factor)

                if output_nodata is not None:
                    wzz = (counter == 0)
                    if wzz.any():
                        outData[wzz] = output_nodata

                # if statusmapOut is not None:
                #     outDatasm = N.zeros(ns)
                #     if sm_nbr_files is not None:
                #         outDatasm[:] = len(file)
                #     else:
                #         if wnz.any():
                #             outDatasm[wnz] = counter[wnz]

                # outDatasm.shape = (1, -1)
                # smDs.GetRasterBand(ib+1).WriteArray(N.array(outDatasm), 0, il)

                # reshape before writing
                outData.shape = (1, -1)
                outband.WriteArray(N.array(outData), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None
        #   Writes metadata to output

        assign_metadata_processing(input_file, output_file)
    except:
        logger.warning('Error in do_cumulate. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_compute_perc_diff_vs_avg(input_file='', avg_file='', output_file='', input_nodata=None, output_nodata=None,
                                output_format=None,
                                output_type=None, options=''):
    # TODO-M.C.: check (and make uniform across functions()) data type
    epsilon = 1e-10

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # open files
        fileFID = gdal.Open(input_file, GA_ReadOnly)
        avgFID = gdal.Open(avg_file, GA_ReadOnly)

        # Read info from file
        nb = fileFID.RasterCount
        ns = fileFID.RasterXSize
        nl = fileFID.RasterYSize
        dataType = fileFID.GetRasterBand(1).DataType
        geoTransform = fileFID.GetGeoTransform()
        projection = fileFID.GetProjection()
        driver_type = fileFID.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file):
                input_nodata = float(sds_meta.get_nodata_value(input_file))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        indata = fileFID.GetRasterBand(1)
        inavg = avgFID.GetRasterBand(1)

        for il in range(fileFID.RasterYSize):
            data = N.ravel(indata.ReadAsArray(0, il, indata.XSize, 1))
            avgVal = N.ravel(inavg.ReadAsArray(0, il, inavg.XSize, 1))

            datatype = data.dtype

            if input_nodata is not None:
                nodata = N.zeros(1, datatype) + input_nodata
                wtp = (data != nodata) * (avgVal != nodata) * (avgVal > epsilon)
            else:
                wtp = (avgVal > epsilon)

            diff = N.zeros(indata.XSize)
            if output_nodata is not None:
                diff = diff + output_nodata

            if wtp.any():
                diff[wtp] = old_div(100.0 * (1.0 * data[wtp] - 1.0 * avgVal[wtp]), (1.0 * avgVal[wtp]))

            diff = diff.round()
            diff.shape = (1, -1)
            diffout = N.array(diff).astype(int)

            outband.WriteArray(diffout, 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Writes metadata to output
        input_list = []
        input_list.append(input_file)
        input_list.append(avg_file)
        #   Close outputs
        outDrv = None
        outDS = None
        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_compute_perc_diff_vs_avg. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_compute_primary_production(chla_file='', sst_file='', kd_file='', par_file='',
                                  chla_nodata=None, sst_nodata=None, kd_nodata=None, par_nodata=None,
                                  output_file='', output_nodata=None, output_format=None, output_type=None,
                                  options=''):
    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # open files
        chla_fileID = gdal.Open(chla_file, GA_ReadOnly)
        sst_fileID = gdal.Open(sst_file, GA_ReadOnly)
        kd_fileID = gdal.Open(kd_file, GA_ReadOnly)
        par_fileID = gdal.Open(par_file, GA_ReadOnly)

        functions.check_output_dir(os.path.dirname(output_file))

        # Read info from file, size are equal for all input files eg. sst, par
        nb = chla_fileID.RasterCount
        ns = chla_fileID.RasterXSize
        nl = chla_fileID.RasterYSize

        dataType = chla_fileID.GetRasterBand(1).DataType
        dataTypesst = sst_fileID.GetRasterBand(1).DataType

        geoTransform = chla_fileID.GetGeoTransform()
        projection = chla_fileID.GetProjection()
        driver_type = chla_fileID.GetDriver().ShortName

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and chla_nodata is not None:
            output_nodata = chla_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, 1, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)
        #
        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        chl_band = chla_fileID.GetRasterBand(1)
        sst_band = sst_fileID.GetRasterBand(1)
        kd_band = kd_fileID.GetRasterBand(1)
        par_band = par_fileID.GetRasterBand(1)

        # day length, dl = 12hrs

        dl = 12
        XSize = chla_fileID.RasterXSize
        #
        for il in range(chla_fileID.RasterYSize):
            F_ratio = N.zeros(XSize).astype(float)
            Pb_opt = N.zeros(XSize).astype(float)

            data_pp = N.zeros(XSize).astype(float) + output_nodata

            data_chl = N.ravel(chla_fileID.ReadAsArray(0, il, XSize, 1))
            data_sst = N.ravel(sst_fileID.ReadAsArray(0, il, XSize, 1))
            data_par = N.ravel(par_fileID.ReadAsArray(0, il, XSize, 1))
            data_kd = N.ravel(kd_fileID.ReadAsArray(0, il, XSize, 1))
            data_sst_rescal = data_sst * 0.01
            data_kd_rescal = data_kd * 0.001

            valid = (data_chl != chla_nodata) * (data_sst != sst_nodata) * (data_par != par_nodata) * (
                        data_kd != kd_nodata)

            if valid.any():

                # calculating f ratio  F using (0.66125 * Eo)/(Eo + 4.1)
                F_ratio[valid] = old_div((0.66125 * data_par[valid]), (data_par[valid] + 4.1))

                # Add a test on SST > 28.5 (see bug ES2-49)
                high_temp = (data_sst_rescal > 28.5)

                # Calculate Pb_opt from SST
                Pb_opt[valid] = -3.27e-8 * data_sst_rescal[valid] ** 7 + 3.4132e-6 * data_sst_rescal[
                    valid] ** 6 - 1.348e-4 * data_sst_rescal[valid] ** 5 + \
                                2.462e-3 * data_sst_rescal[valid] ** 4 - 0.0205 * data_sst_rescal[valid] ** 3 + 0.0617 * \
                                data_sst_rescal[valid] ** 2 + \
                                0.2749 * data_sst_rescal[valid] + 1.2956

                if high_temp.any():
                    Pb_opt[high_temp] = 4.0

                data_pp[valid] = data_chl[valid] * (4.6 / data_kd_rescal[valid]) * F_ratio[valid] * Pb_opt[valid] * dl

            data_pp.shape = (1, -1)

            outband.WriteArray(data_pp, 0, il)

        # #   ----------------------------------------------------------------------------------------------------
        # #   Writes metadata to output

        input_list = []
        input_list.append(chla_file)
        input_list.append(sst_file)
        input_list.append(kd_file)
        input_list.append(par_file)

        # #   Close outputs
        outDrv = None
        outDS = None
        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_compute_primary_production. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

def DetectEdgesInSingleImage(image, histogramWindowStride, \
                             minTheta, histogramWindowSize, minPopProp, minPopMeanDifference, minSinglePopCohesion,
                             minImageValue, \
                             wrapEdges=False, maxImageValue=None, masks=None, maskTests=None, maskValues=None,
                             medianFilterWindowSize=3, \
                             minPropNonMaskedCells=0.65, minGlobalPopCohesion=0.92, threads=1): \
        # Check and assign parameters

    if histogramWindowSize is None:
        histogramWindowSize = 32

    if histogramWindowStride is None:
        histogramWindowStride = 16

    if minTheta is None:
        minTheta = 0.76

    if minPopProp is None:
        minPopProp = 0.25

    if minPopMeanDifference is None:
        minPopMeanDifference = 0.25

    if minSinglePopCohesion is None:
        minSinglePopCohesion = 0.90

    if minImageValue is None:
        minImageValue = 10

    if masks is not None:
        if maskTests is None:
            print ('If you provide a list of masks, you must also provide a parallel list of mask tests.')
        if maskValues is None:
            print ('If you provide a list of masks, you must also provide a parallel list of mask values.')

    if medianFilterWindowSize is not None and medianFilterWindowSize % 2 == 0:
        print ('The median filter window size must be a positive odd integer greater than or equal to 3.')

    if histogramWindowStride > histogramWindowSize:
        print ('The histogram stride cannot be larger than the histogram window size.')

    # Import needed modules.

    import numpy
    from lib.compiled import FrontsUtils

    # The edge detection algorithm uses moving windows. To
    # simplify implementation of that code, create a copy of the
    # caller's image with a buffer around each edge. Also allocate
    # a buffered mask in which True indicates that the
    # corresponding cell of the caller's image is invalid.

    if medianFilterWindowSize is None:
        bufferSize = old_div((histogramWindowSize + 1), 2)
    else:
        bufferSize = max([old_div((medianFilterWindowSize + 1), 2), old_div((histogramWindowSize + 1), 2)])
    rows = bufferSize + image.shape[0] + bufferSize
    cols = bufferSize + image.shape[1] + bufferSize

    bufferedImage = numpy.zeros((rows, cols), dtype=image.dtype)
    bufferedImage[bufferSize:bufferSize + image.shape[0], bufferSize:bufferSize + image.shape[1]] = image

    bufferedMask = numpy.array([True] * rows * cols).reshape((rows, cols))
    unbufferedMask = bufferedMask[bufferSize:bufferSize + image.shape[0], bufferSize:bufferSize + image.shape[1]]
    # unbufferedMask is a reference to cells of bufferedMask, not a deep copy
    unbufferedMask[:] = False

    # Apply the caller's masks.

    if minImageValue is not None:
        print (' Debug: minImageValue is defined.')
        unbufferedMask[:] = numpy.logical_or(unbufferedMask, image < minImageValue)

    if maxImageValue is not None:
        print (' Debug: maxImageValue is defined.')
        unbufferedMask[:] = numpy.logical_or(unbufferedMask, image > maxImageValue)

    if masks is not None:
        for i in range(len(masks)):
            if maskTests[i] == u'equal':
                print((' Debug: Masking cells where mask %(mask)i is equal to ', i, '.'))
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] == maskValues[i])

            elif maskTests[i] == u'notequal':
                print((' Debug: Masking cells where mask %(mask)i is not equal to ', i, '.'))
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] != maskValues[i])

            elif maskTests[i] == u'greaterthan':
                print((' Debug: Masking cells where mask %(mask)i is greater than ', i, '.'))
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] > maskValues[i])

            elif maskTests[i] == u'lessthan':
                print((' Debug: Masking cells where mask %(mask)i is less than ', i, '.'))
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] < maskValues[i])

            elif maskTests[i] == u'anybitstrue':
                print((' Debug: Masking cells where mask ', i, '(mask) bitwise-ANDed with ', X, ' is not zero.'))
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, numpy.bitwise_and(masks[i], maskValues[i]) != 0)

            else:
                print (' is not an allowed mask test.')

    # If the caller specified that the edges should wrap, copy the
    # cells from the left edge of the image (and mask) to the
    # strip of buffer cells to the right of the image (and mask),
    # and visa versa. For example, if the image was 6x6 with a
    # buffer of 2 and these values:
    #
    #     [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  1,  2,  3,  4,  5,  0,  0],
    #      [ 0,  0,  6,  7,  8,  9, 10, 11,  0,  0],
    #      [ 0,  0, 12, 13, 14, 15, 16, 17,  0,  0],
    #      [ 0,  0, 18, 19, 20, 21, 22, 23,  0,  0],
    #      [ 0,  0, 24, 25, 26, 27, 28, 29,  0,  0],
    #      [ 0,  0, 30, 31, 32, 33, 34, 35,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]
    #
    # The resulting image, after the copy operation, would be:
    #
    #     [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 4,  5,  0,  1,  2,  3,  4,  5,  0,  1],
    #      [10, 11,  6,  7,  8,  9, 10, 11,  6,  7],
    #      [16, 17, 12, 13, 14, 15, 16, 17, 12, 13],
    #      [22, 23, 18, 19, 20, 21, 22, 23, 18, 19],
    #      [28, 29, 24, 25, 26, 27, 28, 29, 24, 25],
    #      [34, 35, 30, 31, 32, 33, 34, 35, 30, 31],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]

    if wrapEdges is True:
        bufferedImage[bufferSize:bufferSize + image.shape[0], 0:bufferSize] = bufferedImage[
                                                                              bufferSize:bufferSize + image.shape[0],
                                                                              -(bufferSize * 2):-bufferSize]
        bufferedImage[bufferSize:bufferSize + image.shape[0], -bufferSize:] = bufferedImage[
                                                                              bufferSize:bufferSize + image.shape[0],
                                                                              bufferSize:bufferSize * 2]
        bufferedMask[bufferSize:bufferSize + image.shape[0], 0:bufferSize] = bufferedMask[
                                                                             bufferSize:bufferSize + image.shape[0],
                                                                             -(bufferSize * 2):-bufferSize]
        bufferedMask[bufferSize:bufferSize + image.shape[0], -bufferSize:] = bufferedMask[
                                                                             bufferSize:bufferSize + image.shape[0],
                                                                             bufferSize:bufferSize * 2]

    # Apply the median filters.

    if medianFilterWindowSize is not None:
        # print ' Debug: Applying ',ix,i,' median filter.'
        bufferedImage = FrontsUtils.MedianFilter(bufferedImage, bufferedMask, bufferSize, medianFilterWindowSize)

        # If the caller specified that the edges should wrap, copy
        # image values to the buffer strips again, because the image
        # values probably changed as a result of running the median
        # filter.

        bufferedImage[bufferSize:bufferSize + image.shape[0], 0:bufferSize] = bufferedImage[
                                                                              bufferSize:bufferSize + image.shape[0],
                                                                              -(bufferSize * 2):-bufferSize]
        bufferedImage[bufferSize:bufferSize + image.shape[0], -bufferSize:] = bufferedImage[
                                                                              bufferSize:bufferSize + image.shape[0],
                                                                              bufferSize:bufferSize * 2]

    # Run the Cayula-Cornillon (1992) single-image edge detection
    # algorithm. This function performs the histogram and cohesion
    # steps, but does not perform contour following, thinning or
    # other post-processing.
    #
    # The values of the CandidateCounts image show how many times
    # each cell was a candidate for containing a front, i.e. the
    # number of times it appeared in a histogram window that had a
    # sufficiently large number of non-masked cells to proceed to
    # the histogramming portion of the algorithm. Masked cells can
    # never be candidates for containing a front, by definition,
    # so they will always have a zero CandidateCount. Because
    # successive histogram windows overlap, it is expected that a
    # given non-masked cell will have a CandidateCount greater
    # than 1.
    #
    # The values of the FrontCounts image show how many times each
    # cell was found to contain a front. This value will range
    # from zero (it never contained a front) to the CandidateCount
    # for the cell (it always contained a front in every histogram
    # window that contained it).
    #
    # The values of the WindowStatusCodes and WindowStatusValues
    # images show the result of running the algorithm on the
    # window centered on the cell in question. See the
    # documentation for these parameters for more information.

    bufferedCandidateCounts = numpy.zeros((rows, cols), dtype='int16')
    bufferedFrontCounts = numpy.zeros((rows, cols), dtype='int16')
    bufferedWindowStatusCodes = numpy.zeros((rows, cols), dtype='int8')
    bufferedWindowStatusValues = numpy.zeros((rows, cols), dtype='float32')

    print (' Debug: Running histogramming and cohesion algorithm.')
    timeStarted = time.time()

    # If we're only using one thread, invoke the C code directly.

    if threads <= 1 or threads > image.shape[0]:
        FrontsUtils.CayulaCornillonFronts(bufferedImage, bufferedMask, bufferedCandidateCounts, bufferedFrontCounts,
                                          bufferedWindowStatusCodes, bufferedWindowStatusValues, bufferSize,
                                          histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp,
                                          minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion)

    # If we're using multiple threads, divide the window into
    # equal-sized blocks invoke the C code on each block from a
    # separate thread.

    else:

        # First divide the bufferedImage and bufferedMask into
        # blocks, one block for each thread. Adjust the block
        # height to be a multiple of the histogram window stride;
        # otherwise some cells might be processed fewer times than
        # others. The last block will be slightly larger than the
        # preceding blocks unless the image height divided by the
        # number of threads is a multiple of the stride.
        #
        # The subarrays that are created here are references, not
        # deep copies.

        blockHeight = old_div(image.shape[0], threads)
        blockHeight = blockHeight - blockHeight % histogramWindowStride

        bufferedImageList = []
        bufferedMaskList = []

        for i in range(threads - 1):
            bufferedImageList.append(bufferedImage[i * blockHeight: (i + 1) * blockHeight + bufferSize * 2, :])
            bufferedMaskList.append(bufferedMask[i * blockHeight: (i + 1) * blockHeight + bufferSize * 2, :])

        bufferedImageList.append(bufferedImage[(i + 1) * blockHeight:, :])
        bufferedMaskList.append(bufferedMask[(i + 1) * blockHeight:, :])

        # When each thread passes the window over its block, the
        # window will include some cells from the above and below
        # blocks. As the algorithm executes, it writes values to
        # the numpy arrays we allocated. If we just passed in
        # references to subarrays of those arrays, there is the
        # possibility that two threads will try to write to the
        # same cell at the same time. To prevent this, allocate
        # separate arrays for each thread.

        bufferedCandidateCountsList = []
        bufferedFrontCountsList = []
        bufferedWindowStatusCodesList = []
        bufferedWindowStatusValuesList = []

        for i in range(threads):
            bufferedCandidateCountsList.append(numpy.zeros(bufferedImageList[i].shape, bufferedCandidateCounts.dtype))
            bufferedFrontCountsList.append(numpy.zeros(bufferedImageList[i].shape, bufferedFrontCounts.dtype))
            bufferedWindowStatusCodesList.append(
                numpy.zeros(bufferedImageList[i].shape, bufferedWindowStatusCodes.dtype))
            bufferedWindowStatusValuesList.append(
                numpy.zeros(bufferedImageList[i].shape, bufferedWindowStatusValues.dtype))

        # Import the threading module.

        try:
            import threading as _threading
        except ImportError:
            import dummy_threading as _threading

        # Create and start the threads.

        threadList = []
        for i in range(threads):
            t = _threading.Thread(name='%i' % i, target=FrontsUtils.CayulaCornillonFronts, args=(
            bufferedImageList[i], bufferedMaskList[i], bufferedCandidateCountsList[i], bufferedFrontCountsList[i],
            bufferedWindowStatusCodesList[i], bufferedWindowStatusValuesList[i], bufferSize, histogramWindowSize,
            histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta,
            minSinglePopCohesion, minGlobalPopCohesion))
            t.setDaemon(True)
            print (' Debug: Starting thread %(id)s to process rows %(start)i to %(end)i.')
            threadList.append(t)

        for i in range(threads):
            threadList[i].start()

        # Wait for all of the threads to exit.

        while len(threadList) > 0:
            threadList[0].join()
            print (' Debug: Thread %(id)s exited.')
            del threadList[0]

        # Aggregate the arrays computed by the threads into the
        # array we will return to the caller.

        for i in range(threads - 1):
            bufferedCandidateCounts[i * blockHeight: (i + 1) * blockHeight + bufferSize * 2, :] += \
            bufferedCandidateCountsList[i][:, :]
            bufferedFrontCounts[i * blockHeight: (i + 1) * blockHeight + bufferSize * 2, :] += bufferedFrontCountsList[
                                                                                                   i][:, :]
            bufferedWindowStatusCodes[i * blockHeight: (i + 1) * blockHeight + bufferSize * 2, :] += \
            bufferedWindowStatusCodesList[i][:, :]
            bufferedWindowStatusValues[i * blockHeight: (i + 1) * blockHeight + bufferSize * 2, :] += \
            bufferedWindowStatusValuesList[i][:, :]

        bufferedCandidateCounts[(i + 1) * blockHeight:, :] += bufferedCandidateCountsList[i + 1][:, :]
        bufferedFrontCounts[(i + 1) * blockHeight:, :] += bufferedFrontCountsList[i + 1][:, :]
        bufferedWindowStatusCodes[(i + 1) * blockHeight:, :] += bufferedWindowStatusCodesList[i + 1][:, :]
        bufferedWindowStatusValues[(i + 1) * blockHeight:, :] += bufferedWindowStatusValuesList[i + 1][:, :]

    timeEnded = time.time()
    print ("Debug: Histogram and cohesion algorithm complete. Elapsed time is: %f seconds" % (timeEnded - timeStarted))

    # If the caller specified that the edges should wrap,
    # CandidateCounts and FrontCounts for the the cells on the
    # left and right edges of the image are split between the
    # original locations of those cells and their duplicate
    # locations in the buffer strips along the opposite edges of
    # the image. Add the values from the buffer strips to the
    # values in the original locations. For example, if the
    # CandidateCounts array was 6x6 with a buffer of 2 and these
    # values:
    #
    #     [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 4,  5,  0,  1,  2,  3,  4,  5,  0,  1],
    #      [10, 11,  6,  7,  8,  9, 10, 11,  6,  7],
    #      [16, 17, 12, 13, 14, 15, 16, 17, 12, 13],
    #      [22, 23, 18, 19, 20, 21, 22, 23, 18, 19],
    #      [28, 29, 24, 25, 26, 27, 28, 29, 24, 25],
    #      [34, 35, 30, 31, 32, 33, 34, 35, 30, 31],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]
    #
    # The resulting array, after the copy operation, would be:
    #
    #     [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 4,  5,  0,  2,  2,  3,  8, 10,  0,  1],
    #      [10, 11, 12, 14,  8,  9, 20, 22,  6,  7],
    #      [16, 17, 24, 26, 14, 15, 32, 34, 12, 13],
    #      [22, 23, 36, 38, 20, 21, 44, 46, 18, 19],
    #      [28, 29, 48, 50, 26, 27, 56, 58, 24, 25],
    #      [34, 35, 60, 62, 32, 33, 68, 70, 30, 31],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]

    if wrapEdges:
        bufferedCandidateCounts[bufferSize:bufferSize + image.shape[0],
        -(bufferSize * 2):-bufferSize] += bufferedCandidateCounts[bufferSize:bufferSize + image.shape[0], 0:bufferSize]
        bufferedCandidateCounts[bufferSize:bufferSize + image.shape[0],
        bufferSize:bufferSize * 2] += bufferedCandidateCounts[bufferSize:bufferSize + image.shape[0], -bufferSize:]
        bufferedFrontCounts[bufferSize:bufferSize + image.shape[0],
        -(bufferSize * 2):-bufferSize] += bufferedFrontCounts[bufferSize:bufferSize + image.shape[0], 0:bufferSize]
        bufferedFrontCounts[bufferSize:bufferSize + image.shape[0], bufferSize:bufferSize * 2] += bufferedFrontCounts[
                                                                                                  bufferSize:bufferSize +
                                                                                                             image.shape[
                                                                                                                 0],
                                                                                                  -bufferSize:]

        timeEnded = time.time()
        print ("Debug: Wrap Edges done. Elapsed time is: %f seconds" % (timeEnded - timeStarted))
    else:
        print ("Debug: No wrap edged.")

    # Return successfully.

    unbufferedImage = bufferedImage[bufferSize:bufferSize + image.shape[0], bufferSize:bufferSize + image.shape[1]]
    unbufferedCandidateCounts = bufferedCandidateCounts[bufferSize:bufferSize + image.shape[0],
                                bufferSize:bufferSize + image.shape[1]]
    unbufferedFrontCounts = bufferedFrontCounts[bufferSize:bufferSize + image.shape[0],
                            bufferSize:bufferSize + image.shape[1]]
    unbufferedWindowStatusCodes = bufferedWindowStatusCodes[bufferSize:bufferSize + image.shape[0],
                                  bufferSize:bufferSize + image.shape[1]]
    unbufferedWindowStatusValues = bufferedWindowStatusValues[bufferSize:bufferSize + image.shape[0],
                                   bufferSize:bufferSize + image.shape[1]]

    timeEnded = time.time()
    print ("Debug: Return. Elapsed time is: %f seconds" % (timeEnded - timeStarted))
    return copy.deepcopy(unbufferedMask), copy.deepcopy(unbufferedImage), copy.deepcopy(
        unbufferedCandidateCounts), copy.deepcopy(unbufferedFrontCounts), copy.deepcopy(
        unbufferedWindowStatusCodes), copy.deepcopy(unbufferedWindowStatusValues)


# _____________________________
def do_detect_sst_fronts(input_file='', output_file='', input_nodata=None, parameters=None,
                         output_nodata=None, output_format=None, output_type=None, options=''):

    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Parameters is expected to be None, or a dictionary
        if parameters is not None:

            if 'histogramWindowStride' in list(parameters.keys()):
                histogramWindowStride = parameters['histogramWindowStride']
            else:
                histogramWindowStride = None

            if 'minTheta' in list(parameters.keys()):
                minTheta = parameters['minTheta']
            else:
                minTheta = None
            if 'minPopProp' in list(parameters.keys()):
                minPopProp = parameters['minPopProp']
            else:
                minPopProp = None
            if 'minPopMeanDifference' in list(parameters.keys()):
                minPopMeanDifference = parameters['minPopMeanDifference']
            else:
                minPopMeanDifference = None
            if 'minSinglePopCohesion' in list(parameters.keys()):
                minSinglePopCohesion = parameters['minSinglePopCohesion']
            else:
                minSinglePopCohesion = None
            if 'histogramWindowSize' in list(parameters.keys()):
                histogramWindowSize = parameters['histogramWindowSize']
            else:
                histogramWindowSize = None
            if 'minImageValue' in list(parameters.keys()):
                minImageValue = parameters['minImageValue']
            else:
                minImageValue = None

            minThreshold = 1
            if 'minThreshold' in list(parameters.keys()):
                if parameters['minThreshold'] is not None:
                    minThreshold = parameters['minThreshold']

        rid = ''
        debug = 0

        output_file_final = output_file
        output_file = tmpdir + os.sep + os.path.basename(output_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # Open input file
        inputID = gdal.Open(input_file, GA_ReadOnly)

        # Read info from infile
        nb = inputID.RasterCount
        ns = inputID.RasterXSize
        nl = inputID.RasterYSize

        dataType = inputID.GetRasterBand(1).DataType

        geoTransform = inputID.GetGeoTransform()
        projection = inputID.GetProjection()
        driver_type = inputID.GetDriver().ShortName

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # Manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # Check output directory
        functions.check_output_dir(os.path.dirname(output_file))

        # Instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        if debug:
            n_bands = 3
        else:
            n_bands = 1
        outDS = outDrv.Create(output_file, ns, nl, n_bands, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # Read Input
        inband = inputID.GetRasterBand(1)
        inData = inband.ReadAsArray(0, 0, inband.XSize, inband.YSize)

        inDataInt = N.uint16(inData) * 0
        inData_good = (inData > 0)
        inDataInt[inData_good] = inData[inData_good]

        # Call FrontDetection Algorithm
        [uMask, uImage, uCandidateCounts, uFrontCounts, uWindowStatusCodes, uWindowStatusValues] = \
            DetectEdgesInSingleImage(inDataInt, histogramWindowStride, minTheta, histogramWindowSize, minPopProp,
                                     minPopMeanDifference, minSinglePopCohesion, minImageValue)

        print ("Debug: Applying now Minimum threshold: %i" % minThreshold)

        # Apply minimum threshold (line by line)
        dataOut = N.empty([nl, ns], dtype=bool)
        for il in range(nl):
            data_in = uFrontCounts[il, :]
            rowOut = N.empty([ns], dtype=bool) * 0
            rowOut[data_in >= minThreshold] = 1
            dataOut[il, :] = rowOut[:]

        # Apply thinning
        print ("Debug: Applying now thinning")
        thin_output = pymorph.thin(dataOut)
        # thin_output = dataOut                              # For TEST only ... make it faster

        # Create and write output band
        print ("Debug: Writing the output files")
        if debug:
            outband = outDS.GetRasterBand(1)
            outband.WriteArray(uFrontCounts, 0, 0)
            outband = outDS.GetRasterBand(3)
            outband.WriteArray(dataOut, 0, 0)
            outband = outDS.GetRasterBand(2)
            outband.WriteArray(thin_output, 0, 0)
        else:
            outband = outDS.GetRasterBand(1)
            outband.WriteArray(thin_output, 0, 0)

        # #   ----------------------------------------------------------------------------------------------------
        # #   Writes metadata to output
        print ("Debug: Assigning metadata")
        input_list = []
        input_list.append(input_file)

        # #   Close outputs
        outDrv = None
        outDS = None
        assign_metadata_processing(input_list, output_file, parameters=parameters)

    except:
        logger.warning('Error in detect-sst-fronts. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
def do_ts_linear_filter(input_file='', before_file='', after_file='', output_file='', input_nodata=None,
                        output_format=None,
                        output_type=None, options='', threshold=None):
    #
    # Notes:'The command expects exactly 3 input files, in 3 arguments.'
    #       'The input_nodata defines the output_nodata as well (no recoding)'
    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final = output_file
        output_file = tmpdir + os.sep + os.path.basename(output_file)

        # Open the threee files (add checks)
        f0 = gdal.Open(input_file, GA_ReadOnly)
        fm1 = gdal.Open(before_file, GA_ReadOnly)
        fp1 = gdal.Open(after_file, GA_ReadOnly)

        # get infos from the input_file
        nb = f0.RasterCount
        ns = f0.RasterXSize
        nl = f0.RasterYSize
        dataType = f0.GetRasterBand(1).DataType
        geoTransform = f0.GetGeoTransform()
        projection = f0.GetProjection()
        driver_type = f0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file):
                input_nodata = float(sds_meta.get_nodata_value(input_file))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output(s)
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        for ib in range(nb):

            f0band = f0.GetRasterBand(ib + 1)
            fm1band = fm1.GetRasterBand(ib + 1)
            fp1band = fp1.GetRasterBand(ib + 1)
            outband = outDS.GetRasterBand(ib + 1)

            for il in range(f0.RasterYSize):

                data = N.ravel(f0band.ReadAsArray(0, il, f0band.XSize, 1)).astype(float)
                data_m1 = N.ravel(fm1band.ReadAsArray(0, il, fm1band.XSize, 1)).astype(float)
                data_p1 = N.ravel(fp1band.ReadAsArray(0, il, fp1band.XSize, 1)).astype(float)

                if input_nodata is None:
                    wtp = N.ravel((data_m1 != 0) * (data_p1 != 0))
                else:
                    wtp = N.ravel(
                        (data_m1 != input_nodata) * (data_p1 != input_nodata) * N.ravel((data_m1 != 0) * (data_p1 != 0)))

                correct = data
                if wtp.any():
                    slope1 = N.zeros(data.shape)
                    slope1[wtp] = old_div((data[wtp] - data_m1[wtp]), abs(data_m1[wtp]))
                    slope2 = N.zeros(data.shape)
                    slope2[wtp] = old_div((data_p1[wtp] - data[wtp]), abs(data_p1[wtp]))
                    wtc = (slope1 < -threshold) * (slope2 > threshold)

                    if wtc.any():
                        correct[wtc] = 0.5 * (data_m1[wtc] + data_p1[wtc])

                correct.shape = (1, len(correct))
                outband.WriteArray(N.array(correct), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Writes metadata to output
        input_list = []
        input_list.append(before_file)
        input_list.append(input_file)
        input_list.append(after_file)
        #   Close outputs
        outDrv = None
        outDS = None

        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_ts_linear_filter. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

def do_rain_onset(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
                  output_type=None, options='', current_dekad=None):
    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        output_file_final = output_file
        output_file = tmpdir + os.sep + os.path.basename(output_file)
        # Determines if it is the first dekad of the season
        if len(input_file) == 2:
            first_dekad = True
            fid_t0 = gdal.Open(input_file[0], GA_ReadOnly)
            fid_m1 = gdal.Open(input_file[1], GA_ReadOnly)
        else:
            first_dekad = False
            fid_t0 = gdal.Open(input_file[0], GA_ReadOnly)
            fid_m1 = gdal.Open(input_file[1], GA_ReadOnly)
            fid_m2 = gdal.Open(input_file[2], GA_ReadOnly)
            fid_prev = gdal.Open(input_file[3], GA_ReadOnly)

        # Read info from file
        nb = fid_t0.RasterCount
        ns = fid_t0.RasterXSize
        nl = fid_t0.RasterYSize
        dataType = fid_t0.GetRasterBand(1).DataType
        geoTransform = fid_t0.GetGeoTransform()
        projection = fid_t0.GetProjection()
        driver_type = fid_t0.GetDriver().ShortName
        rangenl = list(range(nl))

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata = float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate outputs
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetProjection(projection)
        outDS.SetGeoTransform(geoTransform)
        outband = outDS.GetRasterBand(1)

        # First dekad of season -> 2 inputs, no previous output
        if first_dekad:
            # parse image by line
            for il in rangenl:
                outData = N.zeros(ns)
                data1 = N.ravel(fid_m1.GetRasterBand(1).ReadAsArray(0, il, ns, 1).astype(float))
                data2 = N.ravel(fid_t0.GetRasterBand(1).ReadAsArray(0, il, ns, 1).astype(float))

                meet = ((data1 >= 25) & ((data2) >= 20))
                # set elements matching mask to dekad number
                outData[meet] = current_dekad - 1

                # reshape before writing
                outData.shape = (1, -1)
                outband.WriteArray(N.array(outData), 0, il)
        else:
            # Case of 3 inputs and the previous output
            # parse image by line
            for il in rangenl:
                outData = N.zeros(ns)
                data1 = N.ravel(fid_m2.GetRasterBand(1).ReadAsArray(0, il, ns, 1).astype(float))
                data2 = N.ravel(fid_m1.GetRasterBand(1).ReadAsArray(0, il, ns, 1).astype(float))
                data3 = N.ravel(fid_t0.GetRasterBand(1).ReadAsArray(0, il, ns, 1).astype(float))
                prev_out = N.ravel(fid_prev.GetRasterBand(1).ReadAsArray(0, il, ns, 1).astype(float))

                meet_1 = ((data1 >= 25) & ((data2 + data3) >= 20))
                meet_2 = ((data2 >= 25) & (data3 >= 20))

                notdone = (prev_out == 0)
                already_done = (prev_out > 0)
                mask_1 = (notdone & meet_1)
                mask_2 = (notdone & meet_2)
                # set elements matching mask to dekad number
                outData[mask_2] = current_dekad - 1
                outData[mask_1] = current_dekad - 2
                outData[already_done] = prev_out[already_done]

                # reshape before writing
                outData.shape = (1, -1)
                outband.WriteArray(N.array(outData), 0, il)

        # ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None

        #   Writes metadata to output
        assign_metadata_processing(input_file, output_file)
    except:
        logger.warning('Error in rain-onset. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# _____________________________
#   Merge/move wrt processing.py functions
def ParseType(type):
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
    elif type == 'CInt16':
        return GDT_CInt16
    elif type == 'CInt32':
        return GDT_CInt32
    elif type == 'CFloat32':
        return GDT_CFloat32
    elif type == 'CFloat64':
        return GDT_CFloat64
    else:
        return GDT_Byte


# _____________________________
#   Merge/move wrt processing.py functions
#   To be completed !!!!
def ReturnNoData(type):
    if type == 'Byte':
        return 255
    elif type == 'Int16':
        return -32768
    elif type == 'UInt16':
        return 65536
    elif type == 'Int32':
        return GDT_Int32
    elif type == 'UInt32':
        return GDT_UInt32
    elif type == 'Float32':
        return GDT_Float32
    elif type == 'Float64':
        return GDT_Float64
    elif type == 'CInt16':
        return GDT_CInt16
    elif type == 'CInt32':
        return GDT_CInt32
    elif type == 'CFloat32':
        return GDT_CFloat32
    elif type == 'CFloat64':
        return GDT_CFloat64
    else:
        return GDT_Byte


def return_as_list(input_args):

    my_list = []
    if isinstance(input_args, list):
        my_list = input_args
    else:
        for item in input_args:
            my_list.append(item)
    return my_list


def do_reproject(inputfile, output_file, native_mapset_name, target_mapset_name):

    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        native_mapset = mapset.MapSet()
        native_mapset.assigndb(native_mapset_name)

        # Define the Native mapset
        target_mapset = mapset.MapSet()
        target_mapset.assigndb(target_mapset_name)

        output_file_final = output_file
        output_file = tmpdir + os.sep + os.path.basename(output_file)

        # Open the input file
        orig_ds = gdal.Open(inputfile)

        orig_cs = osr.SpatialReference(wkt=native_mapset.spatial_ref.ExportToWkt())
        orig_geo_transform = native_mapset.geo_transform
        orig_size_x = native_mapset.size_x
        orig_size_y = native_mapset.size_y
        orig_band = orig_ds.GetRasterBand(1)
        orig_ds.SetGeoTransform(native_mapset.geo_transform)
        orig_ds.SetProjection(orig_cs.ExportToWkt())

        in_data_type = orig_band.DataType

        # Get the Target mapset
        trg_mapset = mapset.MapSet()
        trg_mapset.assigndb(target_mapset_name)
        out_cs = trg_mapset.spatial_ref
        out_size_x = trg_mapset.size_x
        out_size_y = trg_mapset.size_y

        # Create target in memory
        mem_driver = gdal.GetDriverByName('MEM')

        # Assign mapset to dataset in memory
        out_data_type_gdal = in_data_type
        mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, out_data_type_gdal)
        mem_ds.SetGeoTransform(trg_mapset.geo_transform)
        mem_ds.SetProjection(out_cs.ExportToWkt())

        # Do the Re-projection
        orig_wkt = orig_cs.ExportToWkt()
        res = gdal.ReprojectImage(orig_ds, mem_ds, orig_wkt, out_cs.ExportToWkt(),
                                  es_constants.ES2_OUTFILE_INTERP_METHOD)

        out_data = mem_ds.ReadAsArray()

        output_driver = gdal.GetDriverByName('GTiff')
        output_ds = output_driver.Create(output_file, out_size_x, out_size_y, 1, in_data_type)
        output_ds.SetGeoTransform(trg_mapset.geo_transform)
        output_ds.SetProjection(out_cs.ExportToWkt())
        output_ds.GetRasterBand(1).WriteArray(out_data, 0, 0)

        trg_ds = None
        mem_ds = None
        orig_ds = None
        output_driver = None
        output_ds = None

        # Copy metadata, by changing mapset only
        meta_data = metadata.SdsMetadata()
        meta_data.read_from_file(inputfile)
        meta_data.assign_mapset(target_mapset_name)
        meta_data.write_to_file(output_file)

    except:
        logger.warning('Error in do_reproject. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

#   -------------------------------------------------------------------------------------------
def getRasterBox(fid, xstart, xend, ystart, yend, band):
    #
    #   Analyzes the RasterFile (fid) in the CROI area (identified by xstart, xend, ystart, yend)
    #   and returns the range of polygons IDs (minValGrid, maxValGrid) to be considered by doStats.
    #   Used by do_stats_4_raster()
    #   Arguments:
    #
    #       fid: file identifier of the 'grid' raster file (already open)
    #       xstart,xend,ystart,yend: x-y coords of the BB to be considered in the grid file
    #

    # Initialise with 'extreme' values, to be updated in the loop
    minValGrid = None
    maxValGrid = None

    ns = int(xend - xstart + 1)
    nl = int(yend - ystart + 1)

    indexRef = N.arange(ns)

    for il in range(int(ystart), int(yend + 1)):
        data = N.ravel(fid.GetRasterBand(band).ReadAsArray(int(xstart), il, ns, 1))
        wts = (data != 0)

        if wts.any():

            thisMinValGrid = data[wts].min()
            thisMaxValGrid = data[wts].max()

            if minValGrid is None:
                minValGrid = thisMinValGrid
            elif thisMinValGrid < minValGrid:
                minValGrid = thisMinValGrid

            if maxValGrid is None:
                maxValGrid = thisMaxValGrid
            elif thisMaxValGrid > maxValGrid:
                maxValGrid = thisMaxValGrid

    return [minValGrid, maxValGrid]


#   -------------------------------------------------------------------------------------------
#   Computes surface area of each pixel for an given mapset or the given image

#   Argument:
#       inputfile:      input file ( if input file is passed then the geotransform , projection, raster xsize and y size are take from the input
#       output_file:    output file name
#       output_format:  output format (GTIFF by default)
#       output_type:    output type (by default the same as in the input file
#       mapsetcode:      Mapset code ( computes projection, geotransform, x and y size from the mapset)
#       args:           list of additional arguments (FTTB only 1, used for density)
def create_surface_area_raster(input_file=None, output_file='', output_format=None, output_type=None, mapsetcode=None):
    #
    # Notes:

    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        output_file_final = output_file
        output_file = tmpdir + os.sep + os.path.basename(output_file)

        if input_file is not None:
            f1Fid = gdal.Open(input_file, GA_ReadOnly)
            nb = f1Fid.RasterCount
            ns = f1Fid.RasterXSize
            nl = f1Fid.RasterYSize
            dataType = f1Fid.GetRasterBand(1).DataType
            geoTransform = f1Fid.GetGeoTransform()
            projection = f1Fid.GetProjection()
            driver_type = f1Fid.GetDriver().ShortName
            ymin = geoTransform[3]
            pixel_shift_lat = geoTransform[5]

        if mapsetcode is not None:
            # Create Mapset object and test
            native_mapset = mapset.MapSet()
            native_mapset.assigndb(mapsetcode)

            if native_mapset.validate():
                return 1

            mapset_info = querydb.get_mapset(mapsetcode=mapsetcode)
            ymin = float(mapset_info.upper_left_lat)
            nl = int(mapset_info.pixel_size_y)
            ns = int(mapset_info.pixel_size_x)
            geoTransform = native_mapset.geo_transform
            projection = native_mapset.spatial_ref.ExportToWkt()
            pixel_shift_lat = native_mapset.pixel_shift_lat

        # manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format
        if output_format is None:
            outFormat = 'GTIFF'
        else:
            outFormat = output_format

        # instantiate output(s)
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, 1, outType)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # pre-open files, to speed up processing
        # fidList=[]
        # fidList.append(gdal.Open(input_file, GA_ReadOnly))

        outband = outDS.GetRasterBand(1)

        for il in range(nl):
            nl_lat_value = ymin + (il * pixel_shift_lat)
            d = abs(pixel_shift_lat)  # 0.008928571428571
            const_d2km = 12364.35
            area_deg = d * d * math.cos(old_div(nl_lat_value, 180) * math.pi)
            area_km = area_deg * const_d2km

            # if (nl_lat_value != 0):
            surface_area = N.zeros(ns)
            surface_area.fill(area_km)

            surface_area.shape = (1, -1)

            outband.WriteArray(N.array(surface_area), 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Close outputs
        outDrv = None
        outDS = None
        #   Writes metadata to output
        # assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in create_surface_area_raster. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

#   -------------------------------------------------------------------------------------------
def do_raster_stats(fid, fidID, outDS, iband, roi, minId, maxId, nodata, operation, args=None):
    #
    #   Perform the 'operation' in inputfile (fid), according the 'grid' defined in fidID, and write to fidOut
    #   Used by do_stats_4_raster()
    #   Arguments:
    #
    #       fid:    input file identifier
    #       fidID:  file identifier of the 'grid' raster file
    #       fidout: file identifier of the output raster file. file has same size as fin
    #       iband:  number of band to consider (default is 1)
    #       roi:    as returned from common_area
    #               contains all info about offsets (firstX/YOffset -> file (fid), secondX/YOffset -> raster(fidID))
    #       minId, maxID:   range of IDs to consider in fidID
    #       nodata:         value to disregard in comps
    #       operation:      operation to apply
    #       args:           list of additional arguments (FTTB only 1, used for density)
    #

    # Check arguments
    if operation == 'density' and args is None:
        logger.error('Operation density requires an addtional argument')
        return 1

    # output file (fidOut) has the same size as file (fid)
    numIDs = maxId - minId + 1

    # store: sum, N, min, max, nPixId
    statsData = N.zeros((5, (numIDs)))
    minmaxInit = N.zeros((numIDs))

    # let's parse the common window
    ns = roi['xSize']
    nl = roi['ySize']

    # For tests only
    l_start = 0
    l_end = nl - 1

    # Npixels in Rasterfile
    nsiD = fidID.RasterXSize

    # Prepare a matrix to store idValues
    MatrixidData = N.zeros((nl, ns))
    outband = outDS.GetRasterBand(iband + 1)

    logger.debug(' Identifying IDs of polygons and computing stats')
    for il in range(l_start, l_end):
        # read 1 full line from image
        data = N.ravel(fid.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
        # read 1 full line from idRaster
        idDataTmp = N.ravel(fidID.GetRasterBand(iband + 1).ReadAsArray(0, il + roi['secondYOff'], nsiD, 1))

        # reduce data set, for raster file
        idData = idDataTmp[roi['secondXOff']:roi['secondXOff'] + ns]
        MatrixidData[il] = idDataTmp[roi['secondXOff']:roi['secondXOff'] + ns]

        # accumulate values in the vector
        # wtadd is an image index (where position)
        if (nodata is None):
            wtadd = (idData >= minId) * (idData <= maxId)
        else:
            wtadd = (data != nodata) * (idData >= minId) * (idData <= maxId)

        if wtadd.any():
            idPos = idData[wtadd] - minId
            dataSelect = data[wtadd]

            # sum up the value
            for ii in range(len(idPos)):
                statsData[0, idPos[ii]] = statsData[0, idPos[ii]] + dataSelect[ii]
                # counter ++
                statsData[1, idPos[ii]] = statsData[1, idPos[ii]] + 1

            # update min and max
            for ii in range(len(idPos)):
                if (minmaxInit[idPos[ii]] == 0):
                    statsData[2, idPos[ii]] = dataSelect[ii]
                    statsData[3, idPos[ii]] = dataSelect[ii]
                    minmaxInit[idPos[ii]] = 1
                else:
                    if dataSelect[ii] < statsData[2, idPos[ii]]:
                        # reset min
                        statsData[2, idPos[ii]] = dataSelect[ii]
                    if dataSelect[ii] > statsData[3, idPos[ii]]:
                        # reset max
                        statsData[3, idPos[ii]] = dataSelect[ii]

    # On the basis of the iDMatrix, assign the output
    outdata = N.zeros((nl, ns))
    if nodata is not None:
        outdata += nodata

    # Do the test first, to optimize loop ...
    if operation == 'count':
        for il in range(0, nl - 1):
            for ip in range(0, ns - 1):
                outdata[il, ip] = statsData[1, MatrixidData[il, ip] - minId]
    elif operation == 'sum':
        for il in range(l_start, l_end):
            for ip in range(0, ns - 1):
                outdata[il, ip] = statsData[0, MatrixidData[il, ip] - minId]
    elif operation == 'min':
        for il in range(0, nl - 1):
            for ip in range(0, ns - 1):
                outdata[il, ip] = statsData[2, MatrixidData[il, ip] - minId]
    elif operation == 'max':
        for il in range(0, nl - 1):
            for ip in range(0, ns - 1):
                outdata[il, ip] = statsData[3, MatrixidData[il, ip] - minId]
    elif operation == 'avg':
        for il in range(0, nl - 1):
            for ip in range(0, ns - 1):
                if statsData[1, MatrixidData[il, ip] - minId] != 0:
                    outdata[il, ip] = float(statsData[0, MatrixidData[il, ip] - minId]) / float(
                        statsData[1, MatrixidData[il, ip] - minId])

    elif operation == 'density':
        for il in range(0, nl - 1):
            for ip in range(0, ns - 1):
                outdata[il, ip] = float(statsData[0, MatrixidData[il, ip] - minId]) / args[0]

    outband.WriteArray(N.array(outdata), 0, 0)

    return 0


#   -------------------------------------------------------------------------------------------
#   Computes statistics over polygons. The operation is defined by -op option.
#   Polygons are defined by a raster of polygon ids
#   The foreseen operations are:
#       count, sum, min, max, avg : no additional arguments
#       density: 1 argument -> scaling factor
#   Argument:
#       inputfile:      input file
#       grid_file:      file with grid/polygons IDs
#       output_file:    output file name
#       operation:      see above
#       output_format:  output format (GTIFF by default)
#       nodata:         nodata value - in input_file
#       output_type:    output type (by default the same as in the input file
#       options:        additional options (e.g. compression)
#       args:           list of additional arguments (FTTB only 1, used for density)
#
def do_stats_4_raster(input_file, grid_file, output_file, operation, input_mapset_name, grid_mapset_name,
                      output_format=None, nodata=None, output_type=None, options=None, args=None):

    tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                              dir=es_constants.base_tmp_dir)

    output_file_final = output_file
    output_file = tmpdir + os.sep + os.path.basename(output_file)

    # Manage input arguments
    if output_format is None:
        output_format = 'GTiff'

    # Manage options
    options_list = [es_constants.ES2_OUTFILE_OPTIONS]
    if options is not None:
        options_list.append(options)

    try:
        # Open input file
        fidIn = gdal.Open(input_file, GA_ReadOnly)
        if fidIn is None:
            logger.error('Could not open input file $0'.format(input_file))
            return 1
        # Read info from input file
        nsIn = fidIn.RasterXSize
        nlIn = fidIn.RasterYSize
        inGeo = fidIn.GetGeoTransform()
        inProj = fidIn.GetProjection()
        dataType = fidIn.GetRasterBand(1).DataType

        if nodata is None:
            metadata_input = metadata.SdsMetadata()
            metadata_input.read_from_ds(fidIn)
            nodata_output = float(metadata_input.get_item('eStation2_nodata'))
        else:
            nodata_output = nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # Open idRaster
        fidRaster = gdal.Open(grid_file, GA_ReadOnly)
        if fidRaster is None:
            logger.error('Could not open grid file $0'.format(grid_file))
            return 1

        nlevel = fidRaster.RasterCount

        # Instantiate output
        nb = 1
        outDrv = gdal.GetDriverByName(output_format)
        outDS = outDrv.Create(output_file, nsIn, nlIn, nb, outType, options_list)
        outDS.SetProjection(inProj)
        outDS.SetGeoTransform(inGeo)

        # Determine common area, considering the two Mapsets
        mapset_1 = mapset.MapSet()
        mapset_1.assigndb(input_mapset_name)
        mapset_2 = mapset.MapSet()
        mapset_2.assigndb(grid_mapset_name)

        common_roi = mapset_1.compute_common_area(mapset_2)

        if common_roi['isCommon'] != True:
            logger.warning('Images do not have common ROIs')
            return 1

        # Get the min/maxId value from raster file, in common ROI
        [minId, maxId] = getRasterBox(fidRaster,
                                      common_roi['secondXOff'], common_roi['xSize'] - 1 + common_roi['secondXOff'],
                                      common_roi['secondYOff'], common_roi['ySize'] - 1 + common_roi['secondYOff'],
                                      1)
        # parse bands
        for iband in range(nlevel):
            # compute stats and write to output file
            statsData = do_raster_stats(fidIn, fidRaster, outDS, iband, common_roi, minId, maxId, nodata_output,
                                        operation, args=args)

        outDS = None
        outDrv = None

        #   Writes metadata to output
        assign_metadata_processing(input_file, output_file)

    except:
        logger.warning('Error in do_stats_4_raster. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

################################
##  Compute chla gradient   ####
## using normal ndimage sobel###
################################

def do_compute_chla_gradient(input_file='', nodata=None, output_file='', output_nodata=None, output_format=None,
                             output_type=None, options=''):
    try:

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        output_file_final =  output_file
        output_file = tmpdir + os.sep +os.path.basename(output_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # open chla file
        chla_fileID = gdal.Open(input_file, GA_ReadOnly)

        functions.check_output_dir(os.path.dirname(output_file))

        # Read info from file, size are equal for all input files eg. sst, par
        nb = chla_fileID.RasterCount
        ns = chla_fileID.RasterXSize
        nl = chla_fileID.RasterYSize

        dataType = chla_fileID.GetRasterBand(1).DataType

        geoTransform = chla_fileID.GetGeoTransform()
        projection = chla_fileID.GetProjection()
        driver_type = chla_fileID.GetDriver().ShortName

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and nodata is not None:
            output_nodata = nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, 1, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)
        #
        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        chl_band = chla_fileID.GetRasterBand(1)

        data_chla = chl_band.ReadAsArray(0, 0, ns, nl).astype(float)

        # Replace the nodata value with Nan
        data_chla[data_chla == nodata] = N.nan

        # Data smoothing (median filter)
        if sys.platform == 'win32':
            smooth_data_chla = scipy.ndimage.median_filter(data_chla, 3)
            # smooth_data_chla = scipy.ndimage.gaussian_filter(data_chla, 3)
            # Gradient derivation
            # Sobel (X direction)
            sx = scipy.ndimage.sobel(smooth_data_chla, axis=0, mode='nearest')
            # Sobel (Y direction)
            sy = scipy.ndimage.sobel(smooth_data_chla, axis=1, mode='nearest')
        else:
            smooth_data_chla = ndimage.median_filter(data_chla, 3)
            # Gradient derivation
            # Sobel (X direction)
            sx = ndimage.sobel(smooth_data_chla, axis=0, mode='nearest')
            # Sobel (Y direction)
            sy = ndimage.sobel(smooth_data_chla, axis=1, mode='nearest')

        # Sobel
        chla_gradient = N.hypot(sx, sy)

        # Quick and dirty removal of the fronts generated by Nodara
        # wtp = (chla_gradient > 100)
        # chla_gradient[wtp] = 0

        data_gradient = chla_gradient

        # Write out the full matrix N.array(outData)
        outband.WriteArray(data_gradient, 0, 0)
        input_list = []
        input_list.append(input_file)

        # #   Close outputs
        outDrv = None
        outDS = None
        # logger.warning('Writing MetaData not done yet ! To be implemented ...')
        assign_metadata_processing(input_list, output_file)

    except:
        logger.warning('Error in do_compute_chla_gradient. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# ##########################
#   Compute chla gradient  #
#    Jean-Noel Algo        #
############################
def compute_extrapolated_chla_gradient(input_file='', nodata=None, output_file='', output_nodata=None,
                                       output_format=None,
                                       output_type=None, options=''):
    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        output_file_final = output_file
        output_file = tmpdir + os.sep + os.path.basename(output_file)
        ##############
        #  constants #
        ##############
        # filter_x = d2dgauss(n1=n_x1,sigma1=sigma_x1 ,n2=n_x2, sigma2=sigma_x2, theta=theta1)
        filter_x = N.array([[0.3255, 0.0000, -0.3255], [0.5367, 0, -0.5367], [0.3255, -0.0000, -0.3255]])

        pix_km_dy_mat = 4.633
        # filter_y = d2dgauss(n1=n_y1,sigma1=sigma_y1 ,n2=n_y2, sigma2=sigma_y2, theta=theta2)
        filter_y = N.array([[0.3255, 0.5367, 0.3255], [0, 0, 0], [-0.3255, -0.5367, -0.3255]])

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # open chla file
        chla_fileID = gdal.Open(input_file, GA_ReadOnly)

        functions.check_output_dir(os.path.dirname(output_file))

        # Read info from file, size are equal for all input files eg. sst, par
        nb = chla_fileID.RasterCount
        ns = chla_fileID.RasterXSize
        nl = chla_fileID.RasterYSize

        dataType = chla_fileID.GetRasterBand(1).DataType

        geoTransform = chla_fileID.GetGeoTransform()
        projection = chla_fileID.GetProjection()
        driver_type = chla_fileID.GetDriver().ShortName

        # geoTransform = f1Fid.GetGeoTransform()
        ymin = geoTransform[3]
        pixel_shift_lat = geoTransform[5]

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and nodata is not None:
            output_nodata = nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, 1, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)
        #
        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        chl_band = chla_fileID.GetRasterBand(1)

        data_chla = chl_band.ReadAsArray(0, 0, ns, nl).astype(float)

        # Replace the nodata value with Nan
        data_chla[data_chla == nodata] = N.nan

        ###########################################
        ##########  Extrapolate ###################
        ###########################################
        # Copy the data to filter data
        filtData = N.copy(data_chla)

        # Replace NaN values with zeros(for eStation data)
        # filtData[N.invert(N.isfinite(data_chla))] = 0
        # Replace NaN values with zeros(for Jean data)
        filtData[data_chla == nodata] = 0
        # data_chla[data_chla == nodata] = N.nan

        ifinite = N.isfinite(data_chla)  # ifinite = isfinite(Data)

        # This function applies a square-shape order filter (10 iterations)
        # followed by a square-shape gaussian filter to the set of data "Data" and
        # gives the filtered set of data in "FiltData".
        # The size of the order filter is "SzOrd" and the order is "Perc"
        # (percentage of the size of the filter. e.g. 50# = median filter).
        # The size of the gaussian filter is "SzGauss" and the standard deviation
        # is "SigGauss".
        szOrd = 7

        for i in range(10):
            #  replaces each element in A by the orderth element in the sorted set of neighbors specified by the nonzero elements in domain.
            # filtData = ordfilt2(filtData, order, szOrd)
            if sys.platform == 'win32':
                filtData = scipy.ndimage.median_filter(filtData, footprint=N.ones((szOrd, szOrd)))
            else:
                filtData = ndimage.median_filter(filtData, footprint=N.ones((szOrd, szOrd)))
            # filtData = scipy.ndimage.median_filter(filtData, footprint=N.ones((szOrd, szOrd)))
            # filtData = scipy.ndimage.generic_filter(filtData,)
            # re-put measured values where there were some.
            filtData[ifinite] = data_chla[ifinite]

        # replace zero values with NaN
        filtData[filtData == 0] = N.nan

        # Store original data and filterdata after median filter
        ifinite_edge = [data_chla > 0.0] and [N.invert(N.isfinite(filtData))]
        filtData[ifinite_edge] = data_chla[ifinite_edge]

        # apply gaussian filter
        if sys.platform == 'win32':
            filtData = scipy.ndimage.gaussian_filter(filtData, 2, truncate=1)  # ,truncate=1.25
        else:
            filtData = ndimage.gaussian_filter(filtData, 2, truncate=1)  # ,truncate=1.25

        # re-put original measured values on the edges
        ifinite_edge = [data_chla > 0.0] and [
            N.invert(N.isfinite(filtData))]  # N.invert(N.isfinite(filtData))] and [N.isfinite(data)]
        filtData[ifinite_edge] = data_chla[ifinite_edge]

        ###########################################
        ##########  FrontProcessing ###############
        ###########################################
        # Compute the Pixel Size in km
        # X-axis (dlon) gradient by km (!! pix_km_dx varies with latitude!!)
        for il in range(nl):
            nl_lat_value = ymin + (il * pixel_shift_lat)
            d = abs(pixel_shift_lat)  # 0.008928571428571
            const_d2km = 12364.35
            area_deg = d * d * math.cos(old_div(nl_lat_value, 180) * math.pi)
            # area_km = area_deg * const_d2km
            # For opfish approximation
            # const_d2km = 12364.35
            # area_km_equator = abs(mapset_info.pixel_shift_lat) * abs(mapset_info.pixel_shift_long) * const_d2km
            area_km = old_div((area_deg * const_d2km), pix_km_dy_mat)
            # area_km = (area_deg * const_d2km) / 4.58
            # if (nl_lat_value != 0):
            pix_km_dx_mat = N.zeros(ns)
            pix_km_dx_mat.fill(area_km)

            pix_km_dx_mat.shape = (1, -1)
            #
            # outband.WriteArray(N.array(pix_km_dx_mat),0,il)

        # Dx=conv2(data,filterx,'same')./pix_km_dx_mat
        # Canny filter - 1st Gaussian derivative
        # from scipy.ndimage.filters import gaussian_filter1d
        # gauss_x = gaussian_filter1d(filtData, sigma_x1, axis=0, order=1, truncate=1)
        if sys.platform == 'win32':
            gauss_x = scipy.ndimage.convolve(filtData, filter_x)
        else:
            gauss_x = ndimage.convolve(filtData, filter_x)

        canny_x = N.divide(gauss_x, pix_km_dx_mat)
        # Normalize by the filter size (~6 for Nxy=7) to compute gradient in unit/km
        # Dx=Dx./sum(sum(abs(filterx)));
        divisor = N.sum(N.absolute(filter_x))  # 2.3754
        # canny_x = canny_x / N.sum(N.absolute(filter_x))
        canny_x = N.divide(canny_x, divisor)

        if sys.platform == 'win32':
            gauss_y = scipy.ndimage.convolve(filtData, filter_y)
        else:
            gauss_y = ndimage.convolve(filtData, filter_y)

        # canny_y = gaussian_filter1d(filtData, sigma_y1, axis=0, order=1, truncate=1)
        canny_y = N.divide(gauss_y, pix_km_dy_mat)
        # Write out the full matrix N.array(outData)
        # outband.WriteArray(canny_y, 0, 0)
        # data_gradient = chla_gradient
        divisor_y = N.sum(N.absolute(filter_y))
        # canny_x = canny_x / N.sum(N.absolute(filter_x))
        canny_y = N.divide(canny_y, divisor_y)

        ###GradNorm = sqrt(Dx. * Dx + Dy. * Dy);
        squared_val = (canny_x * canny_x) + (canny_y * canny_y)
        gradNorm = N.sqrt(squared_val)

        # # Write out the full matrix N.array(outData)
        outband.WriteArray(gradNorm, 0, 0)
        input_list = []
        input_list.append(input_file)

        # #   Close outputs
        outDrv = None
        outDS = None
        # logger.warning('Writing MetaData not done yet ! To be implemented ...')
        # assign_metadata_processing(input_list, output_file)

    except:
        logger.warning('Error in compute_opFish_indicator. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

# ##########################
#  Compute opFish indicator#
############################
def compute_opFish_indicator(input_file='', nodata=None, output_file='', output_nodata=None, output_format=None,
                             output_type=None, options='', parameters=None):
    try:
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        output_file_final = output_file
        output_file = tmpdir + os.sep + os.path.basename(output_file)
        ##############
        #  constants #
        ##############

        filter_x = N.array([[0.325531532740751, 0.0000,  -0.325531532740751], [0.536710762313292, 0, -0.536710762313292], [0.325531532740751, -0.0000, -0.325531532740751]])
        pix_km_dy_mat = 4.633
        filter_y = N.array([[0.3255, 0.5367, 0.3255], [0, 0, 0], [-0.3255, -0.5367, -0.3255]])

        ###########################################
        # ~~~~~OPFIsh   Constants~~~~~~~~~~~~~~~~#
        ###########################################

        # Parameters is expected to be None, or a dictionary
        if parameters is not None:

            if 'chl_grad_min' in list(parameters.keys()):
                chl_grad_min = parameters['chl_grad_min']
            else:
                chl_grad_min = 0.00032131   #chl_grad_min = 0.00032131  # perc.5th of all species reconstructed OBS by group -- NEW VALUES BY JEON

            if 'chl_grad_int' in list(parameters.keys()):
                chl_grad_int = parameters['chl_grad_int']
            else:
                chl_grad_int = 0.021107  #chl_grad_int = 0.021107# linear fit from 0.09 to 1 (minimum mobility of species)

            if 'chl_feed_min' in list(parameters.keys()):
                chl_feed_min = parameters['chl_feed_min']
            else:
                chl_feed_min = 0.08 #chl_feed_min = 0.08  # mgChl/m3 - minimum among species

            if 'chl_feed_max' in list(parameters.keys()):
                chl_feed_max = parameters['chl_feed_max']
            else:
                chl_feed_max = 11.0 #chl_feed_max = 11.0  # perc.98th green MESOZOOPK, perc.99.3th total MESOZOOPK;

            if 'dc' in list(parameters.keys()):
                dc = parameters['dc']
            else:
                dc = 0.91  #0.91  # (1-dc = 0.09, it is 0.10 in the Arctic report)

   # Compute Juliean calender date
        year_month_day = functions.get_date_from_path_full(input_file)
        dayOfYear = functions.conv_date_yyyymmdd_2_doy(year_month_day)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # open chla file
        chla_fileID = gdal.Open(input_file, GA_ReadOnly)

        # create masked file as gdal object based on input dimension
        masked_fileID = clip_landmask_inputdimension(chla_fileID)

        functions.check_output_dir(os.path.dirname(output_file))

        # Read info from file, size are equal for all input files eg. sst, par
        nb = chla_fileID.RasterCount
        ns = chla_fileID.RasterXSize
        nl = chla_fileID.RasterYSize

        # Array for mask band
        if masked_fileID is not None:
            mask_band = masked_fileID.GetRasterBand(1)
            mask_data = mask_band.ReadAsArray(0, 0, ns, nl).astype(float)
        else:
            mask_data = None

        dataType = chla_fileID.GetRasterBand(1).DataType

        geoTransform = chla_fileID.GetGeoTransform()
        projection = chla_fileID.GetProjection()
        driver_type = chla_fileID.GetDriver().ShortName

        ymin = geoTransform[3]
        pixel_shift_lat = geoTransform[5]

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and nodata is not None:
            output_nodata = nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType = dataType
        else:
            outType = ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat = driver_type
        else:
            outFormat = output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, 1, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)
        #
        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        chl_band = chla_fileID.GetRasterBand(1)

        data_chla = chl_band.ReadAsArray(0, 0, ns, nl).astype(float)

        # Replace the nodata value with Nan
        data_chla[data_chla == nodata] = N.nan

        ###########################################
        ##########  Extrapolate ###################
        ###########################################
        # Copy the data to filter data
        filtData = N.copy(data_chla)

        # Replace NaN values with zeros(for eStation data)
        filtData[N.invert(N.isfinite(data_chla))] = 0

        ifinite = N.isfinite(data_chla)  # ifinite = isfinite(Data)

        szOrd = 7
        for i in range(10):
            if sys.platform == 'win32':
                filtData = scipy.ndimage.median_filter(filtData, footprint=N.ones((szOrd, szOrd)))
            else:
                filtData = ndimage.median_filter(filtData, footprint=N.ones((szOrd, szOrd)))
            # re-put measured values where there were some.
            filtData[ifinite] = data_chla[ifinite]

        # replace zero values with NaN
        filtData[filtData == 0] = N.nan

        # Store original data and filterdata after median filter
        ifinite_edge = [data_chla > 0.0] and [N.invert(N.isfinite(filtData))]
        filtData[ifinite_edge] = data_chla[ifinite_edge]

        # apply gaussian filter
        if sys.platform == 'win32':
            filtData = scipy.ndimage.gaussian_filter(filtData, 2, truncate=1)  # ,truncate=1.25
        else:
            filtData = ndimage.gaussian_filter(filtData, 2, truncate=1)

        # re-put original measured values on the edges
        ifinite_edge = [data_chla > 0.0] and [
            N.invert(N.isfinite(filtData))]
        filtData[ifinite_edge] = data_chla[ifinite_edge]

        ###########################################
        ##########  FrontProcessing ###############
        ###########################################
        # Compute the Pixel Size in km
        pix_km_dx_mat = filtData * N.nan
        for il in range(nl):
            nl_lat_value = ymin + (il * pixel_shift_lat)
            d = abs(pixel_shift_lat)  # 0.008928571428571
            const_d2km = 12363.9869   #12364.35
            area_deg = d * d * math.cos(old_div(nl_lat_value, 180) * math.pi)
            area_km = old_div((area_deg * const_d2km), pix_km_dy_mat)
            pix_km_dx_mat[il,:] = area_km

        if sys.platform == 'win32':
            gauss_x = scipy.ndimage.convolve(filtData, filter_x)
        else:
            gauss_x = ndimage.convolve(filtData, filter_x)
        canny_x = N.divide(gauss_x, pix_km_dx_mat)
        divisor = N.sum(N.absolute(filter_x))  # 2.3754
        canny_x = N.divide(canny_x, divisor)

        if sys.platform == 'win32':
            gauss_y = scipy.ndimage.convolve(filtData, filter_y)
        else:
            gauss_y = ndimage.convolve(filtData, filter_y)

        canny_y = N.divide(gauss_y, pix_km_dy_mat)
        divisor_y = N.sum(N.absolute(filter_y))
        canny_y = N.divide(canny_y, divisor_y)

        squared_val = (canny_x * canny_x) + (canny_y * canny_y)
        gradNorm = N.sqrt(squared_val)

        ###########################################
        ##########  gradCHL2FeedingFit ############
        ###########################################

        feed_hab = gradNorm * N.nan
        feed_hab_condition = (gradNorm < chl_grad_min)
        feed_hab[feed_hab_condition] = 0

        # Slope and intercept of linear fit in natural log
        delta_y = dc
        delta_x = N.log(chl_grad_int) - N.log(chl_grad_min)
        sl_hab = old_div(delta_y, delta_x)
        # intercept = equation of straight line y = mx+b where m is slope
        in_hab = 1 - sl_hab * N.log(chl_grad_int)
        linear_interp = (gradNorm >= chl_grad_min) * (gradNorm <= chl_grad_int)

        # linear interp
        feed_hab[linear_interp] = sl_hab * N.log(gradNorm[linear_interp]) + in_hab
        feed_hab[gradNorm > chl_grad_int] = 1

        #Force no feeding habitat for these conditions
        feed_hab[filtData < chl_feed_min] = 0
        feed_hab[filtData > chl_feed_max] = 0
        feed_hab[0, :], feed_hab[1, :], feed_hab[2, :], feed_hab[3, :], feed_hab[4, :], feed_hab[5, :], feed_hab[6, :], feed_hab[7, :], feed_hab[8, :], feed_hab[9, :]  =N.nan, N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan
        feed_hab[-1, :], feed_hab[-3, :], feed_hab[-2, :], feed_hab[-4, :], feed_hab[-5, :],feed_hab[-6, :], feed_hab[-7, :], feed_hab[-8, :], feed_hab[-9, :], feed_hab[-10, :] =N.nan, N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan
        feed_hab[:, 0], feed_hab[:, 1], feed_hab[:, 2], feed_hab[:, 3],feed_hab[:, 4], feed_hab[:, 5], feed_hab[:, 6], feed_hab[:, 7], feed_hab[:, 8],feed_hab[:, 9]= N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan
        feed_hab[:, -1], feed_hab[:, -2], feed_hab[:, -3], feed_hab[:, -4], feed_hab[:, -5],feed_hab[:, -6], feed_hab[:, -7], feed_hab[:, -8], feed_hab[:, -9], feed_hab[:, -10]= N.nan, N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan,N.nan
        ###########################################
        #########  FeedingHabit2OPFish ############
        ###########################################
        for il in range(nl):

            data = feed_hab[il]
            nl_lat_value = ymin + (il * pixel_shift_lat)
            daylength_val = get_daylength(dayOfYear, nl_lat_value)
            if mask_data is not None:
                data = data * mask_data[il]
            wtp = (data >= 0) * (data <= 100)
            opFish = N.zeros(chla_fileID.RasterXSize)
            if output_nodata is not None:
                opFish = opFish + output_nodata

            if wtp.any():
                opFish[wtp] = data[wtp] * (old_div(daylength_val, 24))
            opFish.shape = (1, -1)
            outband.WriteArray(opFish, 0, il)

        input_list = []
        input_list.append(input_file)
        # #   Close outputs
        outDrv = None
        outDS = None
        # logger.warning('Writing MetaData not done yet ! To be implemented ...')
        assign_metadata_processing(input_list, output_file, parameters=parameters)

    except:
        logger.warning('Error in compute_opFish_indicator. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)
    else:
        shutil.move(output_file, output_file_final)
    finally:
        shutil.rmtree(tmpdir)

def clip_landmask_inputdimension(input_file_gdalobj):

    landmask_file = es_constants.es2globals['estation2_layers_dir']+os.path.sep+'landmask_Earth_byte.tif'
    created_file_masked = None

    if not os.path.isfile(landmask_file):
        return None

    ulx, xres, xskew, uly, yskew, yres = input_file_gdalobj.GetGeoTransform()
    lrx = ulx + (input_file_gdalobj.RasterXSize * xres)
    lry = uly + (input_file_gdalobj.RasterYSize * yres)

    d_lon_min = ulx
    d_lat_min = lry
    d_lon_max = lrx
    d_lat_max = uly

    output_file_naming = str(abs(int(d_lon_min)))+str(abs(int(d_lat_min)))+str(abs(int(d_lon_max)))+str(abs(int(d_lat_max)))+ '_masked_landmask_byte.tif'
    output_masked_tif = es_constants.es2globals['estation2_layers_dir'] + os.path.sep + output_file_naming

    #If already exists then just return the file
    if os.path.isfile(output_masked_tif):
        created_file_masked = gdal.Open(output_masked_tif, GA_ReadOnly)
        return created_file_masked
    command = 'gdalwarp -te {} {} {} {} -tr {} {} -r bilinear {} {}'.format(
        d_lon_min, d_lat_min, d_lon_max, d_lat_max, abs(xres), abs(yres), landmask_file, output_masked_tif)

    os.system(command)

    if os.path.isfile(output_masked_tif):
        created_file_masked = gdal.Open(output_masked_tif, GA_ReadOnly)

    return created_file_masked


# _____________________________
#   Write metadata to an output file.
#   Most of the metadata are copied from an input file (including datatype, scaling, frequency) because we cannot read from
#   the DB -> this is prone to errors !!! we should either
#       1. Populate the DB from the procssing chain.
#       2. Stop if the output product is not define din DB
#

def assign_metadata_processing(input_file_list, output_file, parameters=None):
    # Create Metadata object
    sds_meta = metadata.SdsMetadata()

    # Check if the input file is single, or a list
    if isinstance(input_file_list, list) or isinstance(input_file_list, tuple):
        first_input = input_file_list[0]
    else:
        first_input = input_file_list

    try:
        # Open and read metadata from the 'first' input file
        sds_meta.read_from_file(first_input)

        # If parameters is defined, assign it
        if parameters is not None:
            sds_meta.assign_parameters(parameters)

        # Modify/Assign some of the metadata
        sds_meta.assign_comput_time_now()
        str_date, productcode, subproductcode, mapset, version = functions.get_all_from_filename(
            os.path.basename(output_file))

        #   TODO-M.C.: cannot read metadata from database for a newly created product ! Copy from input file ?
        #
        sds_meta.assign_from_product(productcode, subproductcode, version)

        sds_meta.assign_date(str_date)
        sds_meta.assign_input_files(input_file_list)

        # Define subdirectory
        sub_directory = functions.set_path_sub_directory(productcode, subproductcode, 'Derived', version, mapset)
        sds_meta.assign_subdir(sub_directory)

        # Write Metadata
        sds_meta.write_to_file(output_file)
    except:
        logger.error('Error in assign metadata.')
        raise Exception('Error in assign metadata')


######################################################################################
#   get_daylength
#   Purpose: From dayOfYear, lat -> daylength(in Hrs)
#   Author: Vijay Charan Venkatachalam, JRC, European Commission
#   Date: 2020/02/04
#   Inputs: dayOfYear, lat
#   Output: daylength
#   Description: returns daylength
#
def get_daylength(dayOfYear, lat):
    # The below code has been created by transforming the matlab code available in
    # https://it.mathworks.com/matlabcentral/fileexchange/20390-day-length?focused=3885297&tab=function
    # This calculates the number of hours (hours) and fraction of the day (b) in #daylight.
    # Inputs:
    # Day - day of the year, counted starting with the day of the December solstice in the first year of a Great Year.
    # Latitude - latitude in degrees, North is positive, South is negative
    #
    # Calculations are per Herbert Glarner's formulae which do not take into account refraction, twilight, size of the sun, etc. (http://herbert.gandraxa.com/herbert/lod.asp but be careful about inconsistencies in radians/degrees).
    #
    # Copyright (c) 2015, Travis Wiens
    # All rights reserved.
    #
    # Redistribution and use in source and binary forms, with or without
    # modification, are permitted provided that the following conditions are
    # met:
    #
    #    * Redistributions of source code must retain the above copyright
    #      notice, this list of conditions and the following disclaimer.
    #    * Redistributions in binary form must reproduce the above copyright
    #      notice, this list of conditions and the following disclaimer in
    #      the documentation and/or other materials provided with the distribution
    #
    axis = old_div(23.439 * math.pi, 180)
    j_contant = math.pi / 182.625
    m = 1- math.tan(old_div(lat*math.pi,180)) * math.tan(axis * math.cos(j_contant*dayOfYear))

    if m > 2:   #saturate value for artic
        m = 2
    if m < 0:
        m = 0

    b = old_div(math.acos(1-m),math.pi)   # fraction of the day the sun is up
    return b*24  #hours of sunlight

