#!/usr/bin/python
#
#   Re-project WBD-GEE monthly to WD-GEE-ECOWAS-AVG mapset
#

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
import glob, os
from lib.python import metadata

input_dir = '/data/processing/wd-gee/1.0/WD-GEE-ECOWAS/tif/occurr/'
output_dir = '/data/processing/wd-gee/1.0/WD-GEE-ECOWAS-AVG/tif/occurr/'
new_mapset = 'WD-GEE-ECOWAS-AVG'
in_files = glob.glob(input_dir+'*.tif')

for file in in_files:

    filename = os.path.basename(file)
    out_filename = filename.replace('WD-GEE-ECOWAS','WD-GEE-ECOWAS-AVG')
    out_filepath = output_dir+out_filename

    # Check the file is not yet there
    if not os.path.isfile(out_filepath):
        # Reproject
        command = 'gdal_translate -of GTIFF -co "compress=LZW" -projwin -17.5290058 27.3132762 24.0006488 4.2682552 ' + file +' '+out_filepath
        os.system(command)
        # Update metadata (mapset)
        sds_meta = metadata.SdsMetadata()

        # Check if the input file is single, or a list
        sds_meta.read_from_file(out_filepath)
        sds_meta.assign_mapset(new_mapset)
        sds_meta.write_to_file(out_filepath)

    else:
        print ('Output file already exists: %s' % out_filename)
