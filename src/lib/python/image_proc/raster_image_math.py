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

# Import eStation lib modules
from lib.python import es_logging as log
from lib.python import metadata
from lib.python import functions
from config import es_constants

# Import third-party modules
from osgeo.gdalconst import *
from osgeo import gdal
import numpy as N
import copy
import os, re, os.path, time, sys
import pymorph

logger = log.my_logger(__name__)

# _____________________________
def do_avg_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', output_stddev=None, ):

    # Note: no 'update' functionality is foreseen -> creates output EVERY TIME
    try:
        # Force input to be a list
        input_list = return_as_list(input_file)

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
        fidT=gdal.Open(input_list[0], GA_ReadOnly)
        nb=fidT.RasterCount
        ns=fidT.RasterXSize
        nl=fidT.RasterYSize
        dataType=fidT.GetRasterBand(1).DataType
        geotransform=fidT.GetGeoTransform()
        projection=fidT.GetProjection()
        driver_type=fidT.GetDriver().ShortName

        # manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # instantiate output/sll
        outDrv=gdal.GetDriverByName(outFormat)
        outDS=outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetProjection(projection)
        outDS.SetGeoTransform(geotransform)


        if output_stddev != None:
            outStd = gdal.GetDriverByName(output_format)
            stdDs = outStd.Create(output_stddev, ns, nl, nb, outType, options_list)
            stdDs.SetProjection(projection)
            stdDs.SetGeoTransform(geotransform)

        # pre-open input files
        rangenl = range(nl)
        rangeFile = range(len(input_list))
        fid = []
        for ifid in rangeFile:
            fid.append(gdal.Open(input_list[ifid], GA_ReadOnly))

        # Loop over bands
        for ib in range(nb):
            outband = outDS.GetRasterBand(ib+1)

            # parse image by line
            for il in rangenl:
                counter = N.zeros(ns)
                accum = N.zeros(ns)
                # for all files:
                for ifile in rangeFile:
                    data = N.ravel(fid[ifile].GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1).astype(float))

                    # variable initialization
                    if (ifile==0):
                        if input_nodata is None:
                            avgData = data
                            stdData = N.multiply(data , data)
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
                    outData[wnz] = avgData[wnz]/(counter[wnz])

                if output_nodata != None:
                    wzz = (counter == 0)
                    if wzz.any():
                        outData[wzz] = output_nodata

                # Check if stddev also required
                if output_stddev != None:
                    outDataStd = N.zeros(ns)
                    if wnz.any():
                        outDataStd[wnz] = N.sqrt( stdData[wnz]/(counter[wnz]) - N.multiply(outData[wnz],outData[wnz]) )
                    if output_nodata != None:
                        wzz = (counter == 0)
                        if wzz.any():
                            outDataStd[wzz] = output_nodata

                    outDataStd.shape = (1, -1)
                    stdDs.GetRasterBand(ib+1).WriteArray(N.array(outDataStd), 0, il)

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
        if os.path.isfile(output_stddev):
            os.remove(output_stddev)

# _____________________________
def do_min_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', index_file=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    #       'The optional index file will store the file index (position in input-list) used for the minimum.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??

    try:
        # Force input to be a list
        input_list = return_as_list(input_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # get infos from the last file (to manage case of 'upgraded' DataType - e.g. FEWSNET).
        nFiles=len(input_list)
        f1Fid = gdal.Open(input_list[nFiles-1], GA_ReadOnly)
        nb = f1Fid.RasterCount
        ns = f1Fid.RasterXSize
        nl = f1Fid.RasterYSize
        dataType = f1Fid.GetRasterBand(1).DataType
        geoTransform = f1Fid.GetGeoTransform()
        projection = f1Fid.GetProjection()
        driver_type=f1Fid.GetDriver().ShortName

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

        # manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # instantiate output(s)
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType,options_list)
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
        fidList=[]
        for ii in range(len(input_file)):
            fidList.append(gdal.Open(input_file[ii], GA_ReadOnly))

        for ib in range(nb):
            outband = outDS.GetRasterBand(ib+1)
            if index_file is not None:
                indexBand = indexDS.GetRasterBand(ib+1)

            for il in range(nl):

                for ifile in range(len(input_file)):
                    fid = fidList[ifile]
                    data = N.ravel(fid.GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1).astype(float))

                    if (ifile == 0):
                        # initial value set on first file
                        minData = data
                        if (input_nodata is None):
                            indexData = N.zeros(ns)
                        else:
                            indexData = N.zeros(ns)-1
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
                            wtf = (minData == output_nodata ) * (data != input_nodata)

                            if wtp.any():
                                minData[wtp] = data[wtp]
                                indexData[wtp] = ifile

                            if wtf.any():
                                minData[wtf] = data[wtf]
                                indexData[wtf] = ifile

                minData.shape = (1,-1)
                indexData.shape = (1,-1)

                outband.WriteArray(N.array(minData),0,il)
                if indexDS is not None:
                    #indexBand.WriteArray(gdalnumeric.array(indexData), 0, il)
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

