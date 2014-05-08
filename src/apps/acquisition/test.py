
execfile('/srv/www/eStation2/locals.py')
from config.es2 import *

from apps.acquisition.ingestion import *

#testCase='VGT_NDVI'
testCase='PML_MODIS_CHL'

# Dummy Definitions

# Get target SRS from mapset (now use default one -> ECOWAS)

if testCase=='PML_MODIS_CHL':

    # Assign Target mapset
    mapset=MapSet()
    mapset.assign_ioc_pml()
    out_driver = gdal.GetDriverByName(ES2_OUTFILE_FORMAT)

    product='PML_MODIS_CHL'
    infilename='PML_EMadagascar_MODIS_oc_3daycomp_20100802_20100804.nc'
    outfilename='20100802_PML_MODIS_CHL_3DAY.tif'
    reffilename='20100802_PML_MODIS_CHL_3DAY_ref.tif'

    infile = 'NETCDF:'+test_data_dir_in+'../tmp/'+infilename+':chlor_a'
    infile = test_data_dir_in+'../tmp/'+infilename
    outfile = test_data_dir_out+outfilename
    reffile = test_data_dir_ref+reffilename

    overall_ds = gdal.Open(infile)
    sds = overall_ds.GetSubDatasets()

    orig_ds=gdal.Open(sds[0][0])

    orig_cs = osr.SpatialReference()
    orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
    orig_geo_transform = orig_ds.GetGeoTransform()
    orig_size_x = orig_ds.RasterXSize
    orig_size_y = orig_ds.RasterYSize

    # Get target SRS from mapset
    out_cs = mapset.spatial_ref
    out_size_x = mapset.size_x
    out_size_y = mapset.size_y

    # Create target in memory
    mem_driver = gdal.GetDriverByName('MEM')

    # Assign mapset to dataset in memory
    mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, GDT_Int16)
    mem_ds.SetGeoTransform(mapset.geo_transform)
    mem_ds.SetProjection(out_cs.ExportToWkt())

    # Apply Reproject-Image to the memory-driver
    res = gdal.ReprojectImage(orig_ds, mem_ds, orig_cs.ExportToWkt(), out_cs.ExportToWkt(),
                                      ES2_OUTFILE_INTERP_METHOD)

    # Read from the dataset in memory
    out_data = mem_ds.ReadAsArray()

    # Apply rescale to data
    #        scaled_data = rescale_data(out_data, in_scale_factor, in_offset, in_nodata, in_mask_min, in_mask_max,
    #                                   out_data_type_numpy, out_scale_factor, out_offset, out_nodata)

    # Create a copy to output_file
    trg_ds = out_driver.CreateCopy(outfile, mem_ds, 0, [ES2_OUTFILE_OPTIONS])
    trg_ds.GetRasterBand(1).WriteArray(out_data)

elif testCase=='VGT_NDVI':

    mapset=MapSet()
    mapset.assign_vgt4africa()

    product='VGT_NDVI'
    infilename='V2KRNS10__20130701_NDVI__Africa.ZIP'
    outfilename='20121021_NDWI_ECOWAS.tif'
    reffilename='20121021_NDWI_ECOWAS_ref.tif'

    infile = es2.test_data_dir_in+infilename
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
    native_mapset=es2.mapset()
    native_mapset.assign_vgt4africa()
    ingest_file(infile, outfile, product, subproducts, mapset,native_mapset=native_mapset, unzip='zip')

elif testCase=='MPE':
    mapset=MapSet()
    mapset.assign_vgt4africa()

    inputFiles=(test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000001___-201309040800-__',
             	test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000002___-201309040800-__',
             	test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000003___-201309040800-__',
             	test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000004___-201309040800-__',
             	test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-PRO______-201309040800-__')

    product='MSG_MPE'
    outfilename='201309040800_MSG_MPE_MPE_native.tif'
    outfile = test_data_dir_out+outfilename

    sprod1={'layer':'MPE', 'subproduct':'MPE'}

    subproducts=(sprod1,0)

	# Note: the grib can be managed by python-gdal already !
    tmp_grib_file=compose_regions('MPE', inputFiles, outfile, 'segments')
    print 'Temp grib file is: ', tmp_grib_file

	# Output mapset not defined: keep original one
    ingest_file(tmp_grib_file, outfile, product, subproducts, mapset='',unzip='')
    print 'Tif output file is: ', outfile

