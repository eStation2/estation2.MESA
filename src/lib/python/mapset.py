#
#	purpose: Define the mapset class
#	author:  M. Clerici
#	date:	 25.02.2014
#   descr:	 Defines members and methods of the mapset class
#
#   TODO-M.C.: Define methods to assess relationships between mapsets (e.g. included)
#
from osgeo import osr, gdal
import os, sys, psycopg2, psycopg2.extras

sys.path.append('/srv/www/eStation2/config/')

import es2

class mapset:

    def __init__(self):
        self.SpatialRef=osr.SpatialReference()
        self.GeoTransform=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.sizeX=0
        self.sizeY=0


    def assignDef(self):
        # Assign the VGT4Africa default mapset (continental)
        self.SpatialRef.ImportFromWkt("WGS84")
        self.GeoTransform=[-26.004464285714285, 0.008928571428571, 0.0, 38.004464285714285, 0.0, -0.008928571428571]
        self.sizeX=9633
        self.sizeY=8177

    def assignECOWAS(self):
        # Assign the VGT4Africa default mapset (continental)
        self.SpatialRef.ImportFromWkt("WGS84")
        self.GeoTransform=[-19.004464285714285, 0.008928571428571, 0.0, 28.004464285714285, 0.0, -0.008928571428571]
        self.sizeX=4929
        self.sizeY=2689

def test():
    file=es2.testDataDirOut+'20121021_NDWI.tif'
    ds=gdal.Open(file)
    old_cs=osr.SpatialReference()
    old_cs.ImportFromWkt(ds.GetProjectionRef())
    print old_cs
    geoTransform=ds.GetGeoTransform()
    print geoTransform
    sizeX = ds.RasterXSize
    sizeY = ds.RasterYSize
    print sizeX, sizeY
    #print ds.GetProjectionRef()