# _____________________________
def do_max_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', index_file=None, min_num_valid=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    #       'The optional index file will store the file index (position in input-list) used for the minimum.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??

    try:
        # Force input to be a list
        input_list = return_as_list(input_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # get infos from the last file (to manage case of 'upgraded' DataType - e.g. FEWSNET).
        nFiles=len(input_list)
        f1Fid = gdal.Open(input_list[nFiles-1], GA_ReadOnly)
        nb = f1Fid.RasterCount
        ns = f1Fid.RasterXSize
        nl = f1Fid.RasterYSize
        dataType = f1Fid.GetRasterBand(1).DataType
        geoTransform = f1Fid.GetGeoTransform()
        projection = f1Fid.GetProjection()
        driver_type=f1Fid.GetDriver().ShortName

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

        # manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

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
        fidList=[]
        for ii in range(len(input_file)):
            fidList.append(gdal.Open(input_file[ii], GA_ReadOnly))

        for ib in range(nb):
            outband = outDS.GetRasterBand(ib+1)
            if index_file is not None:
                indexBand = indexDS.GetRasterBand(ib+1)

            for il in range(nl):
                counter = N.zeros(ns)
                for ifile in range(len(input_file)):
                    fid = fidList[ifile]
                    data = N.ravel(fid.GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1).astype(float))

                    if (ifile == 0):
                        maxData = data
                        if (input_nodata is None):
                            indexData = N.zeros(ns)
                            counter[:] = 1.0
                        else:
                            indexData = N.zeros(ns)-1
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
                            wtf = (maxData == input_nodata)*(data!=input_nodata)
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

                maxData.shape = (1,-1)
                indexData.shape = (1,-1)
                outband.WriteArray(N.array(maxData),0,il)
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

#   _____________________________
def do_med_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', min_num_valid=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??
    # TODO-M.C.: : NODATA now are considered as 'normal' values ... should be removed !

    try:
        # Force input to be a list
        input_list = return_as_list(input_file)

        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # get infos from the last file (to manage case of 'upgraded' DataType - e.g. FEWSNET).
        nFiles=len(input_list)
        f1Fid = gdal.Open(input_list[nFiles-1], GA_ReadOnly)
        nb = f1Fid.RasterCount
        ns = f1Fid.RasterXSize
        nl = f1Fid.RasterYSize
        dataType = f1Fid.GetRasterBand(1).DataType
        geoTransform = f1Fid.GetGeoTransform()
        projection = f1Fid.GetProjection()
        driver_type=f1Fid.GetDriver().ShortName

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

        # manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # instantiate output(s)
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # pre-open files, to speed up processing
        fidList=[]
        for ii in range(len(input_list)):
            fidList.append(gdal.Open(input_file[ii], GA_ReadOnly))

        for ib in range(nb):
            outband = outDS.GetRasterBand(ib+1)

            # Do a line at a time ...
            for il in range(nl):

                accum = N.zeros( (len(input_list),ns) )

                for ifile in range(len(input_file)):
                    fid = fidList[ifile]
                    data = N.ravel(fid.GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1).astype(float))

                    accum[ifile,:] = data

                try:
                    medianOut = N.median(accum, axis=0)
                except:
                    medianOut = N.median(accum)

              # # manage 'minvalid' option
                # if min_num_valid is not None:
                #     wtb = (counter < min_num_valid)
                #     if wtb.any():
                #         maxData[wtb] = output_nodata

                medianOut.shape = (1,-1)
                outband.WriteArray(N.array(medianOut),0,il)

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

# _____________________________
def do_oper_subtraction(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):
    #
    # Notes:'The command expects exactly 2 files in input.'

    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

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
        driver_type=fid0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata=float(sds_meta.get_nodata_value(input_file[0]))
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
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType,options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        for ib in range(nb):
            for il in range(nl):
                data0 = N.ravel(fid0.GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1)).astype(float)
                data1 = N.ravel(fid1.GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1)).astype(float)

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

                dataout.shape=(1,-1)
                outDS.GetRasterBand(ib+1).WriteArray(N.array(dataout), 0, il)

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

# _____________________________
def do_oper_division_perc(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):
    
    # Returns the IN1/IN2 * 100; IN1/IN2 might have various datatype (int, float, ...) but internally treated as float
    # Notes:'The command expects exactly 2 files in input.'
    epsilon = 1e-10

    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

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
        driver_type=fid0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata=float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        # TODO-M.C. Replace by calling ReturnNoData
        if input_nodata is None:
            input_nodata = -32768.0

        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType,options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        for ib in range(nb):
            for il in range(nl):
                data0 = N.ravel(fid0.GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1)).astype(float)
                data1 = N.ravel(fid1.GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1)).astype(float)

                if input_nodata is None:
                    wtc = (N.abs(data1) > epsilon)
                else:
                    wtc = (data0 != input_nodata) * (data1 != input_nodata) * (N.abs(data1) > epsilon)


                # TODO-M.C.: check this assignment is done for the other functions as well
                dataout=N.zeros(ns).astype(float)
                if output_nodata is None:
                    dataout=N.zeros(ns).astype(float) + output_nodata

            if wtc.any():
                dataout[wtc] = data0[wtc]/data1[wtc]

                dataout = dataout*100.00
                dataout = dataout.round()
                dataout.shape=(1,-1)
                outDS.GetRasterBand(ib+1).WriteArray(N.array(dataout), 0, il)

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

