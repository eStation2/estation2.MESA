#
#	purpose: Define the mapset class
#	author:  M. Clerici
#	date:	 25.02.2014
#   descr:	 Defines members and methods of the mapset class
#
#   TODO-M.C.: Define methods to assess relationships between mapsets (e.g. included)
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
from builtins import int
from builtins import object
from builtins import range
from builtins import str
from past.utils import old_div

# Import std modules
import numpy as N
import math
import os

# Import third-party modules
from osgeo import gdal
from osgeo import osr, ogr
# from osgeo import gdalconst
# import pygrib

# Import eStation lib modules
from database import querydb

standard_library.install_aliases()


class MapSet(object):

    def __init__(self):
        self.spatial_ref = osr.SpatialReference()
        self.spatial_ref_wkt = None
        self.geo_transform = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.size_x = 0
        self.size_y = 0
        self.short_name = ''
        self.pixel_area = None

    def assigndb(self, mapsetcode):
        mapset = querydb.get_mapset(mapsetcode)
        self.spatial_ref_wkt = mapset.srs_wkt
        geo_transform = [float(mapset.upper_left_long),
                         float(mapset.pixel_shift_long),
                         float(mapset.rotation_factor_long),
                         float(mapset.upper_left_lat),
                         float(mapset.rotation_factor_lat),
                         float(mapset.pixel_shift_lat)]

        self.spatial_ref.ImportFromWkt(self.spatial_ref_wkt)
        self.geo_transform = geo_transform
        self.size_x = int(mapset.pixel_size_x)
        self.size_y = int(mapset.pixel_size_y)
        self.short_name = mapset.mapsetcode

    def assign(self, spatial_ref_wkt, geo_transform, size_x, size_y, short_name):
        # Assign to passed arguments
        self.spatial_ref_wkt = spatial_ref_wkt
        self.spatial_ref.ImportFromWkt(spatial_ref_wkt)
        self.geo_transform = geo_transform
        self.size_x = size_x
        self.size_y = size_y
        self.short_name = short_name

    def assign_default(self):
        # Assign the VGT4Africa default mapset (continental)
        self.spatial_ref.ImportFromWkt("WGS84")
        self.geo_transform = [-26.004464285714285, 0.008928571428571, 0.0, 38.004464285714285, 0.0, -0.008928571428571]
        self.size_x = 9633
        self.size_y = 8177

    def print_out(self):
        # Print Information on the mapset
        print('Spatial Ref WKT: ' + self.spatial_ref.ExportToWkt())
        print(('GeoTransform   : ', self.geo_transform))
        print(('SizeX          : ', self.size_x))
        print(('SizeY          : ', self.size_y))
        print(('Shortname      : ', self.short_name))

    def validate(self, echo=False):

        # Initialize as OK
        result = 0

        # Validate the Spatial Reference
        if echo:
            print('Spatial Ref Validate [0=ok]: ' + str(self.spatial_ref.Validate()))
        result += self.spatial_ref.Validate()

        # Checks on the GeoTransform array
        # code_gt = 1 -> wrong number of elements
        # code_gt = 2 -> wrong type of elements
        code_gt = 0
        if len(self.geo_transform) != 6:
            code_gt = 1
        for igt in self.geo_transform:
            if not isinstance(igt, float):
                code_gt = 2
        if echo:
            print('Geo Transfo Validate [0=ok]: ' + str(code_gt))
        result += code_gt

        code_size_x = isinstance(self.size_x, int) and self.size_x > 0
        if echo:
            print('Size X positive number     : ' + str(code_size_x))
        if not code_size_x:
            result += 1

        code_size_y = isinstance(self.size_y, int) and self.size_y > 0
        if echo:
            print('Size Y positive number     : ' + str(code_size_y))
        if not code_size_y:
            result += 1

        return result

    def get_larger_mapset(self, echo=False):

        larger_mapset = None

        # SPOTV case

        if self.short_name == 'SPOTV-CEMAC-1km':
            larger_mapset = 'SPOTV-Africa-1km'

        if self.short_name == 'SPOTV-ECOWAS-1km':
            larger_mapset = 'SPOTV-Africa-1km'

        if self.short_name == 'SPOTV-IGAD-1km':
            larger_mapset = 'SPOTV-Africa-1km'

        if self.short_name == 'SPOTV-SADC-1km':
            larger_mapset = 'SPOTV-Africa-1km'

        # These two mapsets apply to PML only, and they should considered 'independent' from the Africa 'one',
        # as the 'larger' is not created See also byg in ftp_data_push ES2-209 - 15.2.2018

        # if self.short_name == 'SPOTV-UoG-1km':
        #     larger_mapset =  'SPOTV-Africa-1km'
        # if self.short_name == 'SPOTV-IOC-1km':
        #     larger_mapset =  'SPOTV-Africa-1km'

        # MODIS Africa case
        if self.short_name == 'MODIS-IOC-4km':
            larger_mapset = 'MODIS-Africa-4km'

        if self.short_name == 'MODIS-UoG-4km':
            larger_mapset = 'MODIS-Africa-4km'

        return larger_mapset

    def compute_common_area(self, second_mapset):
        #   Computes the common area of two mapset, ONLY if they have same resolution
        #   It returns shift to apply to each image and the common roi dimensions
        #   Arguments:
        #
        #       second_mapset: mapset to compare with
        #

        roi = {'isCommon': None,  # two ROIs have same pixelsize AND area in common
               'xSize': 0,  # x-dim of common area
               'ySize': 0,  # y-dim of common area
               'firstXOff': 0,  # x-offset of the common area in ROI-1
               'firstYOff': 0,  # y-offset of the common area in ROI-1
               'secondXOff': 0,  # x-offset of the common area in ROI-2
               'secondYOff': 0,  # y-offset of the common area in ROI-2
               }

        # Accuracy in degrees (0.1 km)
        accuracy = (1.0 / 112.0) / 10.0

        # Assign Geo-transform and image-sizes from mapsets
        firstGeo = self.geo_transform
        firstNs = self.size_x
        firstNl = self.size_y
        secondGeo = second_mapset.geo_transform
        secondNs = second_mapset.size_x
        secondNl = second_mapset.size_y

        flag = 1
        for ii in range(len(firstGeo)):
            if firstGeo[ii] != secondGeo[ii]:
                flag = 0

        if flag == 1:
            # ROIs are identical: return trivial parameters
            roi['isCommon'] = True
            roi['xSize'] = firstNs
            roi['ySize'] = firstNl
        else:
            # they are not the same, compute offset
            # they must have same pixel size, otherwise return 'No common ROIs'
            if math.fabs(firstGeo[1] - secondGeo[1]) > accuracy or math.fabs(firstGeo[5] - secondGeo[5]) > accuracy:
                roi['isCommon'] = False
            else:
                xshift = int(old_div((secondGeo[0] - firstGeo[0]), math.fabs(firstGeo[1])))
                if xshift > 0:
                    firstXOff = xshift
                    secondXOff = int(0)
                    xSize = min(int(firstNs - xshift), secondNs)
                else:
                    firstXOff = 0
                    secondXOff = int(abs(xshift))
                    xSize = min((secondNs - abs(xshift)), firstNs)

                yshift = int(old_div((firstGeo[3] - secondGeo[3]), math.fabs(firstGeo[5])))
                if yshift > 0:
                    firstYOff = yshift
                    secondYOff = int(0)
                    ySize = min(int(firstNl - yshift), secondNl)
                else:
                    firstYOff = 0
                    secondYOff = int(abs(yshift))
                    ySize = min(int(secondNl - abs(yshift)), firstNl)

                # once every thing is defined, set isCommon to True
                isCommon = True

            roi['isCommon'] = isCommon
            roi['xSize'] = xSize
            roi['ySize'] = ySize
            roi['firstXOff'] = firstXOff
            roi['firstYOff'] = firstYOff
            roi['secondXOff'] = secondXOff
            roi['secondYOff'] = secondYOff

        return roi

    def is_wbd(self):

        if self.short_name[:6] == 'WD-GEE':
            return True
        else:
            return False

    def compute_pixel_area(self, n_line, n_col):

        #  Compute the size (m^2) for a pixel (line,col) in the mapset

        # Read from the original mapset
        orig_geotranform = self.geo_transform
        x0 = orig_geotranform[0]
        deltax = orig_geotranform[1]
        y0 = orig_geotranform[3]
        deltay = orig_geotranform[5]
        srsOrig = self.spatial_ref

        # Define the SRS for Sinusoidal projection
        srsEqualArea = osr.SpatialReference()
        proj4def = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +DATUM=WGS84"
        srsEqualArea.ImportFromProj4(proj4def)

        transf = osr.CoordinateTransformation(srsOrig, srsEqualArea)

        print(" Mapset Name: " + self.short_name)
        print(" Pixel position: x " + str(n_col) + " y " + str(n_line))
        px = x0 + deltax * n_col
        py = y0 + deltay * n_line
        print(" Pixel position Lon: " + str(px) + " Lat " + str(py))

        # The pixel geometry must be created to execute the within method, and to calculate the actual area
        wkt = "POLYGON((" + str(px) + " " + str(py) + "," + str(px + deltax) + " " + str(py) + "," + str(
            px + deltax) + " " + str(py + deltay) + "," + str(px) + " " + str(py + deltay) + "," + str(px) + " " + str(
            py) + "))"

        geometry = ogr.CreateGeometryFromWkt(wkt)
        pixel_area = geometry.GetArea()
        print(" Pixel area (Deg^2): " + str(pixel_area))

        geometryArea = geometry.Clone()
        geometryArea.Transform(transf)
        pixel_area = geometryArea.GetArea()
        print(" Pixel area (m^2): " + str(pixel_area))
        self.pixel_area = pixel_area

    def create_raster_surface(self, filename=None):     # Method is not used anywhere in the code!
        #  Create a file containing the pixel-size (m2) of each pixel of the mapset
        #  Methodology from http://geoexamples.blogspot.it/2012/06/density-maps-using-gdalogr-python.html

        if filename is None:
            mydir = '/data/static/'
            filename = mydir + os.path.sep + self.short_name + '_' + 'pixelsize.tif'

        # Read from the original mapset
        orig_geotranform = self.geo_transform
        x0 = orig_geotranform[0]
        deltax = orig_geotranform[1]
        y0 = orig_geotranform[3]
        deltay = orig_geotranform[5]
        srsOrig = self.spatial_ref
        size_x = self.size_x
        size_y = self.size_y

        # Create output matrix

        areas = N.zeros((size_y, size_x), dtype=N.float32)

        # Define the SRS for Sinusoidal projection
        srsEqualArea = osr.SpatialReference()
        proj4def = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +DATUM=WGS84"
        srsEqualArea.ImportFromProj4(proj4def)
        transf = osr.CoordinateTransformation(srsOrig, srsEqualArea)

        for iline in range(size_y):
            print(iline)
            for icol in range(size_x):
                px = x0 + deltax * icol
                py = y0 + deltay * iline

                # Define the pixel geometry
                wkt = "POLYGON((" + str(px) + " " + str(py) + "," + str(px + deltax) + " " + str(py) + "," + str(
                    px + deltax) + " " + str(py + deltay) + "," + str(px) + " " + str(py + deltay) + "," + str(
                    px) + " " + str(py) + "))"

                geometry = ogr.CreateGeometryFromWkt(wkt)

                geometryArea = geometry.Clone()
                geometryArea.Transform(transf)
                areas[iline, icol] = geometryArea.GetArea()
                geometryArea = None

        # Write matrix to output

        output_driver = gdal.GetDriverByName('GTiff')
        output_ds = output_driver.Create(filename, size_x, size_y, 1, gdal.GDT_Float32)
        output_ds.SetProjection(self.spatial_ref.ExportToWkt())
        output_ds.SetGeoTransform(orig_geotranform)
        output_ds.GetRasterBand(1).WriteArray(areas)
        output_ds = None

    # def assign_ecowas(self):
    #     # Assign the VGT4Africa default mapset for ECOWAS region
    #     self.spatial_ref.SetWellKnownGeogCS("WGS84")
    #     self.geo_transform = [-19.004464285714285, 0.008928571428571, 0.0, 28.004464285714285, 0.0, -0.008928571428571]
    #     self.size_x = 4929
    #     self.size_y = 2689
    #     self.short_name = 'WGS84_ECOWAS_1km'
    #
    # def assign_ioc_pml(self):
    #     # Assign the VGT4Africa default mapset for ECOWAS region
    #     self.spatial_ref.SetWellKnownGeogCS("WGS84")
    #     self.geo_transform = [31.9955357, 0.008993207901969, 0.0, 5.004464285714285, 0.0, -0.008993207029328]
    #     self.size_x = 4278
    #     self.size_y = 3670
    #     self.short_name = 'WGS84_ECOWAS_1km'
    #
    # def assign_vgt4africa(self):
    #     # Assign the VGT4Africa default mapset (continental)
    #     self.spatial_ref.SetWellKnownGeogCS("WGS84")
    #     self.geo_transform = [-26.004464285714285, 0.008928571428571, 0.0, 38.004464285714285, 0.0, -0.008928571428571]
    #     self.size_x = 9633
    #     self.size_y = 8177
    #     self.short_name = 'WGS84_Africa_1km'
    #
    # def assign_vgt4africa_500m(self):
    #     # Assign the VGT4Africa default mapset (continental)
    #     self.spatial_ref.SetWellKnownGeogCS("WGS84")
    #     self.geo_transform = [-26.004464285714285, 0.0044642857142855, 0.0, 38.004464285714285, 0.0,
    #                           -0.0044642857142855]
    #     self.size_x = 19266  # 9633*2
    #     self.size_y = 16354  # 8177*2
    #     self.short_name = 'WGS84_Africa_500m'
    #
    # def assign_msg_disk(self):
    #     # Assign the msg geostationary proj (see http://osdir.com/ml/gdal-development-gis-osgeo/2010-03/msg00029.html)
    #     # Note 1: gdalinfo will raise errors: 'ERROR 1: tolerance condition error' for the 4 corners, as the are out
    #     # of the globe surface -> no problem (see: https://trac.osgeo.org/gdal/ticket/4381)
    #     # Note 2: if we read SpatRef from grib file, does not Validate
    #     proj4def = "+proj=geos +lon_0=0 +h=35785831 +DATUM=WGS84"
    #     self.spatial_ref.ImportFromProj4(proj4def)
    #     # Set additional inf
    #     # self.spatial_ref.SetAttrValue('PROJCS|GEOCS|DATUM',"WGS84")
    #
    #     self.geo_transform = [-5570248.477582973, 3000.4031659482757, 0.0, 5570248.477582973, 0.0, -3000.4031659482757]
    #     self.size_x = 3712
    #     self.size_y = 3712
    #     self.short_name = 'MSG_satellite_3km'
    #
    # def assign_fewsnet_africa(self):
    #     # Assign the Alberts Equal Area Conic proj(see http://earlywarning.usgs.gov/fews/africa/web/readme.php?symbol=rf)
    #     # Geo-transform is read from the input file (.blw)
    #     self.geo_transform = [-4241357.154883339, 8000.0, 0.0, 4276328.591286063, 0.0, -8000.0]
    #     # as in the old ingest_rfe.sh
    #     proj4def = "+proj=aea +lat_1=-19 +lat_2=21 +lat_0=1 +lon_0=20 +x_0=0 +y_0=0"
    #     self.spatial_ref.ImportFromProj4(proj4def)
    #     # Set additional info, as from FEWSNET website
    #     self.spatial_ref.SetAttrValue('PROJCS', "Albers_Conical_Equal_Area")
    #     # self.spatial_ref.SetAttrValue('PROJCS|GEOCS|DATUM|SPHEROID', "Clarke 1866")
    #
    #     self.size_x = 994
    #     self.size_y = 1089
    #     self.short_name = 'AEA_Africa_8km'
    #
    # def assign_tamsat_africa(self):
    #     # Assign the native TAMSAT Africa Mapset
    #     self.spatial_ref.SetWellKnownGeogCS("WGS84")
    #     # Geo-transform is from old ingest_tamsat.sh
    #     self.geo_transform = [-19.0312, 0.0375, 0.0, 38.0437, 0.0, -0.0375]
    #     # as in the old ingest_rfe.sh
    #     # Set additional info, as from FEWSNET website
    #     self.size_x = 1894
    #     self.size_y = 1974
    #     self.short_name = 'TAMSAT_Africa_4km'
    #
    # def assign_modis_global(self):
    #     # Assign the native TAMSAT Africa Mapset
    #     self.spatial_ref.SetWellKnownGeogCS("WGS84")
    #     # Geo-transform is from old ingest_tamsat.sh
    #     self.geo_transform = [-180.0, 0.04166666666666667, 0.0, 90.0, 0.0, -0.04166666666666667]
    #     # as in the old ingest_rfe.sh
    #     # Set additional info, as from FEWSNET website
    #     self.size_x = 8640
    #     self.size_y = 4320
    #     self.short_name = 'MODIS_Global_4km'
