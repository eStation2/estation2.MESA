#
#	purpose: Define the metadata class
#	author:  M. Clerici
#	date:	 31.03.2014
#   descr:	 Defines members and methods of the metadata class
#
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
from builtins import str
from past.builtins import basestring
from builtins import object

import os
import datetime
import os.path
from config import es_constants

from osgeo import gdal
from osgeo import gdalconst
from .functions import *

# Import eStation2 modules
from lib.python import es_logging as log
from lib.python import functions
from database import querydb

standard_library.install_aliases()

logger = log.my_logger(__name__)


class SdsMetadata(object):

    def __init__(self):

        # TODO-M.C.: Add all the attributes of 'mapset' and 'category_id' ?
        #  so that the contents of the db tables can be created (if not existing on the target station) from metadata ?

        self.sds_metadata = {'eStation2_es2_version': '',
                            # 0. eStation 2 version (the fields below might depend on es2_version)

                            # ------------------  Mapset        ----------------------
                            'eStation2_mapset': '',  # 1. Mapsetcode

                            # ------------------  As in the 'product' table ----------------------
                            'eStation2_product': '',  # 2. productcode
                            'eStation2_subProduct': '',  # 3. subproductcode
                            'eStation2_product_version': '',
                            # 4. product version (e.g. MODIS Collection 4 or 5; by default is undefined -> '')

                            'eStation2_defined_by': '',  # 5. JRC or User
                            'eStation2_category': '',  # 6. Product category (TODO-M.C.: double-check wrt INSPIRE)
                            'eStation2_descr_name': '',  # 7. Product Descriptive Name
                            'eStation2_description': '',  # 8. Product Description
                            'eStation2_provider': '',  # 9. Product provider (NASA, EUMETSAT, VITO, ..)

                            'eStation2_date_format': '',  # 10. Date format (YYYYMMDDHHMM, YYYYMMDD or MMDD)
                            'eStation2_frequency': '',  # 11. Product frequency (as in db table 'frequency')

                            'eStation2_scaling_factor': '',  # 12. Scaling factors
                            'eStation2_scaling_offset': '',  # 13. Scaling offset
                            'eStation2_unit': '',  # 14. physical unit (none for pure numbers, e.g. NDVI)
                            'eStation2_nodata': '',  # 15. nodata value
                            'eStation2_subdir': '',  # 16. subdir in the eStation data tree (redundant - to be removed ??)

                            # ------------------  File Specific ----------------------
                            'eStation2_date': '',  # 17. Date of the product

                            # ------------------  File/Machine Specific ----------------------
                            'eStation2_input_files': '',  # 18. Input files used for computation
                            'eStation2_comp_time': '',  # 19. Time of computation
                            'eStation2_mac_address': '',  # 20. Machine MAC address

                            # ------------------  Fixed         ----------------------
                            'eStation2_conversion': ''  # 21. Rule for converting DN to physical values (free text)
                        }

        self.sds_metadata['eStation2_es2_version'] = 'my_eStation2_sw_release'

        self.sds_metadata['eStation2_mapset'] = 'my_mapset_code'

        self.sds_metadata['eStation2_product'] = 'my_product'
        self.sds_metadata['eStation2_subProduct'] = 'my_sub_product'
        self.sds_metadata['eStation2_product_version'] = 'my_product_version'

        self.sds_metadata['eStation2_defined_by'] = 'JRC'
        self.sds_metadata['eStation2_category'] = 'my_product_category'
        self.sds_metadata['eStation2_descr_name'] = 'my_descriptive_name'
        self.sds_metadata['eStation2_description'] = 'my_description'
        self.sds_metadata['eStation2_provider'] = 'my_product_provider'

        self.sds_metadata['eStation2_date_format'] = 'YYYYMMDDHHMM'
        self.sds_metadata['eStation2_frequency'] = 'my_frequency'

        self.sds_metadata['eStation2_conversion'] = 'Phys = DN * scaling_factor + scaling_offset'
        self.sds_metadata['eStation2_scaling_factor'] = 'my_scaling_factor'
        self.sds_metadata['eStation2_scaling_offset'] = 'my_scaling_offset'
        self.sds_metadata['eStation2_unit'] = 'my_unit'
        self.sds_metadata['eStation2_nodata'] = 'my_nodata'
        self.sds_metadata['eStation2_subdir'] = 'my_subdir'

        self.sds_metadata['eStation2_date'] = 'my_date'
        self.sds_metadata['eStation2_input_files'] = '/my/path/to/file/and/filename1'
        self.sds_metadata['eStation2_comp_time'] = 'Undefined'
        self.sds_metadata['eStation2_mac_address'] = get_machine_mac_address()

        self.sds_metadata['eStation2_parameters'] = 'None'

    def write_to_ds(self, dataset):
        #   Writes  metadata to a target dataset (already opened gdal dataset)
        #   Args:
        #       dataset: osgeo.gdal dataset (open and georeferenced)

        # Check argument ok
        if not isinstance(dataset, gdal.Dataset):
            logger.error('The argument should be an open GDAL Dataset. Exit')
        else:
            # Go through the metadata list and write to sds
            for key, value in list(self.sds_metadata.items()):
                # Check length of value
                if len(str(value)) > 1000:
                    wrt_value = str(value)[0:1000] + ' + others ...'
                else:
                    wrt_value = str(value)
                dataset.SetMetadataItem(key, wrt_value)

    def write_to_file(self, filepath):
        #   Writes  metadata to a target file
        #   Args:
        #       filepath: filepath to a target file

        # Check the output file exist
        if not os.path.isfile(filepath):
            logger.error('Output file does not exist %s' % filepath)
        else:
            # Open output file
            sds = gdal.Open(filepath, gdalconst.GA_Update)
            self.write_to_ds(sds)

    def read_from_ds(self, dataset):
        #   Read metadata structure from an opened file
        #   Args:
        #       dataset: osgeo.gdal dataset (open and georeferenced)

        # Check argument ok
        if not isinstance(dataset, gdal.Dataset):
            logger.error('The argument should be an open GDAL Dataset. Exit')
        else:

            # Go through the metadata list and write to sds
            for key, value in list(self.sds_metadata.items()):
                try:
                    value = dataset.GetMetadataItem(key)
                    self.sds_metadata[key] = value
                except:
                    self.sds_metadata[key] = 'Not found in file'
                    logger.error('Error in reading metadata item %s' % key)

    def read_from_file(self, filepath):
        #   Read metadata structure from a source file
        #   Args:
        #       filepath: full file path (dir+name)

        # Check the file exists
        if not os.path.isfile(filepath):
            logger.error('Input file does not exist %s' % filepath)
        else:
            # Open it and read metadata
            infile = gdal.Open(filepath)
            self.read_from_ds(infile)

            # Close the file
            infile = None

    def assign_es2_version(self):
        #   Assign the es2_version
        self.sds_metadata['eStation2_es2_version'] = es_constants.es2_sw_version

    def assign_compute_time_now(self):
        #   Assign current time to 'comp_time'
        curr_time = datetime.datetime.now()
        str_datetime = curr_time.strftime("%Y-%m-%d %H:%M:%S")
        self.sds_metadata['eStation2_comp_time'] = str_datetime

    def assign_from_product(self, product, subproduct, version):
        try:
            product_out_info = querydb.get_product_out_info(productcode=product, subproductcode=subproduct,
                                                            version=version)
        except:
            logger.error('The product is not defined in the DB')
            return 1

        product_out_info = functions.list_to_element(product_out_info)

        #   Assign prod/subprod/version
        self.sds_metadata['eStation2_product'] = str(product)
        self.sds_metadata['eStation2_subProduct'] = str(subproduct)
        if isinstance(version, str) or isinstance(version, str):
            self.sds_metadata['eStation2_product_version'] = version
        else:
            self.sds_metadata['eStation2_product_version'] = 'undefined'

        self.sds_metadata['eStation2_defined_by'] = product_out_info.defined_by
        self.sds_metadata['eStation2_category'] = product_out_info.category_id
        self.sds_metadata['eStation2_descr_name'] = product_out_info.descriptive_name
        self.sds_metadata['eStation2_description'] = product_out_info.description
        self.sds_metadata['eStation2_provider'] = product_out_info.provider
        self.sds_metadata['eStation2_date_format'] = product_out_info.date_format
        self.sds_metadata['eStation2_frequency'] = product_out_info.frequency_id
        self.sds_metadata['eStation2_scaling_factor'] = product_out_info.scale_factor
        self.sds_metadata['eStation2_scaling_offset'] = product_out_info.scale_offset
        self.sds_metadata['eStation2_unit'] = product_out_info.unit
        self.sds_metadata['eStation2_nodata'] = product_out_info.nodata

    def assign_product_elements(self, product, subproduct, version):
        #   Assign prod/subprod/version
        self.sds_metadata['eStation2_product'] = str(product)
        self.sds_metadata['eStation2_subProduct'] = str(subproduct)

        if isinstance(version, str):
            self.sds_metadata['eStation2_product_version'] = version
        else:
            self.sds_metadata['eStation2_product_version'] = 'undefined'

    def assign_date(self, outputdate):
        #   Assign date of the product
        self.sds_metadata['eStation2_date'] = str(outputdate)

    def assign_mapset(self, mapset_code):
        #   Assign mapset
        self.sds_metadata['eStation2_mapset'] = str(mapset_code)

    def assign_subdir_from_fullpath(self, full_directory):
        #   Assign subdir
        subdir = functions.get_subdir_from_path_full(full_directory)
        self.sds_metadata['eStation2_subdir'] = str(subdir)

    def assign_subdir(self, subdirectory):
        #   Assign subdir
        self.sds_metadata['eStation2_subdir'] = str(subdirectory)

    def assign_input_files(self, input_files):
        #   Assign input file list
        file_string = ''
        if isinstance(input_files, basestring):
            file_string += os.path.basename(input_files) + ';'
        else:
            for ifile in input_files:
                file_string += os.path.basename(ifile) + ';'
        self.sds_metadata['eStation2_input_files'] = file_string

    def merge_input_file_lists(self, old_list, input_files):
        #   Merge new list to the existing one (which is a string)

        true_list = old_list.split(';')
        true_list_not_empty = []
        for elem in true_list:
            if elem != '':
                true_list_not_empty.append(os.path.basename(elem))
        for infile in input_files:
            if not infile in true_list_not_empty:
                true_list_not_empty.append(os.path.basename(infile))
        return true_list_not_empty

    def assign_scaling(self, scaling_factor, scaling_offset, nodata, unit):
        #   Assign scaling
        self.sds_metadata['eStation2_scaling_factor'] = str(scaling_factor)
        self.sds_metadata['eStation2_scaling_offset'] = str(scaling_offset)
        self.sds_metadata['eStation2_nodata'] = str(nodata)
        self.sds_metadata['eStation2_unit'] = str(unit)

    def assign_nodata(self, nodata):
        #   Assign scaling
        self.sds_metadata['eStation2_nodata'] = str(nodata)

    def assign_single_paramater(self, parameter_key, parameter_value):
        # ES2-293 ES2-292
        #   Assign Single Parameter
        self.sds_metadata[parameter_key] = str(parameter_value)

    def assign_scl_factor(self, scl_factor):
        #   Assign scaling
        self.sds_metadata['eStation2_scaling_factor'] = str(scl_factor)

    def assign_parameters(self, parameters):
        #   Assign parameters (defined specifically for SST-FRONTS detection)
        parameters_string = ''
        for key, value in sorted(parameters.items()):
            parameters_string += '{}={}; '.format(key, value)

        self.sds_metadata['eStation2_parameters'] = parameters_string

    def get_item(self, itemname):
        value = 'metadata item not found'
        try:
            value = self.sds_metadata[itemname]
        except:
            pass

        return value

    def get_target_filepath(self, input_file):
        # Given a .GTiff file, reads its metadata and build-up the target fullpath
        # Input filename does not need to be in the eStation2 format, everything read from metadata

        # Check the file exists
        if os.path.isfile(input_file):
            try:
                self.read_from_file(input_file)
            except:
                logger.warning('Error in loading from file %s . Exit' % input_file)

            target_subdir = self.sds_metadata['eStation2_subdir']
            target_dir = es_constants.es2globals['processing_dir'] + target_subdir
            target_name = functions.set_path_filename(self.sds_metadata['eStation2_date'],
                                                      self.sds_metadata['eStation2_product'],
                                                      self.sds_metadata['eStation2_subProduct'],
                                                      self.sds_metadata['eStation2_mapset'],
                                                      self.sds_metadata['eStation2_product_version'],
                                                      '.tif')
            fullpath = target_dir + target_name
            return fullpath
        else:
            logger.warning('File %s does not exist. Exit' % input_file)
            return None

    def get_nodata_value(self, input_file):
        # Given a .GTiff file, reads its metadata and extract NoData value

        # Check the file exists
        if os.path.isfile(input_file):
            try:
                self.read_from_file(input_file)
            except:
                logger.warning('Error in loading from file %s . Exit' % input_file)

            nodata_value = self.sds_metadata['eStation2_nodata']
            return nodata_value
        else:
            logger.warning('File %s does not exist. Exit' % input_file)
            return None

    def get_scaling_values(self, input_file):
        # Given a .GTiff file, reads its metadata and extract NoData value

        # Check the file exists
        if os.path.isfile(input_file):
            try:
                self.read_from_file(input_file)
            except:
                logger.warning('Error in loading from file %s . Exit' % input_file)

            scaling_factor = self.sds_metadata['eStation2_scaling_factor']
            scaling_offset = self.sds_metadata['eStation2_scaling_offset']
            return [float(scaling_factor), float(scaling_offset)]
        else:
            logger.warning('File %s does not exist. Exit' % input_file)
            return None

    def print_out(self):
        # Go through the metadata list and write to std output
        for key, value in list(self.sds_metadata.items()):
            print((key, value))


