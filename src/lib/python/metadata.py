#
#	purpose: Define the metadata class
#	author:  M. Clerici
#	date:	 31.03.2014
#   descr:	 Defines members and methods of the metadata class
#
import os
import datetime
import os.path
from config import es_constants

from osgeo import gdal
from osgeo import gdalconst
from functions import *

# Import eStation2 modules
from lib.python import es_logging as log
from lib.python import functions
from database import querydb
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
# TODO-M.C.: Is it possible to write to a specific domain (e.g. 'eStation2' ???)
#            FTTB we use the 'eStation2_' prefix

class SdsMetadata:

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
        sds_metadata['eStation2_mac_address'] = get_machine_mac_address()

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
            for key, value in sds_metadata.iteritems():
                dataset.SetMetadataItem(key, str(value))

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
            for key, value in sds_metadata.iteritems():
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
        product_out_info = querydb.get_product_out_info(productcode=product,subproductcode=subproduct,version=version, echo=False)
        product_out_info = functions.list_to_element(product_out_info)

    #   Assign prod/subprod/version
        sds_metadata['eStation2_product'] = str(product)
        sds_metadata['eStation2_subProduct'] = str(subproduct)
        if isinstance(version, str) or isinstance(version, unicode):
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

    def assign_input_files(self, input_files):
    #
    #   Assign input file list
        file_string = ''
        if isinstance(input_files,str):
            file_string+=input_files+';'
        else:
            for ifile in input_files:
                file_string+=ifile+';'
        sds_metadata['eStation2_input_files'] = file_string

    def assign_scaling(self, scaling_factor, scaling_offset, nodata, unit):
    #
    #   Assign scaling
        sds_metadata['eStation2_scaling_factor'] = str(scaling_factor)
        sds_metadata['eStation2_scaling_offset'] = str(scaling_offset)
        sds_metadata['eStation2_nodata'] = str(nodata)
        sds_metadata['eStation2_unit'] = str(unit)

    def get_item(self, itemname):

        value='metadata item not found'
        try:
            value = sds_metadata[itemname]
        except:
            pass

        return value

    def print_out(self):
    #
    #   Writes to std output

        # Go through the metadata list and write to sds
        for key, value in sds_metadata.iteritems():
            print key, value


