__author__ = 'venkavi'

#
#  Do 'reading' operations directly h5py library
#
import h5py
import numpy as np
from osgeo import gdal
import os
import time

#input_dir='/data/processing/exchange/Sentinel-3/S3A_OL_2_WRR/S3A_OL_2_WRR____20180305T063241_20180305T071632_20180305T085814_2631_028_291______MAR_O_NR_002.SEN3/'
#output_dir='/data/processing/exchange/Sentinel-3/Outputs/Images/S3A_OL_2_WRR/'
# input_dir='/data/processing/exchange/Sentinel-3/S3A_SL_2_WST/S3A_SL_2_WST____20180413T053236_20180413T053536_20180413T071229_0179_030_076_4860_MAR_O_NR_003.SEN3/'
# output_dir='/data/processing/exchange/Sentinel-3/Outputs/Images/S3A_SL_2_WST/'
#
#
# band='20180413053236-MAR-L2P_GHRSST-SSTskin-SLSTRA-20180413071229-v02.0-fv01.0.nc'
# geo='20180413053236-MAR-L2P_GHRSST-SSTskin-SLSTRA-20180413071229-v02.0-fv01.0.nc'
#
# # 1. Read coordinates, do stats and write geotiff
#
# filename=input_dir+geo
# fd=h5py.File(filename,'r')
#
# #ds=fd['latitude']
# ds=fd['lat']
# data_read64=np.zeros(ds.shape,dtype=float)
# ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
# latitude=ds.value
# #latitude=np.flip(ds.value, 0)
# #latitude=np.flipud(ds.value)
# print 'The min/avg/max for latitude in {} are: {}/{}/{}'.format(geo, np.min(latitude),np.mean(latitude),np.max(latitude))
#
# output_file = output_dir+'latitude.tif'
# output_driver = gdal.GetDriverByName('GTiff')
# orig_size_x = latitude.shape[1]
# orig_size_y = latitude.shape[0]
# in_data_type= gdal.GDT_Float32
# output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
# output_ds.GetRasterBand(1).WriteArray(latitude)
# output_ds = None
#
# ds=fd['lon']
# #ds=fd['longitude']
# data_read64=np.zeros(ds.shape,dtype=float)
# ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
# #longitude=ds.value/1000000.0
# #longitude=np.fliplr(ds.value)
# #longitude=np.flip(ds.value, 0)
# longitude=ds.value
# print 'The min/avg/max for longitude in {} are: {}/{}/{}'.format(geo, np.min(longitude),np.mean(longitude),np.max(longitude))
#
# output_file = output_dir+'longitude.tif'
# output_driver = gdal.GetDriverByName('GTiff')
# orig_size_x = longitude.shape[1]
# orig_size_y = longitude.shape[0]
# in_data_type= gdal.GDT_Float32
# output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
# output_ds.GetRasterBand(1).WriteArray(longitude)
# output_ds = None
#
# fd.close()

# # 2. Read band
# filename = input_dir + band
# fd = h5py.File(filename, 'r')
#
# ds = fd['Oa01_reflectance']
# data_read64 = np.zeros(ds.shape, dtype=float)
# ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
# reflectance = ds.value
# print 'The min/avg/max for reflectance in {} are: {}/{}/{}'.format(geo, np.min(reflectance), np.mean(reflectance),
#                                                                    np.max(reflectance))
#
# output_file = output_dir + 'reflectance.tif'
# output_driver = gdal.GetDriverByName('GTiff')
# orig_size_x = reflectance.shape[1]
# orig_size_y = reflectance.shape[0]
# in_data_type = gdal.GDT_Float32
# output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
# output_ds.GetRasterBand(1).WriteArray(reflectance)
#
# output_ds = None
# time.sleep(20)
# # 3. Reproject to lat/long
# #    gdalwarp: -te xmin ymin xmax ymax [-tr xres yres] [-ts width height]
#
# # lat:  60.0 to 65.0
# # long: 47.0 to 73.0
#
# lon_min = np.min(longitude)
# lat_min = np.min(latitude)
# lon_max = np.max(longitude)
# lat_max = np.max(latitude)
# x_size = 0.00892857
# y_size = 0.00892857
# input_vrt = output_dir + 'SA3.vrt'
# output_tif = output_dir + 'Oa01_reflectance.tif'
#
# command = 'gdalwarp -te {} {} {} {} -s_srs "epsg:4326" -tr {} {} -r near -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
#     lon_min, lat_min, lon_max, lat_max, x_size, y_size, input_vrt, output_tif)
#
# print(command)
# os.system(command)

