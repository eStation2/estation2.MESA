# coding: utf-8
import datetime as dt
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import xarray as xr
from tqdm import tqdm


def _param(ds):
    if 'LAI' in ds.data_vars:
        param = {'product': 'LAI',
                 'short_name': 'leaf_area_index',
                 'long_name': 'Leaf Area Index Resampled 1 Km',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'Missing',
                 'flag_values': '255',
                 'units': '',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 7,
                 'DIGITAL_MAX': 210,
                 'SCALING': 1. / 30,
                 'OFFSET': 0}
        da = ds.LAI

    elif 'FCOVER' in ds.data_vars:
        param = {'product': 'FCOVER',
                 'short_name': 'vegetation_area_fraction',
                 'long_name': 'Fraction of green Vegetation Cover Resampled 1 Km',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'Missing',
                 'flag_values': '255',
                 'units': '',
                 'valid_range': '',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 1.,
                 'DIGITAL_MAX': 250,
                 'SCALING': 1. / 250,
                 'OFFSET': 0}
        da = ds.FCOVER

    elif 'FAPAR' in ds.data_vars:
        param = {'product': 'FAPAR',
                 'short_name': 'Fraction_of_Absorbed_Photosynthetically_Active_Radiation',
                 'long_name': 'Fraction of Absorbed Photosynthetically Active Radiation Resampled 1 KM',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'Missing',
                 'flag_values': '255',
                 'units': '',
                 'valid_range': '',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 0.94,
                 'DIGITAL_MAX': 235,
                 'SCALING': 1. / 250,
                 'OFFSET': 0}
        da = ds.FAPAR

    elif 'NDVI' in ds.data_vars:
        param = {'product': 'NDVI',
                 'short_name': 'Normalized_difference_vegetation_index',
                 'long_name': 'Normalized Difference Vegetation Index Resampled 1 Km',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'Missing cloud snow sea background',
                 'flag_values': '[251 252 253 254 255]',
                 'units': '',
                 'PHYSICAL_MIN': -0.08,
                 'PHYSICAL_MAX': 0.92,
                 'DIGITAL_MAX': 250,
                 'SCALING': 1. / 250,
                 'OFFSET': -0.08}
        da = ds.NDVI

    elif 'DMP' in ds.data_vars:
        param = {'product': 'DMP',
                 'short_name': 'dry_matter_productivity',
                 'long_name': 'Dry matter productivity Resampled 1KM',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'sea',
                 'flag_values': '-2',
                 'units': 'kg / ha / day',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 327.67,
                 'DIGITAL_MAX': 32767,
                 'SCALING': 1. / 100,
                 'OFFSET': 0}
        da = ds.DMP

    elif 'GDMP' in ds.data_vars:
        param = {'product': 'GDMP',
                 'short_name': 'Gross_dry_matter_productivity',
                 'long_name': 'Gross dry matter productivity Resampled 1KM',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'sea',
                 'flag_values': '-2',
                 'units': 'kg / hectare / day',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 655.34,
                 'DIGITAL_MAX': 32767,
                 'SCALING': 1. / 50,
                 'OFFSET': 0}
        da = ds.GDMP

    else:
        sys.exit('GLC product not found please chek')

    return da, param


