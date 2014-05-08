#
#	purpose: Define the metadata class
#	author:  M. Clerici
#	date:	 31.03.2014
#   descr:	 Defines members and methods of the metadata class
#
import datetime

# Add:  Units, scaling factor, offset, nodata

sds_metadata = { 'eStation2_product': '',
                 'eStation2_subProduct': '',
                 'eStation2_version': '',
                 'eStation2_es2_version': '',
                 'eStation2_mapset': '',
                 'eStation2_comp_time': '',
                 'eStation2_input_files': '',
                 'eStation2_scaling_factor': '',
                 'eStation2_scaling_offset': '',
                 'eStation2_conversion': '',
                 'eStation2_nodata': ''

}

class SdsMetadata:

    def __init__(self):

        sds_metadata['eStation2_product'] = 'my_product'
        sds_metadata['eStation2_subProduct'] = 'my_sub_product'
        sds_metadata['eStation2_version'] = 'my_product_version'
        sds_metadata['eStation2_es2_version'] = 'my_eStation2_sw_release'
        sds_metadata['eStation2_mapset'] = 'my_mapset_short_name'
        sds_metadata['eStation2_comp_time'] = '2014-01-01 12:00:00'
        sds_metadata['eStation2_input_files'] = '/my/path/to/file/and/filename1'
        sds_metadata['eStation2_scaling_factor'] = 'my_scaling_factor'
        sds_metadata['eStation2_scaling_offset'] = 'my_scaling_offset'
        sds_metadata['eStation2_conversion'] = 'Phys = DN * scaling_factor + scaling_offset'
        sds_metadata['eStation2_nodata'] = 'my_nodata'

    def write_to_ds(self, dataset):
    #
    #   Writes to output file std metadata structure
    #   Args:
    #       dataset: osgeo.gdal dataset (open and georeferenced)

        # Check dataset is open


        # Go through the metadata list and write to sds
        for key, value in sds_metadata.iteritems():
            dataset.SetMetadataItem(key, value)

    def assign_time_now(self):
    #
    #   Assign current time to 'comp_time'

        curr_time=datetime.datetime.now()
        str_datetime=curr_time.strftime("%Y-%m-%d %H:%M:%S")
        sds_metadata['eStation2_comp_time']=str_datetime

    def assign_product(self, product, subproduct, version):
    #
    #   Assign prod/subprod/version
        sds_metadata['eStation2_product'] = str(product)
        sds_metadata['eStation2_subProduct'] = str(subproduct)
        if isinstance(version, str):
            sds_metadata['eStation2_version'] = version
        else:
            sds_metadata['eStation2_version'] = 'undefined'

    def assign_mapset(self, mapset_short_name):
    #
    #   Assign mapset
        sds_metadata['eStation2_mapset'] = str(mapset_short_name)

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

    def assign_scaling(self, scaling_factor, scaling_offset, nodata):
    #
    #   Assign scaling
        sds_metadata['eStation2_scaling_factor'] = str(scaling_factor)
        sds_metadata['eStation2_scaling_offset'] = str(scaling_offset)
        sds_metadata['eStation2_nodata'] = str(nodata)

    def print_out(self):
    #
    #   Writes to std output

        # Go through the metadata list and write to sds
        for key, value in sds_metadata.iteritems():
            print key, value
