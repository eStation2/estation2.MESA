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
#                               Nevertheless if input_nodata id <def> and output_nodata is <undef> the latter is assigned
#                               to the value of inputs.
#
#                               In functions like <min>, <max> in the loop over files we update an output if we find
#                               a <valid> data to replace a <nodata>
#

# source eStation2 base definitions
import locals

# import standard modules

# Import eStation lib modules
from lib.python import es_logging as log
from lib.python.metadata import *
from lib.python.functions import *

# Import third-party modules
from osgeo.gdalconst import *
from osgeo import gdal
import numpy as N

logger = log.my_logger(__name__)

# _____________________________
def do_avg_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', output_stddev=None, ):

    # Note: no 'update' functionality is foreseen -> creates output EVERY TIME

    # Force input to be a list
    input_list = return_as_list(input_file)

    # Manage options
    options_list = []
    options_list.append(options)

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

# _____________________________
def do_min_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', index_file=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    #       'The optional index file will store the file index (position in input-list) used for the minimum.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??

    # Force input to be a list
    input_list = return_as_list(input_file)

    # Manage options
    options_list = []
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

# _____________________________
def do_max_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', index_file=None, min_num_valid=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    #       'The optional index file will store the file index (position in input-list) used for the minimum.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??

    # Force input to be a list
    input_list = return_as_list(input_file)

    # Manage options
    options_list = []
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

#   _____________________________
def do_med_image(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', min_num_valid=None):
    #
    # Notes:'The command expects a list of at least 2 files in input.'
    # TODO-M.C.: : can be used in 'update' functionality ??? -> reuse output file ??
    # TODO-M.C.: : NODATA now are considered as 'normal' values ... should be removed !

    # Force input to be a list
    input_list = return_as_list(input_file)

    # Manage options
    options_list = []
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

# _____________________________
def do_oper_subtraction(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):
    #
    # Notes:'The command expects exactly 2 files in input.'

    # Manage options
    options_list = []
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

# _____________________________
def do_oper_division(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):
    #
    # Notes:'The command expects exactly 2 files in input.'
    epsilon = 1e-10

    # Manage options
    options_list = []
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
            dataout=N.zeros(ns)
            if input_nodata is None:
                dataout=N.zeros(ns) + output_nodata

            if wtc.any():
                dataout[wtc] = data0[wtc] / data1[wtc]

            dataout.shape=(1,-1)
            outDS.GetRasterBand(ib+1).WriteArray(N.array(dataout), 0, il)

    #   ----------------------------------------------------------------------------------------------------
    #   Close outputs
    outDrv = None
    outDS = None
    #   Writes metadata to output
    assign_metadata_processing(input_file, output_file)

# _____________________________
def do_oper_scalar_multiplication(input_file='', output_file='', scalar=1, input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):
    #
    # Notes:'The command expects exactly 1 file in input.'

    # Manage options
    options_list = []
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

# _____________________________
def do_make_vci(input_file='', min_file='', max_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):

    # Manage options
    options_list = []
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

    # Manage options
    options_list = []
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

# _____________________________
def do_mask_image(input_file='', mask_file='', output_file='',output_format=None,
           output_type=None, options='', mask_value=1, out_value=0):

# _____________________________
#
#   Copy input to output, by setting to out_value all pixel where mask=mask_value
#


    # Manage options
    options_list = []
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
    assign_metadata_processing(input_list, output_file)


# _____________________________
def do_cumulate(input_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options='', output_stddev=None, scale_factor=None):

    # Notes:'The command expects exactly 1 file in input.'

    # Manage options
    options_list = []
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
    outDS=outDrv.Create(output_file, ns, nl, nb, ParseType(outType), options_list)
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

# _____________________________
def do_compute_perc_diff_vs_avg(input_file='', avg_file='', output_file='', input_nodata=None, output_nodata=None, output_format=None,
           output_type=None, options=''):

    # TODO-M.C.: check (and make uniform across functions()) data type
    epsilon = 1e-10

    # Manage options
    options_list = []
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

# _____________________________
def do_ts_linear_filter(input_file='', before_file='', after_file='', output_file='', input_nodata=None, output_format=None,
           output_type=None, options='', threshold=None):
    #
    # Notes:'The command expects exactly 3 input files, in 3 arguments.'
    #       'The input_nodata defines the output_nodata as well (no recoding)'

    # Manage options
    options_list = []
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
                wtp = N.ravel((data_m1 != input_nodata) * (data_p1 != input_nodata))

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
    sds_meta = SdsMetadata()

    # Check if the input file is single, or a list
    if isinstance(input_file_list, list) or isinstance(input_file_list, tuple):
        first_input = input_file_list[0]
    else:
        first_input = input_file_list

    # Open and read data
    sds_meta.read_from_file(first_input)

    # Modify/Assign some to the ingested file
    sds_meta.assign_comput_time_now()

    [productcode, subproductcode, version, str_date, mapset] = get_all_from_path_full(output_file)
    sds_meta.assign_from_product(productcode,subproductcode,version)

    sds_meta.assign_date(str_date)
    sds_meta.assign_input_files(input_file_list)
    sds_meta.assign_subdir_from_fullpath(output_file)

    # Write Metadata
    sds_meta.write_to_file(output_file)
