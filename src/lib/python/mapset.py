#
#	purpose: Define the mapset class
#	author:  M. Clerici
#	date:	 25.02.2014
#   descr:	 Defines members and methods of the mapset class
#
#   TODO-M.C.: Define methods to assess relationships between mapsets (e.g. included)
#

# source eStation2 base definitions
import locals

# Import eStation lib modules
from database import querydb

# Import third-party modules
from osgeo import gdalconst
from osgeo import gdal
from osgeo import osr
import pygrib
import numpy as N


class MapSet:

    def __init__(self):
        self.spatial_ref = osr.SpatialReference()
        self.geo_transform = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.size_x = 0
        self.size_y = 0
        self.short_name = ''

    def assigndb(self, mapsetcode):
        mapset = querydb.get_mapset(mapsetcode, echo=False)
        spatial_ref_wkt = mapset.srs_wkt
        geo_transform = [mapset.upper_left_long,
                         mapset.pixel_shift_long,
                         mapset.rotation_factor_long,
                         mapset.upper_left_lat,
                         mapset.rotation_factor_lat,
                         mapset.pixel_shift_lat]

        self.spatial_ref.ImportFromWkt(spatial_ref_wkt)
        self.geo_transform = geo_transform
        self.size_x = int(mapset.pixel_size_x)
        self.size_y = int(mapset.pixel_size_y)
        self.short_name = mapset.mapsetcode

    def assign(self, spatial_ref_wkt, geo_transform, size_x, size_y, short_name):
        # Assign to passed arguments
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

    def assign_ecowas(self):
        # Assign the VGT4Africa default mapset for ECOWAS region
        self.spatial_ref.SetWellKnownGeogCS("WGS84")
        self.geo_transform = [-19.004464285714285, 0.008928571428571, 0.0, 28.004464285714285, 0.0, -0.008928571428571]
        self.size_x = 4929
        self.size_y = 2689
        self.short_name = 'WGS84_ECOWAS_1km'

    def assign_ioc_pml(self):
        # Assign the VGT4Africa default mapset for ECOWAS region
        self.spatial_ref.SetWellKnownGeogCS("WGS84")
        self.geo_transform = [31.9955357, 0.008993207901969, 0.0, 5.004464285714285, 0.0, -0.008993207029328]
        self.size_x = 4278
        self.size_y = 3670
        self.short_name = 'WGS84_ECOWAS_1km'

    def assign_vgt4africa(self):
        # Assign the VGT4Africa default mapset (continental)
        self.spatial_ref.SetWellKnownGeogCS("WGS84")
        self.geo_transform = [-26.004464285714285, 0.008928571428571, 0.0, 38.004464285714285, 0.0, -0.008928571428571]
        self.size_x = 9633
        self.size_y = 8177
        self.short_name = 'WGS84_Africa_1km'

    def assign_vgt4africa_500m(self):
        # Assign the VGT4Africa default mapset (continental)
        self.spatial_ref.SetWellKnownGeogCS("WGS84")
        self.geo_transform = [-26.004464285714285, 0.0044642857142855, 0.0, 38.004464285714285, 0.0, -0.0044642857142855]
        self.size_x = 19266         # 9633*2
        self.size_y = 16354         # 8177*2
        self.short_name = 'WGS84_Africa_500m'

    def assign_msg_disk(self):
        # Assign the msg geostationary proj (see http://osdir.com/ml/gdal-development-gis-osgeo/2010-03/msg00029.html)
        # Note 1: gdalinfo will raise errors: 'ERROR 1: tolerance condition error' for the 4 corners, as the are out
        # of the globe surface -> no problem (see: https://trac.osgeo.org/gdal/ticket/4381)
        # Note 2: if we read SpatRef from grib file, does not Validate
        proj4def = "+proj=geos +lon_0=0 +h=35785831 +DATUM=WGS84"
        self.spatial_ref.ImportFromProj4(proj4def)
        # Set additional inf
        #self.spatial_ref.SetAttrValue('PROJCS|GEOCS|DATUM',"WGS84")

        self.geo_transform = [-5570248.477582973, 3000.4031659482757, 0.0, 5570248.477582973, 0.0, -3000.4031659482757]
        self.size_x = 3712
        self.size_y = 3712
        self.short_name = 'MSG_satellite_3km'

    def assign_fewsnet_africa(self):
        # Assign the Alberts Equal Area Conic proj(see http://earlywarning.usgs.gov/fews/africa/web/readme.php?symbol=rf)
        # Geo-transform is read from the input file (.blw)
        self.geo_transform = [-4241357.154883339, 8000.0, 0.0, 4276328.591286063, 0.0, -8000.0]
        # as in the old ingest_rfe.sh
        proj4def = "+proj=aea +lat_1=-19 +lat_2=21 +lat_0=1 +lon_0=20 +x_0=0 +y_0=0"
        self.spatial_ref.ImportFromProj4(proj4def)
        # Set additional info, as from FEWSNET website
        self.spatial_ref.SetAttrValue('PROJCS', "Albers_Conical_Equal_Area")
        #self.spatial_ref.SetAttrValue('PROJCS|GEOCS|DATUM|SPHEROID', "Clarke 1866")

        self.size_x = 994
        self.size_y = 1089
        self.short_name = 'AEA_Africa_8km'

    def assign_tamsat_africa(self):
        # Assign the native TAMSAT Africa Mapset
        self.spatial_ref.SetWellKnownGeogCS("WGS84")
        # Geo-transform is from old ingest_tamsat.sh
        self.geo_transform = [-19.0312, 0.0375, 0.0, 38.0437, 0.0, -0.0375]
        # as in the old ingest_rfe.sh
        # Set additional info, as from FEWSNET website
        self.size_x = 1894
        self.size_y = 1974
        self.short_name = 'TAMSAT_Africa_4km'

    def assign_modis_global(self):
        # Assign the native TAMSAT Africa Mapset
        self.spatial_ref.SetWellKnownGeogCS("WGS84")
        # Geo-transform is from old ingest_tamsat.sh
        self.geo_transform = [-180.0, 0.04166666666666667, 0.0, 90.0, 0.0, -0.04166666666666667]
        # as in the old ingest_rfe.sh
        # Set additional info, as from FEWSNET website
        self.size_x = 8640
        self.size_y = 4320
        self.short_name = 'MODIS_Global_4km'

    def print_out(self):
        # Print Information on the mapset
        print 'Spatial Ref WKT: ' + self.spatial_ref.ExportToWkt()
        print 'GeoTransform   : ', self.geo_transform
        print 'SizeX          : ', self.size_x
        print 'SizeY          : ', self.size_y
        print 'Shortname      : ', self.short_name

    def validate(self, echo=False):

        # Initialize as OK
        result = 0

        # Validate the Spatial Reference
        if echo:
            print 'Spatial Ref Validate [0=ok]: ' + str(self.spatial_ref.Validate())
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
            print 'Geo Transfo Validate [0=ok]: ' + str(code_gt)
        result += code_gt

        code_size_x = isinstance(self.size_x, int) and self.size_x > 0
        if echo:
            print 'Size X positive number     : ' + str(code_size_x)
        if not code_size_x:
            result += 1

        code_size_y = isinstance(self.size_y, int) and self.size_y > 0
        if echo:
            print 'Size Y positive number     : ' + str(code_size_y)
        if not code_size_y:
            result += 1

        return result