# _____________________________
def do_oper_scalar_multiplication(input_file='', output_file='', scalar=1, input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):
    #
    # Notes:'The command expects exactly 1 file in input.'

    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # Open input file
        fid0 = gdal.Open(input_file[0], GA_ReadOnly)

        # Read info from file
        nb = fid0.RasterCount
        ns = fid0.RasterXSize
        nl = fid0.RasterYSize
        dataType = fid0.GetRasterBand(1).DataType
        geoTransform = fid0.GetGeoTransform()
        projection = fid0.GetProjection()
        driver_type=fid0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata=float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType,options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        scalarArray=N.zeros(ns)+scalar

        for ib in range(nb):
            for il in range(nl):
                data0 = N.ravel(fid0.GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1)).astype(float)

                if input_nodata is None:
                    dataout = data0 * scalarArray
                else:
                    wtc = (data0 != input_nodata)
                    dataout = N.zeros(ns)
                    if input_nodata is not None:
                        dataout = N.zeros(ns) + output_nodata
                    if wtc.any():
                        dataout[wtc] = data0[wtc] * scalarArray[wtc]

                dataout.shape=(1,-1)
                outDS.GetRasterBand(ib+1).WriteArray(N.array(dataout), 0, il)

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

# _____________________________
def do_make_vci(input_file='', min_file='', max_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):

    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

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
        driver_type=fileFID.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file):
                input_nodata=float(sds_meta.get_nodata_value(input_file))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType,options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        indata = fileFID.GetRasterBand(1)
        inmin = minFID.GetRasterBand(1)
        inmax = maxFID.GetRasterBand(1)

        for il in range(fileFID.RasterYSize):
            data   = N.ravel(indata.ReadAsArray(0, il, indata.XSize, 1))
            minVal = N.ravel(inmin.ReadAsArray(0, il, inmin.XSize, 1))
            maxVal = N.ravel(inmax.ReadAsArray(0, il, inmax.XSize, 1))

            datatype=data.dtype
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
                vci[wtp] = 100.0 * (1.0*data[wtp] - 1.0*minVal[wtp])/(1.0*maxVal[wtp]-1.0*minVal[wtp])

            vci=vci.round()
            vci.shape = (1,-1)
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

# _____________________________
def do_make_baresoil(input_file='', min_file='', max_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', delta_ndvi_max=0.15, ndvi_max=0.14):

#
#   Compute a mask for identifying 'baresoil' from a single NDVI image - based on the condition:
#
#   deltaNDVI < deltaNDVImax AND curr_NDVI < NDVImax
#
#   where: deltaNDVI is Max-Min for the current year
#
#   Output: 0 (or output_nodata)-> baresoil/no-data, 1 -> vegetated
#
#   Note: nodata are considered only in the NDVIcurr file (NOT in min/max).
#
    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # open files
        fileFID = gdal.Open(input_file, GA_ReadOnly)
        if min_file != '' and max_file != '':
            minFID = gdal.Open(min_file, GA_ReadOnly)
            maxFID = gdal.Open(max_file, GA_ReadOnly)

        # Read info from file
        nb = fileFID.RasterCount
        ns = fileFID.RasterXSize
        nl = fileFID.RasterYSize
        dataType = fileFID.GetRasterBand(1).DataType
        geoTransform = fileFID.GetGeoTransform()
        projection = fileFID.GetProjection()
        driver_type=fileFID.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file):
                input_nodata=float(sds_meta.get_nodata_value(input_file))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # instantiate output
        outDrv = gdal.GetDriverByName(outFormat)
        outDS = outDrv.Create(output_file, ns, nl, nb, outType,options_list)
        outDS.SetGeoTransform(geoTransform)
        outDS.SetProjection(projection)

        # assume only 1 band
        outband = outDS.GetRasterBand(1)
        indata = fileFID.GetRasterBand(1)
        if min_file != '' and max_file != '':
            inmin = minFID.GetRasterBand(1)
            inmax = maxFID.GetRasterBand(1)

        for il in range(fileFID.RasterYSize):
            data   = N.ravel(indata.ReadAsArray(0, il, indata.XSize, 1))
            if min_file != '' and max_file != '':
                minVal = N.ravel(inmin.ReadAsArray(0, il, inmin.XSize, 1))
                maxVal = N.ravel(inmax.ReadAsArray(0, il, inmax.XSize, 1))
                deltaVal = maxVal - minVal

            datatype=data.dtype
            if input_nodata is None:
                dataout = N.zeros(ns)
            else:
                dataout = N.zeros(ns) + output_nodata

            # Identify 'bare' pixels (or nodata)
            if min_file != '' and max_file != '':
                w_bare = (data < ndvi_max) * (deltaVal < delta_ndvi_max)
            else:
                w_bare = (data < ndvi_max)

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

            mask.shape = (1,-1)
            outband.WriteArray(mask, 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Writes metadata to output
        input_list = []
        input_list.append(input_file)
        input_list.append(min_file)
        input_list.append(max_file)
        assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_make_baresoil. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)

