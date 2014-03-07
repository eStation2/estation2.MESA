import sys, re, tempfile, zipfile, shutil, os
sys.path.append("os.environ['ESTATION2PATH']")
import ingestion
import es2

testCase='VGT_NDVI'
#testCase='MPE'

# Dummy Definitions
product='myProduct'

# Get target SRS from mapset (now use default one -> ECOWAS)
mapset=es2.mapset()
mapset.assignECOWAS()

if testCase=='VGT_NDVI':

    infilename='V2KRNS10__20130701_NDVI__Africa.ZIP'
    outfilename='20121021_NDWI_ECOWAS.tif'
    reffilename='20121021_NDWI_ECOWAS_ref.tif'

    infile = es2.testDataDirIn+infilename
    outfile = es2.testDataDirOut+outfilename
    reffile = es2.testDataDirRef+reffilename

    if os.path.isfile(outfile):
        print 'Delete file: '+outfile
        os.remove(outfile)
    # Define list of subproducts

    sprod1={'layer':'NDV', 'subproduct':'NDV'}
    sprod2={'layer':'SM', 'subproduct':'SM'}

    subproducts=(sprod1,sprod2)
    # Call ingestion routine
    ingestion.ingest(infile, outfile, product, subproducts, mapset,unzip='zip')

elif testCase=='MPE':

    inputFiles=(es2.testDataDirIn+'L-000-MSG3__-MPEF________-MPEG_____-000001___-201309040800-__',
             es2.testDataDirIn+'L-000-MSG3__-MPEF________-MPEG_____-000002___-201309040800-__',
             es2.testDataDirIn+'L-000-MSG3__-MPEF________-MPEG_____-000003___-201309040800-__',
             es2.testDataDirIn+'L-000-MSG3__-MPEF________-MPEG_____-000004___-201309040800-__',
             es2.testDataDirIn+'L-000-MSG3__-MPEF________-MPEG_____-PRO______-201309040800-__')

    outfilename='201309040800_MPE.tif'
    outfile = es2.testDataDirOut+outfilename

    sprod1={'layer':'MPE', 'subproduct':'MPE'}

    subproducts=(sprod1)

#    ingestion.composeRegions(inputFiles, outfile, 'MPE')
    infile='/tmp/eStation2/ingestionT5NgGz_L-000-MSG3__-MPEF________-MPEG_____-000001___-201309040800-__/MPE_grib_temp.grb'
    ingestion.ingest(infile, outfile, product, subproducts, mapset,unzip='')