class GdalInfo(object):

    ######################################################################################
    #   Purpose: returns into a structure the gdalinfo output over the indicated file
    #   Author: Marco Clerici, JRC, European Commission
    #   Date: 2020/04/14
    #   Inputs: file -> the file to parse
    #   Output: structure with gdalinfo output

    def __init__(self):
        DriverShort = ''
        DriverLong = ''
        RasterXSize = 0
        RasterYSize = 0
        RasterCount = 0
        Projection = ''
        GeoTransform = [0,0,0,0,0,0]
        BandMax = 0.0
        BandMin = 0.0
        BandMean = 0.0
        BandStd = 0.0

    def get_gdalinfo(self, filename, stats=True, print_out=False):

        if not os.path.isfile(filename):
            logger.error("File does not exists {}:".format(filename))
            return -1

        # Open the file by using gdal
        dataset = gdal.Open(filename,gdal.GA_ReadOnly)
        if not dataset:
            logger.error("Cannot open dataset in file {}:".format(filename))
            return -1

        # Read number of properties
        self.DriverShort = dataset.GetDriver().ShortName
        self.DriverLong = dataset.GetDriver().LongName
        self.RasterXSize = dataset.RasterXSize
        self.RasterYSize = dataset.RasterYSize
        self.RasterCount = dataset.RasterCount
        self.Projection = dataset.GetProjection()
        self.GeoTransform = dataset.GetGeoTransform()
        band = dataset.GetRasterBand(1)
        # Do not assign stats ... seems they are not realiable computed
        # self.BandMin = band.GetMinimum()
        # self.BandMax = band.GetMaximum()
        # self.BandMean, self.BandStd = band.ComputeBandStats()

        # if not self.BandMin or not self.BandMax:
        #     (self.BandMin,self.BandMax) = band.ComputeRasterMinMax(True)

        if print_out:
            print("Driver: {}/{}".format(dataset.GetDriver().ShortName,
                                        dataset.GetDriver().LongName))
            print("Size is {} x {} x {}".format(dataset.RasterXSize,
                                                dataset.RasterYSize,
                                                dataset.RasterCount))
            print("Projection is {}".format(dataset.GetProjection()))
            print("Origin = ({}, {})".format(self.GeoTransform[0],self. GeoTransform[3]))
            print("Pixel Size = ({}, {})".format(self.GeoTransform[1], self.GeoTransform[5]))

            print("Band Type={}".format(gdal.GetDataTypeName(band.DataType)))

            print("Min={:.3f}, Max={:.3f}".format(self.BandMin,self.BandMax))
            print("Mean={:.3f}, Std={:.3f}".format(self.BandMean,self.BandStd))

        return 0

    def compare_gdalinfo(self, gdal_info):
        equal = True
        # Get  all members
        try:
            my_dict = vars(self)
            other_dict = vars(gdal_info)
            for attr in my_dict:
                if my_dict[attr] != other_dict[attr]:
                    equal = False
        except:
            logger.error("Error in comparing gdal_info")
            equal = False

        return equal
