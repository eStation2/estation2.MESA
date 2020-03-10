from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Find a file with a 'larger' area and clip to the requested one
#	author:  M. Clerici
#	date:	 07.08.2018
#
#   Arguments:  IN: fullpath of file to be clipped
#               IN: output file to be generated
#               IN: mapset of the requested file
#

from builtins import round
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.builtins import basestring
from builtins import object
try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo.gdalconst import *
    gdal.TermProgress = gdal.TermProgress_nocb
except ImportError:
    import gdal, osr
    from gdalconst import *

import os
import datetime
import sys
import glob

# TODO: add more checks to the code - very error prone now
# TODO: update and/or pass as an argument
base_data_dir = '/data/processing/'

sds_metadata = { 'eStation2_es2_version': '',               # 0. eStation 2 version (the fields below might depend on es2_version)

                                                            # ------------------  Mapset        ----------------------
                 'eStation2_mapset': '',                    # 1. Mapsetcode

                                                            # ------------------  As in the 'product' table ----------------------
                 'eStation2_product': '',                   # 2. productcode
                 'eStation2_subProduct': '',                # 3. subproductcode
                 'eStation2_product_version': '',           # 4. product version (e.g. MODIS Collection 4 or 5; by default is undefined -> '')

                 'eStation2_defined_by': '',                # 5. JRC or User
                 'eStation2_category': '',                  # 6. Product category
                 'eStation2_descr_name': '',                # 7. Product Descriptive Name
                 'eStation2_description': '',               # 8. Product Description
                 'eStation2_provider': '',                  # 9. Product provider (NASA, EUMETSAT, VITO, ..)

                 'eStation2_date_format': '',               # 10. Date format (YYYYMMDDHHMM, YYYYMMDD or MMDD)
                 'eStation2_frequency': '',                 # 11. Product frequency (as in db table 'frequency')

                 'eStation2_scaling_factor': '',            # 12. Scaling factors
                 'eStation2_scaling_offset': '',            # 13. Scaling offset
                 'eStation2_unit': '',                      # 14. physical unit (none for pure numbers, e.g. NDVI)
                 'eStation2_nodata': '',                    # 15. nodata value
                 'eStation2_subdir': '',                    # 16. subdir in the eStation data tree (redundant - to be removed ??)

                                                            # ------------------  File Specific ----------------------
                 'eStation2_date': '',                      # 17. Date of the product

                                                            # ------------------  File/Machine Specific ----------------------
                 'eStation2_input_files': '',               # 18. Input files used for computation
                 'eStation2_comp_time': '',                 # 19. Time of computation
                 'eStation2_mac_address': '',               # 20. Machine MAC address

                                                            # ------------------  Fixed         ----------------------
                 'eStation2_conversion': ''                 # 21. Rule for converting DN to physical values (free text)


}

