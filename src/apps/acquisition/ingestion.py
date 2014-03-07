#
#	purpose: Define the ingest service
#	author:  M.Clerici
#	date:	 20.02.2014
#   descr:	 Process input files into the specified 'mapset'
#	history: 1.0
#
#   TODO-M.C.: define an overall ingestion PDL, by considering the various cases identified in 1.X
#   TODO-M.C.: how to manage the writing of several files to the same output ? (e.g. PML Chl or Modis tiles) ?
#
import os, sys, re, signal, commands, datetime, tempfile, re, zipfile
import time, string
from osgeo import osr, gdal

sys.path.append('/srv/www/eStation2/config/')

# eStation2 base definitions
import es2
import zipfile
logger=es2.log.myLogger(__name__)

def driveIngestion():
#   Driver of the ingestion process
#       Reads configuration from the database
#       Reads the list of files existing in input directory
#       Loops over file and call the specific ingestion script
#
    print 'empty'

def ingest(inputfile, outputfile, product, subproducts, mapset, unzip=''):
#   Ingest a single file
#   Arguments:
#       inputfile: input file full name
#       outputfile: output file full name (??)
#       product: product description name (for DB insertions)
#       subproducts: list of subproducts to be extracted from the file. Contains dictionaries such as:
#           sprod={'layer':'layerName','sprod':'subProdname'}
#
#       mapset: output mapset to be applied
#       unzip[option]: either 1 or the zip type ('zip','gzip','bz2')
#
    # Test the file exists
    if os.path.isfile(inputfile) == False:
        logger.error('Input file does not exist')
        return

    # Unzip the file (extract only layers matching subproducts)
    reMatch='.*['
    if isinstance(subproducts,dict):
        # manage the case of 1 element/sprod only in the list
        reMatch=reMatch+subproducts['layer']+'].*'
    else:
        for sprod in subproducts:
            reMatch=reMatch+sprod['layer']
            if sprod !=  subproducts[-1]:
                reMatch=reMatch+'|'
            else:
                reMatch = reMatch+'].*'

    if unzip != '':
        try:
            tmpDir=tempfile.mkdtemp(prefix=__name__, suffix='_'+os.path.basename(inputfile), dir='/tmp/eStation2/')
        except:
            logger.error('Cannot create temporary dir in /tmp/eStation2/. Exit')
            return

        if (unzip == 'zip') or (re.search(inputfile,'.*\.(zip)(ZIP)$')):
            intermFilesList=[]                              # Create an empty list for unzipped files
            if zipfile.is_zipfile(inputfile):
                zFile=zipfile.ZipFile(inputfile)            # Create ZipFile object
                list=zFile.namelist()                       # Get the list of its contents
                for files in list:
                    print files
                    if re.match(reMatch,files):             # Check it matches one of sprods -> extract from zip
                        filename=os.path.basename(files)
                        data=zFile.read(files,tmpDir)
                        myfilePath=os.path.join(tmpDir,filename)
                        myfile = open(myfilePath,"wb")
                        myfile.write(data)
                        myfile.close()
                        intermFilesList.append(myfilePath)
                zFile.close()
                # shutil.rmtree(tmpDir)                     # TEMP !!!????

            else:
                logger.error("File %s is not a valid zipfile. Exit",inputfile)

    for intermFile in intermFilesList:
        # Import CoordSys from fil
        origDs=gdal.Open(intermFile)
        origData = origDs.ReadAsArray()
        origCs=osr.SpatialReference()
        origCs.ImportFromWkt(origDs.GetProjectionRef())

        # Get target SRS from mapset
        # TODO-M.C.: add checks on mapsets
        outCs=mapset.SpatialRef
        outSizeX = mapset.sizeX
        outSizeY = mapset.sizeY

        # Create target in memory
        memDriver = gdal.GetDriverByName('MEM')

        # TODO-M.C.: define output data type by passing an additional argument (or from DB ?)
        outDs = memDriver.Create('',outSizeX, outSizeY, 1, gdal.GDT_Byte)
        outDs.SetGeoTransform(mapset.GeoTransform)
        outDs.SetProjection(outCs.ExportToWkt())

        # Apply Reproject-Image
        res = gdal.ReprojectImage(origDs, outDs, origCs.ExportToWkt(), outCs.ExportToWkt(), gdal.GRA_Bilinear)
        outData = outDs.ReadAsArray()
        # Create and write outputfile
        outDriver = gdal.GetDriverByName("GTiff")
        trgDs = outDriver.CreateCopy(outputfile, outDs, 0)
        trgDs = None

    # TODO-M.C.: upsert into DB (product/subproduct)
    # TODO-M.C.: add Metadata to the ingested file ..consider using
    # trgDs.SetMetadata({'key1':'value1'})

def composeRegions(inputFiles, outputFile, type):
#   Create an output by merging different segments/regions/tiles
#   Arguments:
#       inputfiles: list of input files
#       outputfile: output file
#       type: enumerate indicating the type of files
#           0 - MSG-LRIT
#           1 - MPE (4 segments)
#           2 - LSASAF (Nafr/Safr)
#           3 - MODIS - hv tiles
#

    if type=='MPE':
    # 4 expected segm as input + EPI as [4])
        # Test the file exists
        if os.path.isfile(inputFiles[0]) == False:
            logger.error('Input file does not exist')
            return
    # Create temp output dir
    try:
        print inputFiles[0]
        tmpdir=tempfile.mkdtemp(prefix=__name__, suffix='_'+os.path.basename(inputFiles[0]), dir='/tmp/eStation2/')
    except:
        logger.error('Cannot create temporary dir in /tmp/eStation2/. Exit')
        return

    # Remove small header and concatenate to binary output
    infiles=inputFiles[0:4]
    outTmpGribFile=tmpdir+'/MPE_grib_temp.grb'

    outfid=open(outTmpGribFile,"w")
    for ifile in infiles:
        infid =open(ifile, "r")
        # skip the PK_header (103 bytes)
        infid.seek(103)
        data = infid.read()
        outfid.write(data)
        infid.close()
    outfid.close()

    # Read the file with gdal
    print outTmpGribFile