def pre_process_slstr_sst(subproducts=None, input_file=None, output_dir=None, input_dir=None):
    #check whether subproduct list is empty
    if not subproducts:
        return

    # 1. Read coordinates, do stats and write geotiff
    filename = input_dir + input_file
    fd = h5py.File(filename, 'r')

    ds = fd['lat']
    data_read64 = np.zeros(ds.shape, dtype=float)
    ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
    latitude = ds.value
    print 'The min/avg/max for latitude in {} are: {}/{}/{}'.format(input_file, np.min(latitude), np.mean(latitude),
                                                                    np.max(latitude))

    output_file = output_dir + 'latitude.tif'
    output_driver = gdal.GetDriverByName('GTiff')
    orig_size_x = latitude.shape[1]
    orig_size_y = latitude.shape[0]
    in_data_type = gdal.GDT_Float32
    output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
    output_ds.GetRasterBand(1).WriteArray(latitude)
    output_ds = None

    ds = fd['lon']
    data_read64 = np.zeros(ds.shape, dtype=float)
    ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
    longitude = ds.value
    print 'The min/avg/max for longitude in {} are: {}/{}/{}'.format(input_file, np.min(longitude), np.mean(longitude),
                                                                     np.max(longitude))
    output_file = output_dir + 'longitude.tif'
    output_driver = gdal.GetDriverByName('GTiff')
    orig_size_x = longitude.shape[1]
    orig_size_y = longitude.shape[0]
    in_data_type = gdal.GDT_Float32
    output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
    output_ds.GetRasterBand(1).WriteArray(longitude)
    output_ds = None
    del output_ds

    for sprod in subproducts:
        # 2. Read band
        ds = fd[sprod]
        data_read64 = np.zeros(ds.shape, dtype=float)
        ds.id.read(h5py.h5s.ALL, h5py.h5s.ALL, data_read64, mtype=h5py.h5t.NATIVE_DOUBLE)
        seasurfacetemp = ds.value
        print 'The min/avg/max for seasurfacetemp in {} are: {}/{}/{}'.format(input_file, np.min(seasurfacetemp), np.mean(seasurfacetemp),
                                                                           np.max(seasurfacetemp))

        un_proj_filename = sprod + '_un_proj.tif'
        output_file = output_dir + un_proj_filename
        output_driver = gdal.GetDriverByName('GTiff')
        orig_size_x = seasurfacetemp.shape[2]
        orig_size_y = seasurfacetemp.shape[1]
        in_data_type = gdal.GDT_Float32
        output_ds = output_driver.Create(output_file, orig_size_x, orig_size_y, 1, in_data_type)
        for i, image in enumerate(seasurfacetemp, 1):
            #image_inverted = np.flip(image, 0)
            output_ds.GetRasterBand(i).WriteArray(image)
        #output_ds.GetRasterBand(1).WriteArray(seasurfacetemp)
        output_ds = None
        del output_ds

        # 3. Reproject to lat/long
        lon_min = np.min(longitude)
        lat_min = np.min(latitude)
        lon_max = np.max(longitude)
        lat_max = np.max(latitude)
        x_size = 0.00892857
        y_size = 0.00892857

        #Create vrt file
        write_vrt(un_proj_filename=un_proj_filename, rasterXSize=orig_size_x, rasterYSize=orig_size_y, output_dir=output_dir)

        #TODO search vrt file in the tmp folder
        input_vrt = output_dir + 'seasurfacetemp.vrt'
        output_tif = output_dir + sprod + '.tif'

        command = 'gdalwarp -dstnodata "-32768" -te {} {} {} {} -s_srs "epsg:4326" -tr {} {} -r near -t_srs "+proj=longlat +datum=WGS84" -ot Float32 {} {}'.format(
            lon_min, lat_min, lon_max, lat_max, x_size, y_size, input_vrt, output_tif)

        print(command)
        os.system(command)

        fd.close()

#gdalwarp -te 47.0 60.0 73.0 65.0 -s_srs "epsg:4326" -tr 0.00892857 0.00892857 -r near -t_srs "+proj=longlat +datum=WGS84" ${output_dir}SA3.vrt ${output_dir}${band}_gdalwarp_tr.tif