class SdsMetadata(object):

    def __init__(self):

        sds_metadata['eStation2_es2_version'] = 'my_eStation2_sw_release'

        sds_metadata['eStation2_mapset'] = 'my_mapset_code'

        sds_metadata['eStation2_product'] = 'my_product'
        sds_metadata['eStation2_subProduct'] = 'my_sub_product'
        sds_metadata['eStation2_product_version'] = 'my_product_version'

        sds_metadata['eStation2_defined_by'] = 'JRC'
        sds_metadata['eStation2_category'] = 'my_product_category'
        sds_metadata['eStation2_descr_name'] = 'my_descriptive_name'
        sds_metadata['eStation2_description'] = 'my_description'
        sds_metadata['eStation2_provider'] = 'my_product_provider'

        sds_metadata['eStation2_date_format'] = 'YYYYMMDDHHMM'
        sds_metadata['eStation2_frequency'] = 'my_frequency'

        sds_metadata['eStation2_conversion'] = 'Phys = DN * scaling_factor + scaling_offset'
        sds_metadata['eStation2_scaling_factor'] = 'my_scaling_factor'
        sds_metadata['eStation2_scaling_offset'] = 'my_scaling_offset'
        sds_metadata['eStation2_unit'] = 'my_unit'
        sds_metadata['eStation2_nodata'] = 'my_nodata'
        sds_metadata['eStation2_subdir'] = 'my_subdir'

        sds_metadata['eStation2_date'] = 'my_date'
        sds_metadata['eStation2_input_files'] = '/my/path/to/file/and/filename1'
        sds_metadata['eStation2_comp_time'] = 'my_comp_time'
        sds_metadata['eStation2_mac_address'] = 'N.A.'

        sds_metadata['eStation2_parameters'] = 'my_processing_parameters'

    def write_to_ds(self, dataset):
    #
    #   Writes  metadata to a target dataset (already opened gdal dataset)
    #   Args:
    #       dataset: osgeo.gdal dataset (open and georeferenced)

        # Check argument ok
        if not isinstance(dataset,gdal.Dataset):
            print ('The argument should be an open GDAL Dataset. Exit')
        else:
            # Go through the metadata list and write to sds
            for key, value in sds_metadata.items():
                # Check length of value
                if len(str(value)) > 1000:
                    wrt_value=str(value)[0:1000]+' + others ...'
                else:
                    wrt_value=str(value)
                dataset.SetMetadataItem(key, wrt_value)

    def write_to_file(self, filepath):
    #
    #   Writes  metadata to a target file
    #   Args:
    #       dataset: osgeo.gdal dataset (open and georeferenced)

        # Check the output file exist
        if not os.path.isfile(filepath):
             print ('Output file does not exist %s' % filepath)
        else:
            # Open output file
            sds = gdal.Open(filepath, GA_Update)
            self.write_to_ds(sds)

    def read_from_ds(self, dataset):
    #
    #   Read metadata structure from an opened file
    #   Args:
    #       dataset: osgeo.gdal dataset (open and georeferenced)

        # Check argument ok
        if not isinstance(dataset,gdal.Dataset):
            print ('The argument should be an open GDAL Dataset. Exit')
        else:

            # Go through the metadata list and write to sds
            for key, value in sds_metadata.items():
                try:
                    value = dataset.GetMetadataItem(key)
                    sds_metadata[key] = value
                except:
                    sds_metadata[key] = 'Not found in file'
                    print ('Error in reading metadata item %s' % key)

    def read_from_file(self, filepath):
    #
    #   Read metadata structure from a source file
    #   Args:
    #       filepath: full file path (dir+name)

        # Check the file exists
        if not os.path.isfile(filepath):
            print ('Input file does not exist %s' % filepath)
        else:
            # Open it and read metadata
            infile=gdal.Open(filepath)
            self.read_from_ds(infile)

            # Close the file
            infile= None

    def assign_comput_time_now(self):
    #
    #   Assign current time to 'comp_time'

        curr_time=datetime.datetime.now()
        str_datetime=curr_time.strftime("%Y-%m-%d %H:%M:%S")
        sds_metadata['eStation2_comp_time']=str_datetime

    def assign_mapset(self, mapset_code):
    #
    #   Assign mapset
        sds_metadata['eStation2_mapset'] = str(mapset_code)

    def assign_subdir(self, subdirectory):
    #
    #   Assign subdir
        sds_metadata['eStation2_subdir'] = str(subdirectory)

    def print_out(self):
    #
    #   Writes to std output

        # Go through the metadata list and write to sds
        for key, value in sds_metadata.items():
            print((key, value))


def get_all_from_path_dir(dir_name):

    # Make sure there is a leading separator at the end of 'dir'
    mydir=dir_name+os.path.sep

    tokens = [token for token in mydir.split(os.sep) if token]
    sub_product_code = tokens[-1]
    product_type = tokens[-2]
    mapset = tokens[-3]
    version =  tokens[-4]
    product_code =  tokens[-5]

    return [product_code, sub_product_code, version, mapset, product_type]

def set_path_filename_no_date(product_code, sub_product_code, mapset_id, version, extension):

    filename_nodate =     "_" + str(product_code) + '_' \
                              + str(sub_product_code) + "_" \
                              + mapset_id +  "_" \
                              + version + extension

    return filename_nodate

def set_path_sub_directory(product_code, sub_product_code, type_subdir, version, mapset):

    sub_directory = str(product_code) + os.path.sep + \
                    str(version) + os.path.sep + \
                    mapset + os.path.sep + \
                    type_subdir + os.path.sep +\
                    str(sub_product_code) + os.path.sep

    return sub_directory

def get_all_from_filename(filename):

    # Get info from directory
    tokens = [token for token in filename.split('_') if token]
    str_date = tokens[0]
    product_code = tokens[1]
    sub_product_code = tokens[2]
    mapset = tokens[3]
    # Remove extension from tokens[4] -> version
    parts = tokens[4].split('.')
    version = tokens[4].replace('.'+parts[-1],'')

    return [str_date, product_code, sub_product_code, mapset, version]