# _____________________________
def do_mask_image(input_file='', mask_file='', output_file='',output_format=None,
           output_type=None, options='', mask_value=1, out_value=0):

# _____________________________
#
#   Copy input to output, by setting to out_value all pixel where mask=mask_value
#

    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

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
        driver_type=fileFID.GetDriver().ShortName

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

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
            data   = N.ravel(indata.ReadAsArray(0, il, indata.XSize, 1))
            maskVal = N.ravel(inmask.ReadAsArray(0, il, inmask.XSize, 1))

            datatype=data.dtype

            wtp = (maskVal == mask_value)

            output = data
            if wtp.any():
                output[wtp] = out_value

            output.shape = (1,-1)

            outband.WriteArray(output, 0, il)

        #   ----------------------------------------------------------------------------------------------------
        #   Writes metadata to output
        input_list = []
        input_list.append(input_file)
        input_list.append(mask_file)
        #   Close outputs
        outDrv = None
        outDS = None
        #assign_metadata_processing(input_list, output_file)
    except:
        logger.warning('Error in do_mask_image. Remove outputs')
        if os.path.isfile(output_file):
            os.remove(output_file)

# _____________________________
def do_cumulate(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', output_stddev=None, scale_factor=None):

    # Notes:'The command expects exactly 1 file in input.'

    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

        # Open input file
        fid0 = gdal.Open(input_file[0], GA_ReadOnly)

        # Read info from file
        nb = fid0.RasterCount
        ns = fid0.RasterXSize
        nl = fid0.RasterYSize
        dataType = fid0.GetRasterBand(1).DataType
        geoTransform = fid0.GetGeoTransform()
        projection = fid0.GetProjection()
        driver_type=fid0.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file[0]):
                input_nodata=float(sds_meta.get_nodata_value(input_file[0]))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

        # instantiate outputs
        outDrv=gdal.GetDriverByName(outFormat)
        outDS=outDrv.Create(output_file, ns, nl, nb, outType, options_list)
        outDS.SetProjection(projection)
        outDS.SetGeoTransform(geoTransform)

        # TODO-M.C.: is that to be implemented ? ever used ?
        # if statusmapOut is not None:
        #     outSMDrv = gdal.GetDriverByName(format)
        #     smDs = outSMDrv.Create(statusmapOut, ns, nl, nb, ParseType('UInt16'), options)
        #     smDs.SetProjection(projection)
        #     smDs.SetGeoTransform(geotransform)

        # pre-open the files
        rangenl = range(nl)
        rangeFile = range(len(input_file))
        fid = []
        for ifid in rangeFile:
            fid.append(gdal.Open(input_file[ifid], GA_ReadOnly))

        for ib in range(nb):
            outband = outDS.GetRasterBand(ib+1)

            # parse image by line
            for il in rangenl:
                    counter = N.zeros(ns)

                    # for all files:
                    for ifile in rangeFile:
                        data = N.ravel(fid[ifile].GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1).astype(float))

                        if (ifile==0):
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
                            outData[wnz] = cumData[wnz]*float(scale_factor)

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

# _____________________________
def do_compute_perc_diff_vs_avg(input_file='', avg_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):

    # TODO-M.C.: check (and make uniform across functions()) data type
    epsilon = 1e-10

    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

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
        driver_type=fileFID.GetDriver().ShortName

        # Try and assign input_nodata if it is UNDEF
        if input_nodata is None:
            sds_meta = metadata.SdsMetadata()
            if os.path.exists(input_file):
                input_nodata=float(sds_meta.get_nodata_value(input_file))
            else:
                logger.info('Test file not existing: do not assign metadata')

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and input_nodata is not None:
            output_nodata = input_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

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
            data   = N.ravel(indata.ReadAsArray(0, il, indata.XSize, 1))
            avgVal = N.ravel(inavg.ReadAsArray(0, il, inavg.XSize, 1))

            datatype=data.dtype

            if input_nodata is not None:
                nodata=N.zeros(1,datatype) + input_nodata
                wtp = (data != nodata) * (avgVal != nodata) * (avgVal > epsilon)
            else:
                wtp = (avgVal > epsilon)

            diff = N.zeros(indata.XSize)
            if output_nodata is not None:
                diff = diff + output_nodata

            if wtp.any():
                diff[wtp] = 100.0 * (1.0*data[wtp] - 1.0*avgVal[wtp])/(1.0*avgVal[wtp])

            diff=diff.round()
            diff.shape = (1,-1)
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

