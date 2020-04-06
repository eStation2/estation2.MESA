from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library

import os
import lib.python.functions as function

standard_library.install_aliases()
_author__ = "Vijay Charan Venkatachalam"


def rename(sourcedir):
    for pathAndFilename in os.listdir(sourcedir):
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))
        yyyymmdd = title[0:8]
        prod_ext = title[8:44]
        dekad_yyymmdd = function.conv_yyyymmdd_g2_2_yyyymmdd(yyyymmdd)
        # print pathAndFilename +"-=------" +os.path.join(dir, dekad_yyymmdd + prod_ext + ext)
        # #"old: "+pathAndFilename+"new: "+dekad_yyymmdd + prod_ext + ext
        os.rename(os.path.join(sourcedir, pathAndFilename), os.path.join(sourcedir, dekad_yyymmdd + prod_ext + ext))


rename("/data/processing/exchange/DMPv2/dmp/")