def get_date_from_path_filename(filename):

    str_date = filename.split('_')[0]

    return str_date

def is_larger(candidate_file, trg_mapset):

    # Check the candidate file is suitable for extracting the requested one
    # Look only at the Boundary Box [xmin,ymin] is LL, [xmax,ymax] is UR
    # NOTE: geo_transform contains UL [xmin,ymax]

    # Get geo-info from candidate file
    available_ds = gdal.Open(candidate_file)

    # Manage geo-referencing for 'available' file
    available_geo_transform = available_ds.GetGeoTransform()
    available_size_x = available_ds.RasterXSize
    available_size_y = available_ds.RasterYSize
    available_ds = None
    available_deltax = available_geo_transform[1]
    available_deltay = available_geo_transform[5]

    available_xmin = available_geo_transform[0]
    available_xmax = available_xmin+available_deltax*available_size_x

    available_ymax = available_geo_transform[3]
    available_ymin = available_ymax+available_deltay*available_size_y

    # Manage geo-referencing for requested mapset
    requested_deltax = trg_mapset["pixel_shift_long"]
    requested_deltay = trg_mapset["pixel_shift_lat"]

    requested_xmin = trg_mapset["upper_left_long"]
    requested_xmax = requested_xmin+requested_deltax*trg_mapset["pixel_size_x"]

    requested_ymax = trg_mapset["upper_left_lat"]
    requested_ymin = requested_ymax+requested_deltay*trg_mapset["pixel_size_y"]

    # Compare the two BBoxes
    is_larger = False
    if round(available_xmin, 8) <= round(requested_xmin, 8) \
            and round(available_xmax, 8) >= round(requested_xmax, 8) \
            and round(available_ymin, 8) <= round(requested_ymin, 8) \
            and round(available_ymax, 8) >= round(requested_ymax, 8):
        is_larger = True

    # print (is_larger)
    # is_larger = True
    # if available_xmin >= requested_xmin or available_xmax <= requested_xmax or available_ymin >= requested_ymin or available_ymax <= requested_ymax:
    #     is_larger = False

    return is_larger

def set_path_filename(date_str, product_code, sub_product_code, mapset_id, version,  extension):

    filename = date_str + set_path_filename_no_date(product_code, sub_product_code, mapset_id, version, extension)
    return filename

def do_find_larger(requested_file, trg_mapset):

    # Look for another file (i.e. another mapset)
    [product_code, sub_product_code, version, mapset, type_subdir] = get_all_from_path_dir(os.path.dirname(requested_file))
    str_date = get_date_from_path_filename(os.path.basename(requested_file))
    my_mapset='*'
    re_subdir=set_path_sub_directory(product_code, sub_product_code, type_subdir, version, my_mapset)
    re_filename=set_path_filename(str_date, product_code, sub_product_code, my_mapset, version,  '.tif')

    available_files = glob.glob(base_data_dir+os.path.sep+re_subdir+re_filename)

    # Check the mapset is 'larger'
    if isinstance(available_files, basestring):
        my_list = [available_files]
    else:
        my_list = available_files
    for candidate_file in my_list:
        if is_larger(candidate_file, trg_mapset):
            return candidate_file
    return ''