# _____________________________
def do_compute_primary_production(chla_file='', sst_file='', kd_file='', par_file='',
                                  chla_nodata=None, sst_nodata=None, kd_nodata=None, par_nodata=None,
                                  output_file='', output_nodata=None, output_format=None, output_type=None,
                                  options=''):

    try:
        # Manage options
        options_list = [es_constants.ES2_OUTFILE_OPTIONS]
        options_list.append(options)

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
        driver_type=chla_fileID.GetDriver().ShortName

        # Force output_nodata=input_nodata it the latter is DEF and former UNDEF
        if output_nodata is None and chla_nodata is not None:
            output_nodata = chla_nodata

        # Manage out_type (take the input one as default)
        if output_type is None:
            outType=dataType
        else:
            outType=ParseType(output_type)

        # manage out_format (take the input one as default)
        if output_format is None:
            outFormat=driver_type
        else:
            outFormat=output_format

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
            F_ratio=N.zeros(XSize).astype(float)
            Pb_opt=N.zeros(XSize).astype(float)

            data_pp=N.zeros(XSize).astype(float) + output_nodata

            data_chl = N.ravel(chla_fileID.ReadAsArray(0, il, XSize, 1))
            data_sst = N.ravel(sst_fileID.ReadAsArray(0, il, XSize, 1))
            data_par   = N.ravel(par_fileID.ReadAsArray(0, il, XSize, 1))
            data_kd   = N.ravel(kd_fileID.ReadAsArray(0, il, XSize, 1))
            data_sst = data_sst*0.01


            valid = (data_chl !=  chla_nodata) * (data_sst != sst_nodata) * (data_par != par_nodata) *(data_kd != kd_nodata)

            if valid.any():

                # calculating f ratio  F using (0.66125 * Eo)/(Eo + 4.1)
                F_ratio[valid] = (0.66125*data_par[valid])/(data_par[valid] + 4.1)

                # Calculate Pb_opt from SST
                Pb_opt[valid] = -3.27e-8*data_sst[valid]**7 + 3.4132e-6*data_sst[valid]**6 - 1.348e-4*data_sst[valid]**5 + \
                          2.462e-3*data_sst[valid]**4 - 0.0205*data_sst[valid]**3 + 0.0617*data_sst[valid]**2 + \
                          0.2749*data_sst[valid] + 1.2956

                data_pp[valid] = data_chl[valid]*(4.6/data_kd[valid])*F_ratio[valid]*Pb_opt[valid]*dl

            data_pp.shape = (1,-1)


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

