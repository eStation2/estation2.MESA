#
#	purpose: Define the all functions for processing raster datasets (previously in ~/PS/bin/*py)
#	author:  M. Clerici
#	date:	 11.06.2014
#   descr:	 Define the all functions for processing raster datasets (previously in ~/PS/bin/*py)
#
#   TODO-M.C.: optimize (replace loops)

# Import standard modules
import sys
import os.path
#import cpimgfile ??

# Import eStation lib modules
import database.querydb as querydb

# Import third-party modules
from osgeo.gdalconst import *
from osgeo import gdal
from osgeo import osr
import pygrib
import numpy as N

try:
    from osgeo import gdal
    from osgeo.gdalconst import *
    gdal.TermProgress = gdal.TermProgress_nocb
except ImportError:
    import gdal
    from gdalconst import *
try:
    import numpy as N
    N.arrayrange = N.arange
except ImportError:
    import Numeric as N

try:
    from osgeo import gdal_array as gdalnumeric
except ImportError:
    import gdalnumeric
    
import sys
import os.path
import operator
import math

# _____________________________
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
	return GDT_Float32
# ______________________________
def Usage(message):
    print message

    sys.exit(1)

# ______________________________
def do_recode(file, outfile, value_s, value_t, outTypeIn, format, options):
    fid0 = gdal.Open(file, GA_ReadOnly)
    ns = fid0.RasterXSize
    nl = fid0.RasterYSize
    nb = fid0.RasterCount

    if outTypeIn is None:
        outType = fid0.GetRasterBand(1).DataType
    else:
        outType = ParseType(outTypeIn)
    
    outDrv = gdal.GetDriverByName(format)
    outDs = outDrv.Create(outfile, ns, nl, nb, outType, options)
    outDs.SetProjection(fid0.GetProjection())
    outDs.SetGeoTransform(fid0.GetGeoTransform())

    for ib in range(nb):
        for il in range(nl):
            data0=N.ravel(fid0.GetRasterBand(ib+1).ReadAsArray(0,il,ns,1))

            # set to N.zeros to enable auto cast whenever needed
            dataout=N.zeros(ns) + data0
            for it in range(len(value_s)):
                wtp = (data0 == value_s[it])
                if wtp.any():
                    dataout[wtp]=value_t[it]
            

            dataout.shape=(1,-1)
            outDs.GetRasterBand(ib+1).WriteArray(N.array(dataout),0,il)
            gdal.TermProgress( (ib*(ns*nl)+il*ns)/float(ns*nl*nb) )
            
    gdal.TermProgress(1)

# ______________________________
#
#   Quick wrapper for calling from ruffus
#
def myrecode(file, outfile, value_s, value_t):

    format = 'Gtiff'
    options= []

    fid0 = gdal.Open(file, GA_ReadOnly)
    ns = fid0.RasterXSize
    nl = fid0.RasterYSize
    nb = fid0.RasterCount

    outType = fid0.GetRasterBand(1).DataType

    outDrv = gdal.GetDriverByName(format)
    outDs = outDrv.Create(outfile, ns, nl, nb, outType, options)
    outDs.SetProjection(fid0.GetProjection())
    outDs.SetGeoTransform(fid0.GetGeoTransform())

    for ib in range(nb):
        for il in range(nl):
            data0=N.ravel(fid0.GetRasterBand(ib+1).ReadAsArray(0,il,ns,1))

            # set to N.zeros to enable auto cast whenever needed
            dataout=N.zeros(ns) + data0
            for it in range(len(value_s)):
                wtp = (data0 == value_s[it])
                if wtp.any():
                    dataout[wtp]=value_t[it]


            dataout.shape=(1,-1)
            outDs.GetRasterBand(ib+1).WriteArray(N.array(dataout),0,il)
            gdal.TermProgress( (ib*(ns*nl)+il*ns)/float(ns*nl*nb) )

    gdal.TermProgress(1)

# ______________________________
if __name__=="__main__":
    
    outfile = None
    format = 'Gtiff'
    options= []
    file = None
    value_s=[]
    value_t=[]
    outType = None

    ii = 1
    while ii < len(sys.argv):
        arg = sys.argv[ii]

        if arg == '-of':
            ii = ii + 1
            format = sys.argv[ii]

        elif arg == '-co':
            ii = ii + 1
            options.append(sys.argv[ii])
        elif arg == '-outType':
            ii = ii + 1
            outType = sys.argv[ii]

        elif arg == '-r':
            ii = ii + 1
            value_s.append(float( sys.argv[ii]))
            ii = ii + 1
            value_t.append( float(sys.argv[ii]))
            
        elif arg == '-o':
            ii = ii + 1
            outfile = sys.argv[ii]

        else :
            file=arg

        ii = ii + 1

    #check inputs
    if file is None:
        Usage('Missing an input file name.')

    if outfile is None:
        Usage('Missing an output file name.')

    if len(value_s)==0:
        Usage('You must define source/target values.')

    if len(value_s)!=len(value_t):
        Usage('For each source value you must define a target value.')

    if (os.path.isfile(file)):
        pass
    else:
        Usage('Input file does not exist: '+file)
        

    do_recode(file, outfile, value_s, value_t, outType, format, options)