def do_clip(inputfile, outputfile, trg_mapset):


    # Open the input file
    orig_ds = gdal.Open(inputfile)

    # Read all geo-referencing
    orig_cs = osr.SpatialReference()
    orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
    orig_geo_transform = orig_ds.GetGeoTransform()
    orig_size_x = orig_ds.RasterXSize
    orig_size_y = orig_ds.RasterYSize
    orig_band = orig_ds.GetRasterBand(1)
    orig_ds.SetProjection(orig_cs.ExportToWkt())

    # Read also DataType
    in_data_type = orig_band.DataType

    # Prepare output geo-referencing
    spatial_ref_wkt = trg_mapset["srs_wkt"]
    spatial_ref = osr.SpatialReference()
    out_cs = spatial_ref.ImportFromWkt(spatial_ref_wkt)
    out_cs = osr.SpatialReference(wkt=spatial_ref_wkt)

    out_size_x = trg_mapset["pixel_size_x"]
    out_size_y = trg_mapset["pixel_size_y"]

    # Create target in memory
    mem_driver = gdal.GetDriverByName('MEM')

    # Assign mapset to dataset in memory
    out_data_type_gdal = in_data_type
    mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, out_data_type_gdal)
    output_geo_transform=[trg_mapset["upper_left_long"],
                          trg_mapset["pixel_shift_long"],
                          trg_mapset["rotation_factor_long"],
                          trg_mapset["upper_left_lat"],
                          trg_mapset["rotation_factor_lat"],
                          trg_mapset["pixel_shift_lat"]]

    mem_ds.SetGeoTransform(output_geo_transform)
    mem_ds.SetProjection(out_cs.ExportToWkt())

    # Do the Re-projection
    orig_wkt = orig_cs.ExportToWkt()
    res = gdal.ReprojectImage(orig_ds, mem_ds, orig_wkt, out_cs.ExportToWkt(),
                              GRA_NearestNeighbour)

    out_data = mem_ds.ReadAsArray()

    output_driver = gdal.GetDriverByName('GTiff')
    output_ds = output_driver.Create(outputfile, out_size_x, out_size_y, 1, in_data_type)
    output_ds.SetGeoTransform(output_geo_transform)
    output_ds.SetProjection(out_cs.ExportToWkt())
    output_ds.GetRasterBand(1).WriteArray(out_data,0,0)

    trg_ds = None
    mem_ds = None
    orig_ds = None
    output_driver = None
    output_ds = None

    # Copy metadata, by changing mapset only
    meta_data = SdsMetadata()
    meta_data.read_from_file(inputfile)
    meta_data.assign_mapset(trg_mapset["mapsetcode"])
    meta_data.write_to_file(outputfile)

# _____# ______________________________
if __name__=="__main__":


    inputfile = None

    ii = 1
    while ii < len(sys.argv):
        arg = sys.argv[ii]

        if arg == '-if':
            ii = ii + 1
            requested_file = sys.argv[ii]

        elif arg == '-odir':
            ii = ii + 1
            outputdir = sys.argv[ii]

        elif arg == '-descr':
            ii = ii + 1
            description = sys.argv[ii]

        elif arg == '-mapsetcode':
            ii = ii + 1
            mapsetcode = sys.argv[ii]

        elif arg == '-pixel_shift_lat':
            ii = ii + 1
            pixel_shift_lat = float(sys.argv[ii])

        elif arg == '-pixel_shift_long':
            ii = ii + 1
            pixel_shift_long = float(sys.argv[ii])

        elif arg == '-pixel_size_x':
            ii = ii + 1
            pixel_size_x = int(sys.argv[ii])

        elif arg == '-pixel_size_y':
            ii = ii + 1
            pixel_size_y = int(sys.argv[ii])

        elif arg == '-rotation_factor_lat':
            ii = ii + 1
            rotation_factor_lat = float(sys.argv[ii])

        elif arg == '-rotation_factor_long':
            ii = ii + 1
            rotation_factor_long = float(sys.argv[ii])

        elif arg == '-upper_left_lat':
            ii = ii + 1
            upper_left_lat = float(sys.argv[ii])

        elif arg == '-upper_left_long':
            ii = ii + 1
            upper_left_long = float(sys.argv[ii])

        # elif arg == '-srs_wkt':
        #     ii = ii + 1
        #     srs_wkt = sys.argv[ii]
        srs_wkt = "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9108\"]],AUTHORITY[\"EPSG\",\"4326\"]]"

        ii = ii + 1

    # Check inputs - TO BE COMPLETED !!

    if requested_file is None:
        print ('Missing the requested file name. Exit')
        exit(1)


    # Check the requested file is there
    if os.path.exists(requested_file):
        print ('Requested file exists, no need to clip. Exit')
        exit()

    output_mapset = {"description": description,
                     "mapsetcode": mapsetcode,
                     "pixel_shift_lat": pixel_shift_lat,
                     "pixel_shift_long": pixel_shift_long,
                     "pixel_size_x": pixel_size_x,
                     "pixel_size_y": pixel_size_y,
                     "rotation_factor_lat": rotation_factor_lat,
                     "rotation_factor_long": rotation_factor_long,
                     "srs_wkt": srs_wkt,
                     "upper_left_lat": upper_left_lat,
                     "upper_left_long": upper_left_long}

    larger_file = do_find_larger(requested_file, output_mapset)
    clipped_file = outputdir+os.path.basename(requested_file)

    if larger_file is not '':
        do_clip(larger_file, clipped_file, output_mapset)
    else:
        print ('ERROR: No any file found. Exit')
        exit()

    print ('INFO: The clipped file has been generated {0}. Exit.'.format(clipped_file))