def DetectEdgesInSingleImage(image, histogramWindowStride, \
                             minTheta, histogramWindowSize, minPopProp, minPopMeanDifference, minSinglePopCohesion, minImageValue, \
                             wrapEdges=False, maxImageValue=None, masks=None, maskTests=None, maskValues=None, medianFilterWindowSize=3,\
                             minPropNonMaskedCells=0.65, minGlobalPopCohesion=0.92, threads=1): \

    # Check and assign parameters

    if histogramWindowSize is None:
        histogramWindowSize=16

    if histogramWindowStride is None:
        histogramWindowStride=8

    if minTheta is None:
        minTheta=0.76

    if minPopProp is None:
        minPopProp=0.25

    if minPopMeanDifference is None:
        minPopMeanDifference=0.25

    if minSinglePopCohesion is None:
        minSinglePopCohesion=0.90

    if minImageValue is None:
        minImageValue=2

    if masks is not None:
        if maskTests is None:
            print 'If you provide a list of masks, you must also provide a parallel list of mask tests.'
        if maskValues is None:
            print 'If you provide a list of masks, you must also provide a parallel list of mask values.'

    if medianFilterWindowSize is not None and medianFilterWindowSize % 2 == 0:
        print 'The median filter window size must be a positive odd integer greater than or equal to 3.'

    if histogramWindowStride > histogramWindowSize:
        print 'The histogram stride cannot be larger than the histogram window size.'

    # Import needed modules.

    import numpy
    from lib.compiled import FrontsUtils

    # The edge detection algorithm uses moving windows. To
    # simplify implementation of that code, create a copy of the
    # caller's image with a buffer around each edge. Also allocate
    # a buffered mask in which True indicates that the
    # corresponding cell of the caller's image is invalid.

    if medianFilterWindowSize is None:
        bufferSize = (histogramWindowSize + 1) / 2
    else:
        bufferSize = max([(medianFilterWindowSize + 1) / 2, (histogramWindowSize + 1) / 2])
    rows = bufferSize + image.shape[0] + bufferSize
    cols = bufferSize + image.shape[1] + bufferSize

    bufferedImage = numpy.zeros((rows, cols), dtype=image.dtype)
    bufferedImage[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]] = image

    bufferedMask = numpy.array([True] * rows * cols).reshape((rows, cols))
    unbufferedMask = bufferedMask[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
# unbufferedMask is a reference to cells of bufferedMask, not a deep copy
    unbufferedMask[:] = False

    # Apply the caller's masks.

    if minImageValue is not None:
        print ' Debug: minImageValue not defined.'
        unbufferedMask[:] = numpy.logical_or(unbufferedMask, image < minImageValue)

    if maxImageValue is not None:
        print ' Debug: maxImageValue not defined.'
        unbufferedMask[:] = numpy.logical_or(unbufferedMask, image > maxImageValue)

    if masks is not None:
        for i in range(len(masks)):
            if maskTests[i] == u'equal':
                print ' Debug: Masking cells where mask %(mask)i is equal to ',i,'.'
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] == maskValues[i])

            elif maskTests[i] == u'notequal':
                print ' Debug: Masking cells where mask %(mask)i is not equal to ',i,'.'
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] != maskValues[i])

            elif maskTests[i] == u'greaterthan':
                print ' Debug: Masking cells where mask %(mask)i is greater than ',i,'.'
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] > maskValues[i])

            elif maskTests[i] == u'lessthan':
                print ' Debug: Masking cells where mask %(mask)i is less than ',i,'.'
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] < maskValues[i])

            elif maskTests[i] == u'anybitstrue':
                print ' Debug: Masking cells where mask ',i,'(mask) bitwise-ANDed with ',X,' is not zero.'
                unbufferedMask[:] = numpy.logical_or(unbufferedMask, numpy.bitwise_and(masks[i], maskValues[i]) != 0)

            else:
                print ' is not an allowed mask test.'

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
        bufferedImage[bufferSize:bufferSize+image.shape[0], 0:bufferSize] = bufferedImage[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize]
        bufferedImage[bufferSize:bufferSize+image.shape[0], -bufferSize:] = bufferedImage[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2]
        bufferedMask[bufferSize:bufferSize+image.shape[0], 0:bufferSize] = bufferedMask[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize]
        bufferedMask[bufferSize:bufferSize+image.shape[0], -bufferSize:] = bufferedMask[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2]

    # Apply the median filters.

    if medianFilterWindowSize is not None:
        #print ' Debug: Applying ',ix,i,' median filter.'
        bufferedImage = FrontsUtils.MedianFilter(bufferedImage, bufferedMask, bufferSize, medianFilterWindowSize)

        # If the caller specified that the edges should wrap, copy
        # image values to the buffer strips again, because the image
        # values probably changed as a result of running the median
        # filter.

        bufferedImage[bufferSize:bufferSize+image.shape[0], 0:bufferSize] = bufferedImage[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize]
        bufferedImage[bufferSize:bufferSize+image.shape[0], -bufferSize:] = bufferedImage[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2]

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

    print ' Debug: Running histogramming and cohesion algorithm.'
    timeStarted = time.time()

    # If we're only using one thread, invoke the C code directly.

    if threads <= 1 or threads > image.shape[0]:
        FrontsUtils.CayulaCornillonFronts(bufferedImage, bufferedMask, bufferedCandidateCounts, bufferedFrontCounts, bufferedWindowStatusCodes, bufferedWindowStatusValues, bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion)

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

        blockHeight = image.shape[0] / threads
        blockHeight = blockHeight - blockHeight % histogramWindowStride

        bufferedImageList = []
        bufferedMaskList = []

        for i in range(threads - 1):
            bufferedImageList.append(bufferedImage[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :])
            bufferedMaskList.append(bufferedMask[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :])

        bufferedImageList.append(bufferedImage[(i+1) * blockHeight : , :])
        bufferedMaskList.append(bufferedMask[(i+1) * blockHeight : , :])

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
            bufferedWindowStatusCodesList.append(numpy.zeros(bufferedImageList[i].shape, bufferedWindowStatusCodes.dtype))
            bufferedWindowStatusValuesList.append(numpy.zeros(bufferedImageList[i].shape, bufferedWindowStatusValues.dtype))

        # Import the threading module.

        try:
            import threading as _threading
        except ImportError:
            import dummy_threading as _threading

        # Create and start the threads.

        threadList = []
        for i in range(threads):
            t = _threading.Thread(name='%i' % i, target=FrontsUtils.CayulaCornillonFronts, args=(bufferedImageList[i], bufferedMaskList[i], bufferedCandidateCountsList[i], bufferedFrontCountsList[i], bufferedWindowStatusCodesList[i], bufferedWindowStatusValuesList[i], bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion))
            t.setDaemon(True)
            print ' Debug: Starting thread %(id)s to process rows %(start)i to %(end)i.'
            threadList.append(t)

        for i in range(threads):
            threadList[i].start()

        # Wait for all of the threads to exit.

        while len(threadList) > 0:
            threadList[0].join()
            print ' Debug: Thread %(id)s exited.'
            del threadList[0]

        # Aggregate the arrays computed by the threads into the
        # array we will return to the caller.

        for i in range(threads - 1):
            bufferedCandidateCounts[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :] += bufferedCandidateCountsList[i][:,:]
            bufferedFrontCounts[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :] += bufferedFrontCountsList[i][:,:]
            bufferedWindowStatusCodes[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :] += bufferedWindowStatusCodesList[i][:,:]
            bufferedWindowStatusValues[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :] += bufferedWindowStatusValuesList[i][:,:]

        bufferedCandidateCounts[(i+1) * blockHeight : , :] += bufferedCandidateCountsList[i+1][:,:]
        bufferedFrontCounts[(i+1) * blockHeight : , :] += bufferedFrontCountsList[i+1][:,:]
        bufferedWindowStatusCodes[(i+1) * blockHeight : , :] += bufferedWindowStatusCodesList[i+1][:,:]
        bufferedWindowStatusValues[(i+1) * blockHeight : , :] += bufferedWindowStatusValuesList[i+1][:,:]

    timeEnded = time.time()
    print ("Debug: Histogram and cohesion algorithm complete. Elapsed time is: %f seconds" % (timeEnded-timeStarted))

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
        bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize] += bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], 0:bufferSize]
        bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2] += bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], -bufferSize:]
        bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize] += bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], 0:bufferSize]
        bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2] += bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], -bufferSize:]

        timeEnded = time.time()
        print ("Debug: Wrap Edges done. Elapsed time is: %f seconds" % (timeEnded-timeStarted))
    else:
        print ("Debug: No wrap edged.")

    # Return successfully.

    unbufferedImage = bufferedImage[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
    unbufferedCandidateCounts = bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
    unbufferedFrontCounts = bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
    unbufferedWindowStatusCodes = bufferedWindowStatusCodes[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
    unbufferedWindowStatusValues = bufferedWindowStatusValues[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]

    timeEnded = time.time()
    print ("Debug: Return. Elapsed time is: %f seconds" % (timeEnded-timeStarted))
    return copy.deepcopy(unbufferedMask), copy.deepcopy(unbufferedImage), copy.deepcopy(unbufferedCandidateCounts), copy.deepcopy(unbufferedFrontCounts), copy.deepcopy(unbufferedWindowStatusCodes), copy.deepcopy(unbufferedWindowStatusValues)

# _____________________________
def do_detect_sst_fronts(input_file='', output_file='', input_nodata=None, parameters=None,
                          output_nodata=None, output_format=None, output_type=None, options=''):


    # Parameters is expected to be None, or a dictionary
    if parameters is not None:

        if 'histogramWindowStride' in parameters.keys():
            histogramWindowStride = parameters['histogramWindowStride']
        else:
            histogramWindowStride = None

        if 'minTheta' in parameters.keys():
            minTheta = parameters['minTheta']
        else:
            minTheta = None
        if 'minPopProp' in parameters.keys():
            minPopProp = parameters['minPopProp']
        else:
            minPopProp = None
        if 'minPopMeanDifference' in parameters.keys():
            minPopMeanDifference = parameters['minPopMeanDifference']
        else:
            minPopMeanDifference = None
        if 'minSinglePopCohesion' in parameters.keys():
            minSinglePopCohesion = parameters['minSinglePopCohesion']
        else:
            minSinglePopCohesion = None
        if 'histogramWindowSize' in parameters.keys():
            histogramWindowSize = parameters['histogramWindowSize']
        else:
            histogramWindowSize = None
        if 'minImageValue' in parameters.keys():
            minImageValue = parameters['minImageValue']
        else:
            minImageValue = None

        minThreshold = 2
        if 'minThreshold' in parameters.keys():
            if parameters['minThreshold'] is not None:
                minThreshold = parameters['minThreshold']

    rid = ''
    debug = 0

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
    driver_type=inputID.GetDriver().ShortName

    # Manage out_type (take the input one as default)
    if output_type is None:
        outType=dataType
    else:
        outType=ParseType(output_type)

    # Manage out_format (take the input one as default)
    if output_format is None:
        outFormat=driver_type
    else:
        outFormat=output_format

    # Check output directory
    functions.check_output_dir(os.path.dirname(output_file))

    # Instantiate output
    outDrv = gdal.GetDriverByName(outFormat)
    if debug:
        n_bands= 3
    else:
        n_bands= 1
    outDS = outDrv.Create(output_file, ns, nl, n_bands, outType, options_list)
    outDS.SetGeoTransform(geoTransform)
    outDS.SetProjection(projection)

    # Read Input
    inband = inputID.GetRasterBand(1)
    inData = inband.ReadAsArray(0,0,inband.XSize,inband.YSize)
    inDataInt = N.uint16(inData*1000)                               # To Be Verified

    # Call FrontDetection Algorithm
    [uMask, uImage, uCandidateCounts, uFrontCounts,uWindowStatusCodes, uWindowStatusValues] = \
        DetectEdgesInSingleImage(inDataInt,histogramWindowStride,minTheta,histogramWindowSize,minPopProp, minPopMeanDifference,minSinglePopCohesion,minImageValue)

    print ("Debug: Applying now Minimum threshold: %i" % minThreshold)

    # Apply minimum threshold (line by line)
    dataOut = N.empty([nl,ns],dtype=bool)
    for il in range(nl):
        data_in = uFrontCounts[il,:]
        rowOut=N.empty([ns],dtype=bool)*0
        rowOut[data_in >= minThreshold]= 1
        dataOut[il,:] = rowOut[:]

    # Apply thinning
    print ("Debug: Applying now thinning")
    thin_output = pymorph.thin(dataOut)

    # Create and write output band
    print ("Debug: Writing the output files")
    if debug:
        outband = outDS.GetRasterBand(1)
        outband.WriteArray(uFrontCounts,0,0)
        outband = outDS.GetRasterBand(2)
        outband.WriteArray(dataOut,0,0)
        outband = outDS.GetRasterBand(3)
        outband.WriteArray(thin_output,0,0)
    else:
        outband = outDS.GetRasterBand(1)
        outband.WriteArray(thin_output,0,0)

    # #   ----------------------------------------------------------------------------------------------------
    # #   Writes metadata to output
    input_list = []
    input_list.append(input_file)
    #assign_metadata_processing(input_list, output_file)

    # #   Close outputs
    outDrv = None
    outDS = None

# _____________________________
def do_ts_linear_filter(input_file='', before_file='', after_file='', output_file='', input_nodata=None, output_format=None,
           output_type=None, options='', threshold=None):
    #
    # Notes:'The command expects exactly 3 input files, in 3 arguments.'
    #       'The input_nodata defines the output_nodata as well (no recoding)'

    # Manage options
    options_list = [es_constants.ES2_OUTFILE_OPTIONS]
    options_list.append(options)

    # Open the threee files (add checks)
    f0  = gdal.Open(input_file, GA_ReadOnly)
    fm1 = gdal.Open(before_file, GA_ReadOnly)
    fp1  = gdal.Open(after_file, GA_ReadOnly)

    # get infos from the input_file
    nb = f0.RasterCount
    ns = f0.RasterXSize
    nl = f0.RasterYSize
    dataType = f0.GetRasterBand(1).DataType
    geoTransform = f0.GetGeoTransform()
    projection = f0.GetProjection()
    driver_type=f0.GetDriver().ShortName

    # Try and assign input_nodata if it is UNDEF
    if input_nodata is None:
        sds_meta = metadata.SdsMetadata()
        if os.path.exists(input_file):
            input_nodata=float(sds_meta.get_nodata_value(input_file))
        else:
            logger.info('Test file not existing: do not assign metadata')

    # manage out_type (take the input one as default)
    if output_type is None:
        outType=dataType
    else:
        outType=ParseType(output_type)

    # manage out_format (take the input one as default)
    if output_format is None:
        outFormat=driver_type
    else:
        outFormat=output_format

    # instantiate output(s)
    outDrv = gdal.GetDriverByName(outFormat)
    outDS = outDrv.Create(output_file, ns, nl, nb, outType, options_list)
    outDS.SetGeoTransform(geoTransform)
    outDS.SetProjection(projection)

    for ib in range(nb):

        f0band  = f0.GetRasterBand(ib+1)
        fm1band = fm1.GetRasterBand(ib+1)
        fp1band = fp1.GetRasterBand(ib+1)
        outband = outDS.GetRasterBand(ib+1)

        for il in range(f0.RasterYSize):

            data    = N.ravel(f0band.ReadAsArray(0, il, f0band.XSize, 1)).astype(float)
            data_m1 = N.ravel(fm1band.ReadAsArray(0, il, fm1band.XSize, 1)).astype(float)
            data_p1 = N.ravel(fp1band.ReadAsArray(0, il, fp1band.XSize, 1)).astype(float)

            if input_nodata is None:
                wtp = N.ravel((data_m1 != 0) * (data_p1 != 0))
            else:
                wtp = N.ravel((data_m1 != input_nodata) * (data_p1 != input_nodata) * N.ravel((data_m1 != 0) * (data_p1 != 0)))

            correct = data
            if wtp.any():
                slope1      = N.zeros(data.shape)
                slope1[wtp] = (data[wtp] - data_m1[wtp])/abs(data_m1[wtp])
                slope2      = N.zeros(data.shape)
                slope2[wtp] = (data_p1[wtp] - data[wtp])/abs(data_p1[wtp])
                wtc         = ( slope1 < -threshold ) * ( slope2 > threshold )

                if wtc.any():
                    correct[wtc] = 0.5*( data_m1[wtc] + data_p1[wtc] )

            correct.shape = (1, len(correct))
            outband.WriteArray(N.array(correct),0,il)

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

# _____________________________
#   Write to an output file the metadata
#

def assign_metadata_processing(input_file_list, output_file):

    # Create Metadata object
    sds_meta = metadata.SdsMetadata()

    # Check if the input file is single, or a list
    if isinstance(input_file_list, list) or isinstance(input_file_list, tuple):
        first_input = input_file_list[0]
    else:
        first_input = input_file_list

    # Open and read data
    sds_meta.read_from_file(first_input)

    # Modify/Assign some to the ingested file
    sds_meta.assign_comput_time_now()
    str_date, productcode, subproductcode, mapset, version = functions.get_all_from_filename(os.path.basename(output_file))
    # [productcode, subproductcode, version, str_date, mapset] = functions.get_all_from_path_full(output_file)

    #   TODO-M.C.: cannot read metadata from database for a newly created product ! Copy from input file ?
    #
    sds_meta.assign_from_product(productcode, subproductcode, version)
    #sds_meta.assign_product_elemets(productcode, subproductcode, version)

    sds_meta.assign_date(str_date)
    sds_meta.assign_input_files(input_file_list)

    # Define subdirectory
    sub_directory = functions.set_path_sub_directory(productcode,subproductcode,'Derived',version,mapset)
    sds_meta.assign_subdir(sub_directory)

    # Write Metadata
    sds_meta.write_to_file(output_file)