def write_vrt(un_proj_filename=None, rasterXSize=None, rasterYSize=None, output_dir=None):
    # Write the 'vrt' file
    file_vrt = output_dir + 'seasurfacetemp.vrt'
    un_proj_filepath = output_dir + un_proj_filename
    with open(file_vrt,'w') as outFile:
        # outFile.write('<VRTDataset rasterXSize="1217" rasterYSize="14952" rasterXSize="1217" rasterYSize="14952">\n')
        # outFile.write('    <Metadata domain="GEOLOCATION">\n')
        # outFile.write('        <MDI key="X_DATASET">'+output_dir+'longitude.tif</MDI>\n')
        # outFile.write('        <MDI key="X_BAND">1</MDI>\n')
        # outFile.write('        <MDI key="Y_DATASET">'+output_dir+'latitude.tif</MDI>\n')
        # outFile.write('        <MDI key="Y_BAND">1</MDI>\n')
        # outFile.write('        <MDI key="PIXEL_OFFSET">0</MDI>\n')
        # outFile.write('        <MDI key="LINE_OFFSET">0</MDI>\n')
        # outFile.write('        <MDI key="PIXEL_STEP">1</MDI>\n')
        # outFile.write('        <MDI key="LINE_STEP">1</MDI>\n')
        # outFile.write('    </Metadata>\n')
        # outFile.write('    <VRTRasterBand dataType="UInt16" band="1">\n')
        # outFile.write('        <Metadata>\n')
        # outFile.write('            <MDI key="add_offset">0</MDI>\n')
        # outFile.write('            <MDI key="ancillary_variables">Oa01_radiance_err</MDI>\n')
        # outFile.write('            <MDI key="coordinates">time_stamp altitude latitude longitude</MDI>\n')
        # outFile.write('            <MDI key="long_name">TOA radiance for OLCI acquisition band Oa01</MDI>\n')
        # outFile.write('            <MDI key="NETCDF_VARNAME">Oa01_radiance</MDI>\n')
        # outFile.write('            <MDI key="scale_factor">0.01394646</MDI>\n')
        # outFile.write('            <MDI key="standard_name">toa_upwelling_spectral_radiance</MDI>\n')
        # outFile.write('            <MDI key="units">mW.m-2.sr-1.nm-1</MDI>\n')
        # outFile.write('            <MDI key="valid_max">65534</MDI>\n')
        # outFile.write('            <MDI key="valid_min">0</MDI>\n')
        # outFile.write('            <MDI key="_FillValue">65535</MDI>\n')
        # outFile.write('        </Metadata>\n')
        # outFile.write('        <NoDataValue>65535</NoDataValue>\n')
        # outFile.write('        <UnitType>mW.m-2.sr-1.nm-1</UnitType>\n')
        # outFile.write('        <Scale>0.01394645962864161</Scale>\n')
        # outFile.write('        <SimpleSource>\n')
        # outFile.write('            <MDI key="LINE_STEP">1</MDI>\n')
        # outFile.write('            <SourceFilename>'+un_proj_filepath+'</SourceFilename>\n')
        # outFile.write('            <SourceBand>1</SourceBand>\n')
        # outFile.write('        </SimpleSource>\n')
        # outFile.write('    </VRTRasterBand>\n')
        # outFile.write('</VRTDataset>\n')
        outFile.write('<VRTDataset rasterXSize="'+str(rasterXSize)+'" rasterYSize="'+str(rasterYSize)+'">\n')
        outFile.write('    <Metadata domain="GEOLOCATION">\n')
        outFile.write('        <MDI key="X_DATASET">'+output_dir+'longitude.tif</MDI>\n')
        outFile.write('        <MDI key="X_BAND">1</MDI>\n')
        outFile.write('        <MDI key="Y_DATASET">'+output_dir+'latitude.tif</MDI>\n')
        outFile.write('        <MDI key="Y_BAND">1</MDI>\n')
        outFile.write('        <MDI key="PIXEL_OFFSET">0</MDI>\n')
        outFile.write('        <MDI key="LINE_OFFSET">0</MDI>\n')
        outFile.write('        <MDI key="PIXEL_STEP">1</MDI>\n')
        outFile.write('        <MDI key="LINE_STEP">1</MDI>\n')
        outFile.write('    </Metadata>\n')
        outFile.write('    <VRTRasterBand dataType="Int16" band="1">\n')
        outFile.write('        <Metadata />\n')
        outFile.write('        <SimpleSource>\n')
        outFile.write('            <MDI key="LINE_STEP">1</MDI>\n')
        outFile.write('            <SourceFilename>'+un_proj_filepath+'</SourceFilename>\n')
        outFile.write('            <SourceBand>1</SourceBand>\n')
        outFile.write('        </SimpleSource>\n')
        outFile.write('    </VRTRasterBand>\n')
        outFile.write('</VRTDataset>\n')

def test_pre_process_slstr_sst():
    input_dir = '/data/processing/exchange/Sentinel-3/S3A_SL_2_WST/S3A_SL_2_WST____20180413T053236_20180413T053536_20180413T071229_0179_030_076_4860_MAR_O_NR_003.SEN3/'
    output_dir = '/data/processing/exchange/Sentinel-3/Outputs/Images/S3A_SL_2_WST/'
    for file in os.listdir(input_dir):

        #TODO check for the bounding box from xfdumanifest.xml

        if file.endswith(".nc"):
            pre_process_slstr_sst(subproducts=['sea_surface_temperature'], input_file=file,
                                  output_dir=output_dir, input_dir=input_dir)
        else:
            continue


test_pre_process_slstr_sst()