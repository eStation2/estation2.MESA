from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
_author__ = "Vijay Charan Venkatachalam"

import os
import lib.python.functions as function


def rename(dir):
    for pathAndFilename in os.listdir(dir):
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))
        yyyymmdd = title[0:8]
        prod_ext =  title[8:44]
        dekad_yyymmdd = function.conv_yyyymmdd_g2_2_yyyymmdd(yyyymmdd)
        #print pathAndFilename +"-=------" +os.path.join(dir, dekad_yyymmdd + prod_ext + ext) #"old: "+pathAndFilename+"new: "+dekad_yyymmdd + prod_ext + ext
        os.rename(os.path.join(dir,pathAndFilename), os.path.join(dir, dekad_yyymmdd + prod_ext + ext))


rename("/data/processing/exchange/DMPv2/dmp/")