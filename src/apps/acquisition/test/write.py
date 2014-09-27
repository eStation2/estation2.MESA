execfile('/srv/www/eStation2/locals.py')
from config.es2 import *
from apps.acquisition.ingestion import *

# Test Writing metadata to an new ext. file
file='/srv/www/eStation2/apps/acquisition/tmp/NDV_Africa_G.tif'
outputfile='test.tif'

out_driver=gdal.GetDriverByName('GTiff')

if 0:
    # Test options in CreateCopy()
    sdsIN=gdal.Open(file)
    trg_ds = out_driver.CreateCopy(outputfile,sdsIN,0, [])

else:
    # Test options in Create()
    sdsIN=gdal.Open(file)
    band = sdsIN.GetRasterBand(1)
    data = band.ReadAsArray(0,0,1000,1000)

    out_driver=gdal.GetDriverByName('GTiff')
    trg_ds = out_driver.Create(outputfile,1000,1000, 1, GDT_Byte, [ 'COMPRESS=LZW' ])
    trg_ds.GetRasterBand(1).WriteArray(data)