def _downloader(user, psw, folder):
    url = 'https://land.copernicus.vgt.vito.be/manifest/'

    session = requests.Session()
    session.auth = (user, psw)

    manifest = session.get(url, allow_redirects=True)
    products = pd.read_html(manifest.text)[0][2:-1]['Name']
    products = products[products.str.contains('300_')].reset_index(drop=True)
    print(products)
    val = input('Please select the product from the list:')
    url = f'{url}{products[int(val)]}'

    manifest = session.get(url, allow_redirects=True)
    product = pd.read_html(manifest.text)[0][-2:-1]['Name'].values[0]
    purl = f'{url}{product}'
    r = session.get(purl, stream=True)
    rows = r.text.split('\n')
    dates = pd.DataFrame()
    for line in rows[:-1]:
        r = re.search(r"\d\d\d\d(\/)\d\d(\/)\d\d", line)
        dates = dates.append(pd.DataFrame([line], index=[pd.to_datetime(r[0], format="%Y/%m/%d")]))

    val = input('Please insert the date in teh format YYYY/MM/DD:')

    dates = dates.sort_index()
    i = dates.index.searchsorted(dt.datetime.strptime(val, "%Y/%m/%d"))
    link = dates.iloc[i][0]
    filename = os.path.basename(link)
    if folder != '':
        path = sys.path.join(folder, filename)
    else:
        path = filename

    r = session.get(link, stream=True)

    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    t = tqdm(total=total_size, unit='iB', unit_scale=True)

    with open(path, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    if total_size != 0 and t.n != total_size:
        print("ERROR, something went wrong")

    return path


def _aoi(da, ds, my_ext):
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    def bnd_box_adj(my_ext):
        lat_1k = np.arange(80., -60., -1. / 112)
        lon_1k = np.arange(-180., 180., 1. / 112)

        lat_300 = ds.lat.values
        lon_300 = ds.lon.values
        # (ULX, ULY, LRX, LRY)
        ext_1K = np.zeros(4)

        # Change LR for eStation convention (add half a pixel each side)
        ext_1K[0] = find_nearest(lon_1k, my_ext[0]) - 1. / 224 # ULX
        ext_1K[1] = find_nearest(lat_1k, my_ext[1]) + 1. / 224 # ULY
        # ext_1K[2] = find_nearest(lon_1k, my_ext[2]) - 1. / 224 # LRX original
        # ext_1K[3] = find_nearest(lat_1k, my_ext[3]) + 1. / 224 # LRY original
        ext_1K[2] = find_nearest(lon_1k, my_ext[2]) + 1. / 224 # LRX -> eStation
        ext_1K[3] = find_nearest(lat_1k, my_ext[3]) - 1. / 224 # LRY -> eStation

        # TEMP: expected result: -26.0044643,  38.0044643 60.0044643, -35.0044643

        my_ext[0] = find_nearest(lat_300, ext_1K[0])
        my_ext[1] = find_nearest(lon_300, ext_1K[1])
        my_ext[2] = find_nearest(lat_300, ext_1K[2])
        my_ext[3] = find_nearest(lon_300, ext_1K[3])

        # TEMP: expected result: -26.0044643,  38.0044643 60.0044643, -35.0044643

        return my_ext

    if len(my_ext):
        assert my_ext[1] >= my_ext[3], 'min Latitude is bigger than correspond Max, ' \
                                       'pls change position or check values.'
        assert my_ext[0] <= my_ext[2], 'min Longitude is bigger than correspond Max, ' \
                                       'pls change position or check values.'
        assert ds.lat[-1] <= my_ext[3] <= ds.lat[0], 'min Latitudinal value out of original dataset Max ext.'
        assert ds.lat[-1] <= my_ext[1] <= ds.lat[0], 'Max Latitudinal value out of original dataset Max ext.'
        assert ds.lon[0] <= my_ext[0] <= ds.lon[-1], 'min Longitudinal value out of original dataset Max ext.'
        assert ds.lon[0] <= my_ext[2] <= ds.lon[-1], 'Max Longitudinal value out of original dataset Max ext.'
        adj_ext = bnd_box_adj(my_ext)

        da = da.sel(lon=slice(adj_ext[0], adj_ext[2]), lat=slice(adj_ext[1], adj_ext[3]))
    else:
        da = da.shift(lat=1, lon=1)
    return da


def _date_extr(path):
    _, tail = os.path.split(path)
    pos = [pos for pos, char in enumerate(tail) if char == '_'][2]
    date = tail[pos + 1: pos + 9]
    date_h = pd.to_datetime(date, format = '%Y%m%d')
    return date, date_h


def _resampler(path, my_ext, plot, out_folder):
    # Load the dataset
    ds = xr.open_dataset(path, mask_and_scale=False)

    # select parameters according to the product.
    da, param = _param(ds)
    date, date_h = _date_extr(path)

    # AOI
    da = _aoi(da, ds, my_ext)

    # create the mask according to the fixed values
    da_msk = da.where(da <= param['DIGITAL_MAX'])

    # create the coarsen dataset
    coarsen = da_msk.coarsen(lat=3, lon=3, coord_func=np.mean, boundary='trim', keep_attrs=False).mean()

    # mask the dataset according to the minumum required values
    vo = xr.where(da <= param['DIGITAL_MAX'], 1, 0)
    vo_cnt = vo.coarsen(lat=3, lon=3, coord_func=np.mean, boundary='trim', keep_attrs=False).sum()
    da_r = coarsen.where(vo_cnt >= 5)

    # Add time dimension
    da_r = da_r.assign_coords({'time': date_h})
    da_r = da_r.expand_dims(dim='time', axis=0)

    # Write the output
    da_r.name = param['product']
    da_r.attrs['short_name'] = param['short_name']
    da_r.attrs['long_name'] = param['long_name']
    prmts = dict({param['product']: {'dtype': 'f8', 'zlib': 'True', 'complevel': 4}})

    name = param['product']
    if len(my_ext) != 0:
        file_name = f'CGLS_{name}_{date}_1KM_Resampled_AOI_.nc'
    else:
        file_name = f'CGLS_{name}_{date}_1KM_Resampled_.nc'

    out_file = os.path.join(out_folder, file_name)
    da_r.to_netcdf(out_file, encoding=prmts)

    print(f'{file_name} resampled')

    # Plot
    if plot:
        da_r.plot(robust=True, cmap='YlGn', figsize=(15, 10))
        plt.title(f'Copernicus Global Land\n Resampled {name} to 1K over Europe\n date: {date_h.date()}')
        plt.ylabel('latitude')
        plt.xlabel('longitude')
        plt.draw()
        plt.show()


def main():
    # If the product is locally present fill the path otherwise leave empty
    path = 'd:/Data/CGL_subproject_coarse_res/2019/300/c_gls_NDVI300_201901010000_GLOBE_PROBAV_V1.0.1.nc'

    # define the output folder
    out_folder = 'd:/Data/CGL_subproject_coarse_res/2019/resampled'

    # Define the credential for the Copernicus Global Land repository
    user = ''
    psw = ''

    # Define the AOI (ULX, ULY, LRX, LRY)
    my_ext = [-35.0, 38.0, 60.0, -26.0]
    # my_ext = [-18.58, 62.95, 51.57, 28.5]

    # Plot results
    plot = False

    # Processing
    if path == '':
        # Download and process
        assert user, 'User ID is empty'
        assert psw, 'Password is empty'

        path = _downloader(user, psw, out_folder)
        _resampler(path, my_ext, plot, out_folder)
    elif os.path.isfile(path):
        # Single file process
        _resampler(path, my_ext, plot, out_folder)
    elif os.path.isdir(path):
        # Multiprocessing for local files

        if not os.listdir(path):
            print("Directory is empty")
        else:
            for filename in os.listdir(path):
                if filename.endswith(".nc"):
                    path_ = os.path.join(path, filename)
                    _resampler(path_, my_ext, plot, out_folder)

    print('Conversion done')


if __name__ == '__main__':
    main()