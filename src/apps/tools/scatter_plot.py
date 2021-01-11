import numpy as np
import matplotlib.pyplot as plt
from scipy import stats  # , interpolate
from osgeo import gdal

import os

def plot_1o1(data_1, data_2, x_label=None, y_label=None, figure_title=None, png_file=None):
    """
    :param data_1:              -> np.array dataset 1
    :param data_2:              -> np.array dataset 2
    :param x_label:             -> STRING; label for x-axis (typically: Name of dataset-1)
    :param y_label:             -> STRING; label for y-axis (typically: Name of dataset-2)
    :param figure_title:        -> STRING; title to be printed on the canvas
    """
    '''
    ************************************************************
    # Replace no data to nan
    ************************************************************
    '''
    
    
    if np.shape(data_1) != np.shape(data_2):
        raise Exception('Dataset must have te same dimensions')

    '''
    ************************************************************
    # Check the labels (if assigned)
    ************************************************************
    '''
    if x_label is None:
        x_label = 'dataset(1)'

    if y_label is None:
        y_label = 'dataset(2)'

    if figure_title is None:
        figure_title = 'Density Scatter Plot'

    '''
    ***************  SPATIAL CONSISTENCY! **********************
    '''
    sz = data_1.shape
    if len(sz) == 2:
        n_plots = 1
        data_1 = [data_1]
        data_2 = [data_2]
        figure_title = [figure_title]
    else:
        n_plots = sz[0]

    for sp in range(n_plots):
        d1 = data_1[sp]
        d2 = data_2[sp]
        #max_v = 900
        max_v = np.ceil(min(np.nanmax(d1), np.nanmax(d2)))
        min_v = np.round(min(np.nanmin(d1), np.nanmin(d2)))
        #min_v = -100

        mask = d1 + d2
        x_line = d1[~np.isnan(mask)]
        y_line = d2[~np.isnan(mask)]
        xx = np.linspace(min_v, max_v, 10)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_line, y_line)

        slp = np.full_like(xx, fill_value=slope)
        itc = np.full_like(xx, fill_value=intercept)

        line = slp * xx + itc

        rmsd = np.sqrt(np.nansum(np.square(np.array(data_1).flatten() - np.array(data_2).flatten())) /
                       np.count_nonzero(~np.isnan((np.array(data_1) - np.array(data_2)))))

        h, x_edges, y_edges = np.histogram2d(x_line, y_line, bins=150)
        h = np.rot90(h)
        h = np.flipud(h)

        h_mask = np.ma.masked_where(h < 1, h)  # Mask pixels with a value of zero
        # Log
        h_mask = np.log10(h_mask)

        txt_1 = 'Slope=' + str("{:.3f}".format(slope)) + '\n'
        txt_2 = 'Intercept=' + str("{:.3f}".format(intercept)) + '\n'
        txt_3 = 'R$^{2 }$=' + str("{:.3f}".format(r_value ** 2)) + '\n'
        txt_4 = 'RMSD=' + str("{:.3f}".format(rmsd))
        lbl = txt_1 + txt_2 + txt_3 + txt_4

        # color_map = cm.get_cmap('jet')
        plt.figure(figsize=(7, 6), facecolor='w', edgecolor='k')
        plt.grid()

        color_map = plt.cm.get_cmap('jet')

        plt.pcolormesh(x_edges, y_edges, h_mask, cmap=color_map)

        cb = plt.colorbar(aspect=30)  # , ticks=cb_ticks)
        cb.ax.set_ylabel('log$_{10}$(N)', fontsize=12)
        plt.plot(xx, xx, color=[0, 0, 0], ls='-', lw=2, label=None)
        plt.plot(xx, line, color=[1, 0, 1], ls='-', lw=3, label=lbl)
        plt.xlim([min_v, max_v])
        plt.ylim([min_v, max_v])
        cb.ax.tick_params(labelsize=12)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.minorticks_on()
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(figure_title[sp] + '\n', fontsize=14, fontweight='bold')
        plt.legend(loc=2, fontsize=10, numpoints=1, shadow=True)
        plt.grid()
        plt.tight_layout()

        plt.savefig("/data/processing/exchange/"+png_file+".png")
        
        #plt.show()

#ds_1 = gdal.Open("E:\\dev\\Mapplot\\1999-2017\\vgt-ndvi\\10davg-linearx2\\1221_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif")
#data_1 = np.array(ds_1.GetRasterBand(1).ReadAsArray())
#
#ds_2 = gdal.Open("E:\\dev\\Mapplot\\1999-2014\\vgt-ndvi\\10davg-linearx2\\1221_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif")
#data_2 = np.array(ds_2.GetRasterBand(1).ReadAsArray())
#
#data_1 = data_1.astype('float')
#data_2 = data_2.astype('float')
#data_1[data_1==-32768]=np.nan
#data_2[data_2==-32768]=np.nan
#data_1 = np.random.sample((10, 10))
#data_2 = np.random.sample((10, 10))
# M.C. Commented on 21.12.2020
# input_directory = os.fsencode("/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/10davg-linearx2/")
# filename = "test"
# for file in os.listdir(input_directory):
#     filename = os.fsdecode(file)
#     if filename.endswith(".tif") or filename.endswith(".py"):
#         ds_1 = gdal.Open("/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/10davg-linearx2/"+filename)
#         data_1 = np.array(ds_1.GetRasterBand(1).ReadAsArray())
#
#         ds_2 = gdal.Open("/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/10dmax-linearx2/"+filename)
#         data_2 = np.array(ds_2.GetRasterBand(1).ReadAsArray())
#
#         data_1 = data_1.astype('float')
#         data_2 = data_2.astype('float')
#         #
#         data_1[data_1 == -32768] = np.nan
#         data_2[data_2 == -32768] = np.nan
#
#         plot_1o1(data_1, data_2, "1999-2017", "1999-2014", filename)
#
#     else:
#         continue
#plot_1o1(data_1, data_2, "1999-2017", "1999-2014", "Scatterplot - avg")

indir = '/data/processing/exchange/vgt-ndvi/NDVI300/c_gls_NDVI300_202007010000_AFRI_OLCI_V2.0.1/processed/SPOTV-Africa-1km/'
files = [indir+'average_20200701_olci-ndvi_ndv_SPOTV-Africa-1km_V2.0.tif',
         indir+'nearestneighbour_20200701_olci-ndvi_ndv_SPOTV-Africa-1km_V2.0.tif']

ds_1 = gdal.Open(files[0])
data_1 = np.array(ds_1.GetRasterBand(1).ReadAsArray())

ds_2 = gdal.Open(files[1])
data_2 = np.array(ds_2.GetRasterBand(1).ReadAsArray())

data_1 = data_1.astype('float')
data_2 = data_2.astype('float')
#
data_1[data_1 == -32768] = np.nan
data_2[data_2 == -32768] = np.nan

plot_1o1(data_1, data_2, x_label="Average", y_label="Nearest", png_file='NDVI_OLCI_reprojected')

