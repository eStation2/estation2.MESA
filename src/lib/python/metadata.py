from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Define the metadata class
#	author:  M. Clerici
#	date:	 31.03.2014
#   descr:	 Defines members and methods of the metadata class
#
from future import standard_library
standard_library.install_aliases()
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
from database import querydb_meta
logger = log.my_logger(__name__)

# TODO-M.C.: Add all the attributes of 'mapset' and 'category_id' ? so that the contents of the db tables can be created (if not existing on the target station) from metadata ?

sds_metadata = { 'eStation2_es2_version': '',               # 0. eStation 2 version (the fields below might depend on es2_version)

                                                            # ------------------  Mapset        ----------------------
                 'eStation2_mapset': '',                    # 1. Mapsetcode

                                                            # ------------------  As in the 'product' table ----------------------
                 'eStation2_product': '',                   # 2. productcode
                 'eStation2_subProduct': '',                # 3. subproductcode
                 'eStation2_product_version': '',           # 4. product version (e.g. MODIS Collection 4 or 5; by default is undefined -> '')

                 'eStation2_defined_by': '',                # 5. JRC or User
                 'eStation2_category': '',                  # 6. Product category (TODO-M.C.: double-check wrt INSPIRE)
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
        sds_metadata['eStation2_comp_time'] = 'Undefined'
        sds_metadata['eStation2_mac_address'] = get_machine_mac_address()

        sds_metadata['eStation2_parameters'] = 'None'

    def write_to_ds(self, dataset):
    #
    #   Writes  metadata to a target dataset (already opened gdal dataset)
    #   Args:
    #       dataset: osgeo.gdal dataset (open and georeferenced)

        # Check argument ok
        if not isinstance(dataset,gdal.Dataset):
            logger.error('The argument should be an open GDAL Dataset. Exit')
        else:
            # Go through the metadata list and write to sds
            for key, value in list(sds_metadata.items()):
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
             logger.error('Output file does not exist %s' % filepath)
        else:
            # Open output file
            sds = gdal.Open(filepath, gdalconst.GA_Update)
            self.write_to_ds(sds)

    def read_from_ds(self, dataset):
    #
    #   Read metadata structure from an opened file
    #   Args:
    #       dataset: osgeo.gdal dataset (open and georeferenced)

        # Check argument ok
        if not isinstance(dataset,gdal.Dataset):
            logger.error('The argument should be an open GDAL Dataset. Exit')
        else:

            # Go through the metadata list and write to sds
            for key, value in list(sds_metadata.items()):
                try:
                    value = dataset.GetMetadataItem(key)
                    sds_metadata[key] = value
                except:
                    sds_metadata[key] = 'Not found in file'
                    logger.error('Error in reading metadata item %s' % key)

    def read_from_file(self, filepath):
    #
    #   Read metadata structure from a source file
    #   Args:
    #       filepath: full file path (dir+name)

        # Check the file exists
        if not os.path.isfile(filepath):
            logger.error('Input file does not exist %s' % filepath)
        else:
            # Open it and read metadata
            infile=gdal.Open(filepath)
            self.read_from_ds(infile)

            # Close the file
            infile= None

    def assign_es2_version(self):
    #
    #   Assign the es2_version
        sds_metadata['eStation2_es2_version'] = es_constants.es2_sw_version

    def assign_comput_time_now(self):
    #
    #   Assign current time to 'comp_time'

        curr_time=datetime.datetime.now()
        str_datetime=curr_time.strftime("%Y-%m-%d %H:%M:%S")
        sds_metadata['eStation2_comp_time']=str_datetime

    def assign_from_product(self, product, subproduct, version):
    #
        try:
            product_out_info = querydb_meta.get_product_out_info(productcode=product,subproductcode=subproduct,version=version)
        except:
            logger.error('The product is not defined in the DB')
            return 1

        product_out_info = functions.list_to_element(product_out_info)

    #   Assign prod/subprod/version
        sds_metadata['eStation2_product'] = str(product)
        sds_metadata['eStation2_subProduct'] = str(subproduct)
        if isinstance(version, str) or isinstance(version, str):
            sds_metadata['eStation2_product_version'] = version
        else:
            sds_metadata['eStation2_product_version'] = 'undefined'

        sds_metadata['eStation2_defined_by'] = product_out_info.defined_by
        sds_metadata['eStation2_category'] = product_out_info.category_id
        sds_metadata['eStation2_descr_name'] = product_out_info.descriptive_name
        sds_metadata['eStation2_description'] = product_out_info.description
        sds_metadata['eStation2_provider'] = product_out_info.provider
        sds_metadata['eStation2_date_format'] = product_out_info.date_format
        sds_metadata['eStation2_frequency'] = product_out_info.frequency_id
        sds_metadata['eStation2_scaling_factor'] = product_out_info.scale_factor
        sds_metadata['eStation2_scaling_offset'] = product_out_info.scale_offset
        sds_metadata['eStation2_unit'] = product_out_info.unit
        sds_metadata['eStation2_nodata'] = product_out_info.nodata

    def assign_product_elemets(self, product, subproduct, version):
    #
    #   Assign prod/subprod/version
        sds_metadata['eStation2_product'] = str(product)
        sds_metadata['eStation2_subProduct'] = str(subproduct)

        if isinstance(version, str) or isinstance(version, str):
            sds_metadata['eStation2_product_version'] = version
        else:
            sds_metadata['eStation2_product_version'] = 'undefined'

    def assign_date(self, date):
    #
    #   Assign date of the product
        sds_metadata['eStation2_date'] = str(date)

    def assign_mapset(self, mapset_code):
    #
    #   Assign mapset
        sds_metadata['eStation2_mapset'] = str(mapset_code)

    def assign_subdir_from_fullpath(self, full_directory):
    #
    #   Assign subdir
        subdir = functions.get_subdir_from_path_full(full_directory)
        sds_metadata['eStation2_subdir'] = str(subdir)

    def assign_subdir(self, subdirectory):
    #
    #   Assign subdir
        sds_metadata['eStation2_subdir'] = str(subdirectory)

    def assign_input_files(self, input_files):
    #
    #   Assign input file list
        file_string = ''
        if isinstance(input_files,basestring):
            file_string+=os.path.basename(input_files)+';'
        else:
            for ifile in input_files:
                file_string+=os.path.basename(ifile)+';'
        sds_metadata['eStation2_input_files'] = file_string

    def merge_input_file_lists(self, old_list, input_files):
    #
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
    #
    #   Assign scaling
        sds_metadata['eStation2_scaling_factor'] = str(scaling_factor)
        sds_metadata['eStation2_scaling_offset'] = str(scaling_offset)
        sds_metadata['eStation2_nodata'] = str(nodata)
        sds_metadata['eStation2_unit'] = str(unit)

    def assign_nodata(self, nodata):
    #
    #   Assign scaling
        sds_metadata['eStation2_nodata'] = str(nodata)

    def assign_single_paramater(self, parameter_key, parameter_value):
    # ES2-293 ES2-292
    #   Assign Single Parameter
        sds_metadata[parameter_key] = str(parameter_value)

    def assign_scl_factor(self, scl_factor):
    #
    #   Assign scaling
        sds_metadata['eStation2_scaling_factor'] = str(scl_factor)

    def assign_parameters(self, parameters):
    #
    #   Assign parameters (defined specifically for SST-FRONTS detection)
        parameters_string=''
        for key, value in sorted(parameters.items()):
            parameters_string+='{}={}; '.format(key,value)

        sds_metadata['eStation2_parameters'] = parameters_string


    def get_item(self, itemname):

        value='metadata item not found'
        try:
            value = sds_metadata[itemname]
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

            target_subdir = sds_metadata['eStation2_subdir']
            target_dir=es_constants.es2globals['processing_dir']+target_subdir
            target_name=functions.set_path_filename(sds_metadata['eStation2_date'],
                                                    sds_metadata['eStation2_product'],
                                                    sds_metadata['eStation2_subProduct'],
                                                    sds_metadata['eStation2_mapset'],
                                                    sds_metadata['eStation2_product_version'],
                                                    '.tif')
            fullpath = target_dir+target_name
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

            nodata_value = sds_metadata['eStation2_nodata']
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

            scaling_factor = sds_metadata['eStation2_scaling_factor']
            scaling_offset = sds_metadata['eStation2_scaling_offset']
            return [float(scaling_factor), float(scaling_offset)]
        else:
            logger.warning('File %s does not exist. Exit' % input_file)
            return None

    def print_out(self):
    #
    #   Writes to std output

        # Go through the metadata list and write to sds
        for key, value in list(sds_metadata.items()):
            print((key, value))


