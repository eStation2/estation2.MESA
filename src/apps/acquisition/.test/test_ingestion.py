#
#	purpose: Test the ingest module
#	author:  M. Clerici
#	date:	 26.02.2014
#	history: 1.0
#

import shutil, sys, filecmp, os
from nose import *

sys.path.append("../")
sys.path.append("os.environ['ESTATION2PATH']")
import ingestion
import es2

class test_ingestion():

        # Definitions

        def my_setup_function():
            pass
        def my_teardown_function():
            pass

        @with_setup(my_setup_function, my_teardown_function)

        def test_ingest_VGT(self):

            # Definitions
            infilename='20121021_NDWI.tif'
            outfilename='20121021_NDWI_ECOWAS.tif'
            reffilename='20121021_NDWI_ECOWAS_ref.tif'

            infile = es2.testDataDirIn+infilename
            outfile = es2.testDataDirOut+outfilename
            reffile = es2.testDataDirRef+reffilename

            # Dummy Definitions
            product='myProduct'
            subproduct='mySubProduct'

            # Get target SRS from mapset (now use default one -> ECOWAS)
            mapset=es2.mapset()
            mapset.assignECOWAS()

            # Call ingestion routine
            ingestion.ingest(infile, outfile, product, subproduct, mapset)

            # Compare output file
            assert filecmp.cmp(outfile, reffile)

