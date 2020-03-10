from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = 'clerima'

#
#   Rotate by 180 degrees the initially ingested MSG-MPE products
#
import glob
import os, unittest
import numpy as N
from osgeo import gdal
from osgeo import osr

from lib.python import es_logging as log
from lib.python import metadata
from config import es_constants

my_logger = log.my_logger(__name__)


# Create a new file in output dir, with same name and metadata, but flipped array inside
def rotate_mpe(input_file, output_dir):

    basename = os.path.basename(input_file)
    output_file = output_dir+basename

    my_logger.info('Working on file {0}'.format(basename))

    out_data_type_gdal = gdal.GDT_Int16

    # Instance metadata object and read from source
    sds_meta = metadata.SdsMetadata()
    sds_meta.read_from_file(input_file)

    # Load data from source
    orig_ds = gdal.Open(input_file, gdal.GA_ReadOnly)
    orig_cs = osr.SpatialReference()
    orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
    orig_geo_transform = orig_ds.GetGeoTransform()
    orig_size_x = orig_ds.RasterXSize
    orig_size_y = orig_ds.RasterYSize

    band = orig_ds.GetRasterBand(1)
    orig_data = band.ReadAsArray(0, 0, orig_size_x, orig_size_y)

    # Prepare output driver
    out_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)

    # Play with data
    rev_data = N.flipud(orig_data)
    orig_data = N.fliplr(rev_data)

    # No reprojection, only format-conversion
    trg_ds = out_driver.Create(output_file, orig_size_x, orig_size_y, 1, out_data_type_gdal,
                               [es_constants.ES2_OUTFILE_OPTIONS])

    trg_ds.SetProjection(orig_ds.GetProjectionRef())
    trg_ds.SetGeoTransform(orig_geo_transform)

    trg_ds.GetRasterBand(1).WriteArray(orig_data)

    sds_meta.write_to_ds(trg_ds)
    orig_ds = None
    trg_ds = None

    # Rename the original file
    os.rename(input_file,input_file+'.wrong')

def correct_all():

    # Drive the loop for correction

    input_dir = '/data/processing/msg-mpe-old/undefined/MSG-satellite-3km/tif/mpe/'
    output_dir = '/data/processing/msg-mpe/undefined/MSG-satellite-3km/tif/mpe/'

    files_list = glob.glob(input_dir+'*.tif')

    for myfile in files_list:
        rotate_mpe(myfile, output_dir)

class TestRotate(unittest.TestCase):

    def TestCase(self):

        in_file='/data/processing/msg-mpe-old/undefined/MSG-satellite-3km/tif/mpe/201609011200_msg-mpe_mpe_MSG-satellite-3km_undefined.tif'
        output_dir = '/data/processing/msg-mpe/undefined/MSG-satellite-3km/tif/mpe/'
        rotate_mpe(in_file, output_dir)

    def TestRunAll(self):

        correct_all()
