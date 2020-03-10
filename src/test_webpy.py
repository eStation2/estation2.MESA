from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import str
_author__ = "Jurriaan van 't Klooster"

from config import es_constants
# from apps.productmanagement.datasets import Dataset
# from apps.productmanagement.products import Product
# from lib.python import functions
# from database import querydb
import unittest
# import datetime
import webpy_esapp_helpers
# import webpy_esapp
from database import crud

# TODO: The plotly.plotly module is deprecated, please install the chart-studio package and use the chart_studio.plotly module instead.
import plotly as py
# from plotly.graph_objs import *

import io
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import base64

from lib.python import es_logging as log

logger = log.my_logger(__name__)


class TestWebpy(unittest.TestCase):

    def test_checkCreateSubproductDir(self):
        # productcode = 'vgt-ndvi'
        # version = 'sv2-pv2.2'

        productcode = 'lsasaf-et'
        version = 'undefined'

        webpy_esapp_helpers.checkCreateSubproductDir(productcode, version)
        self.assertEqual(1, 1)

    def test_DeleteProduct(self):
        getparams = {
            'productcode': 'jur3',
            'version': 'v1.1'
        }
        deletestatus = webpy_esapp_helpers.DeleteProduct(productcode=getparams['productcode'],
                                                         version=getparams['version'])
        print(deletestatus)
        self.assertEqual(1, 1)

    def test_exportLegend(self):
        params = {
            'task': 'exportLegend',
            'legendid': 214,
            'legendname': 'CHLA Value -  36 steps, 0 to 10'
        }
        filename = webpy_esapp_helpers.ExportLegend(params)
        print(filename)
        self.assertEqual(1, 1)

    def test_GetLogos(self):
        logos_json = webpy_esapp_helpers.GetLogos()
        return logos_json

    def test_IngestArchive(self):
        params = {
            'task': 'run',
            'service': 'ingestarchive'
        }
        result = webpy_esapp_helpers.IngestArchive(params)

        self.assertEqual(1, 1)

    def test_UpdateProduct(self):
        productcode = 'vgt-lai'
        version = 'V2.0'
        updatestatus = webpy_esapp_helpers.UpdateProduct(productcode=productcode, version=version, activate=True)

        return updatestatus

    def test_UpdateUserSettings(self):

        params = {
            'systemsettings': {
                'active_version': "2.1.2",
                'archive_dir': "/data/archives/",
                'base_dir': "/srv/www/eStation2",
                'base_tmp_dir': "/tmp/eStation2",
                'current_mode': "Recovery",
                'data_dir': "/dataxxx",
                'dbname': "d6estation2",
                'dbpass': "Mk44t*Gw!FJP",
                'dbuser': "d6estation2",
                'default_language': "eng",
                'eumetcast_files_dir': "/eumetcast/",
                'get_eumetcast_output_dir': "/data/ingest/",
                'get_internet_output_dir': "/data/ingest/",
                'host': "pgsql96-srv1.jrc.org",
                'id': 0,
                'ingest_dir': "/data/ingest/",
                'log_general_level': "INFO",
                'loglevel': "INFO",
                'port': "5432",
                'processing_dir': "/data/processing/",
                'proxy': "http://10.168.209.73:8012",
                'role': "PC2",
                'static_data_dir': "/data/static_data/",
                'thema': "JRC",
                'type_installation': "Full"
            }
        }

        updatestatus = webpy_esapp_helpers.UpdateUserSettings(params)
        self.assertEqual(1, 1)

    def test_getRunningRequestJobs(self):
        response_json = webpy_esapp_helpers.getRunningRequestJobs()
        self.assertEqual(1, 1)

    def test_pausesRequestJob(self):
        # requestid = 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_vci-linearx2_dataset'
        # requestid = 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_10davg-linearx2_dataset'
        requestid = 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_mapset'

        result = webpy_esapp_helpers.pauseRequestJob(requestid)
        result = webpy_esapp_helpers.statusRequestJob(requestid)

        self.assertEqual(1, 1)

    def test_restartRequestJob(self):
        # requestid = 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_vci-linearx2_dataset'
        requestid = 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_linearx2diff-linearx2_dataset'

        result = webpy_esapp_helpers.restartRequestJob(requestid)
        result = webpy_esapp_helpers.statusRequestJob(requestid)

        self.assertEqual(1, 1)

    def test_statusRequestJob(self):
        # requestid = 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_vci-linearx2_dataset'
        # requestid = 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_10davg-linearx2_dataset'
        requestid = 'vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_mapset'

        result = webpy_esapp_helpers.statusRequestJob(requestid)

        self.assertEqual(1, 1)

    def test_createRequestJob(self):
        params = {
            'level': 'dataset',
            'productcode': 'vgt-ndvi',
            'version': 'sv2-pv2.2',
            'subproductcode': '1monmin',
            'mapsetcode': 'SPOTV-IGAD-1km'
        }

        result = webpy_esapp_helpers.createRequestJob(params)

        self.assertEqual(1, 1)

    def test_scatterTimeseries(self):

        params = {
            'userid': 'jurvtk',
            'istemplate': 'false',
            'graph_tpl_id': -1,
            'graph_tpl_name': 'default',
            'graphtype': 'scatter',
            'selectedTimeseries': '[{"productcode": "vgt-ndvi", "version": "sv2-pv2.2", "subproductcode": "ndvi-linearx2",' + \
                                  '"mapsetcode": "SPOTV-Africa-1km", "date_format": "YYYYMMDD",' + \
                                  '"frequency_id": "e1dekad", "cumulative": false, "difference": false,' + \
                                  '"reference": false, "colorramp": false, "legend_id": null, "zscore": false}]',
            'tsdrawprops': '[{"productcode": "vgt-ndvi", "subproductcode": "ndvi-linearx2", "version": "sv2-pv2.2",' + \
                           '"tsname_in_legend": "VGT 10 Day NDVI Filtered", "charttype": "line", "color": "#008000",' + \
                           '"linestyle": "Solid", "linewidth": 4, "yaxe_id": "ndvi"}]',
            'yAxes': None,
            'yearTS': None,
            'tsFromPeriod': '20180101',
            'tsToPeriod': '20180111',
            'yearsToCompare': None,
            'tsFromSeason': None,
            'tsToSeason': None,
            'WKT': 'POLYGON((34.59220000000096 -7.995099999998274, 34.59194000000207 -7.996689999998125, 34.58456000000115 -7.998529999998937, 34.580260000000635 -8.012669999998252, 34.576570000001084 -8.005299999998897, 34.56612000000132 -8.01328999999896, 34.56059000000096 -8.021889999998166, 34.56059000000096 -8.024349999997867, 34.555060000000594 -8.021279999999024, 34.5483000000022 -8.017589999997654, 34.54276000000209 -8.013899999998102, 34.539080000002286 -8.013899999998102, 34.53108000000066 -8.018819999999323, 34.530470000001515 -8.020659999998315, 34.52494000000115 -8.018199999998615, 34.51264000000083 -8.016359999997803, 34.505270000001474 -8.016969999998764, 34.49851000000126 -8.020049999999173, 34.494200000001 -8.015749999998661, 34.486830000001646 -8.015129999997953, 34.48375000000124 -8.018819999999323, 34.47638000000188 -8.024349999997867, 34.46470000000227 -8.028649999998379, 34.447180000001026 -8.032649999999194, 34.43919000000096 -8.031419999999343, 34.43427000000156 -8.033259999998336, 34.43489000000227 -8.040029999998296, 34.4287400000012 -8.040029999998296, 34.419520000001285 -8.040639999999257, 34.41030000000137 -8.04862999999932, 34.40046000000075 -8.049859999999171, 34.393700000002354 -8.049859999999171, 34.388780000001134 -8.0437099999981, 34.38079000000107 -8.041259999998147, 34.370340000001306 -8.041259999998147, 34.3642000000018 -8.044329999998808, 34.36235000000124 -8.04801999999836, 34.35498000000189 -8.05047999999806, 34.34698000000208 -8.049859999999171, 34.34084000000075 -8.049859999999171, 34.33592000000135 -8.049859999999171, 34.33531000000221 -8.056009999998423, 34.33838000000105 -8.058469999998124, 34.33285000000069 -8.059699999997974, 34.32916000000114 -8.068919999997888, 34.33100000000195 -8.079979999998613, 34.32670000000144 -8.078749999998763, 34.326090000002296 -8.079369999997652, 34.319940000001225 -8.085509999998976, 34.319940000001225 -8.089199999998527, 34.322400000000926 -8.094119999997929, 34.31502000000182 -8.09595999999874, 34.30887000000075 -8.091659999998228, 34.30887000000075 -8.082439999998314, 34.3084400000007 -8.077269999997952, 34.30826000000161 -8.077519999998913, 34.30211000000236 -8.06952999999885, 34.29719000000114 -8.065229999998337, 34.296580000001995 -8.04678999999851, 34.290430000000924 -8.033879999999044, 34.28675000000112 -8.031419999999343, 34.28367000000071 -8.021579999998721, 34.27568000000065 -8.008679999999003, 34.2744500000008 -7.99514999999883, 34.268300000001545 -7.987159999998767, 34.26400000000103 -7.975479999999152, 34.25601000000097 -7.952129999997851, 34.246790000001056 -7.936139999997977, 34.23880000000099 -7.912779999998747, 34.22896000000219 -7.89556999999877, 34.224050000000716 -7.880209999999352, 34.217900000001464 -7.868529999997918, 34.20438000000104 -7.861149999998816, 34.176720000001296 -7.867299999998068, 34.12385000000177 -7.878359999998793, 34.05193000000145 -7.89618999999766, 33.948050000000876 -7.9213899999977, 33.93514000000141 -7.924459999998362, 33.86599000000206 -7.935839999998279, 33.86599000000206 -7.931919999999082, 33.86599000000206 -7.915549999997893, 33.862920000001395 -7.885429999998451, 33.86230000000069 -7.870059999999285, 33.86722000000191 -7.854699999998047, 33.878280000000814 -7.843019999998433, 33.89242000000195 -7.821499999998196, 33.89734000000135 -7.809819999998581, 33.909630000001926 -7.787699999998949, 33.91762000000199 -7.765569999997751, 33.93238000000201 -7.73913999999786, 33.93852000000152 -7.715779999998631, 33.94590000000062 -7.701019999998607, 33.95266000000083 -7.68380999999863, 33.962500000001455 -7.672129999999015, 33.97172000000137 -7.653079999998226, 33.97448000000077 -7.642319999999018, 33.97879000000103 -7.634329999998954, 33.98001000000113 -7.62388, 33.98493000000235 -7.615279999998165, 33.98985000000175 -7.604209999997693, 33.996000000001004 -7.592529999998078, 34.00399000000107 -7.577159999998912, 34.00153000000137 -7.564869999998336, 33.996610000001965 -7.551959999998871, 33.9935400000013 -7.537819999997737, 33.997230000000854 -7.52552999999898, 34.00583000000188 -7.510779999998704, 34.03595000000132 -7.499709999998231, 34.04594000000179 -7.496639999999388, 34.05992000000151 -7.492339999998876, 34.08574000000226 -7.484349999998813, 34.11217000000215 -7.475129999998899, 34.13492000000224 -7.472669999999198, 34.145370000002 -7.465289999998277, 34.15336000000207 -7.462219999999434, 34.169340000002194 -7.463449999999284, 34.18225000000166 -7.45423, 34.193930000001274 -7.440699999999197, 34.20376000000215 -7.430869999998322, 34.20561000000089 -7.42472, 34.217900000001464 -7.414889999998195, 34.22896000000219 -7.401359999998022, 34.240640000001804 -7.400129999998171, 34.25908000000163 -7.408739999998943, 34.270150000002104 -7.406279999999242, 34.28675000000112 -7.394599999997809, 34.30334000000221 -7.404439999998431, 34.31902000000082 -7.400439999999435, 34.33561000000191 -7.394289999998364, 34.34791000000223 -7.384459999999308, 34.34852000000137 -7.378929999998945, 34.36327000000165 -7.38506999999845, 34.39032000000225 -7.380769999997938, 34.39708000000064 -7.374619999998686, 34.407530000002225 -7.374619999998686, 34.41737000000103 -7.370939999998882, 34.42597000000205 -7.366019999997661, 34.42905000000064 -7.355569999997897, 34.4315000000006 -7.350039999999353, 34.43888000000152 -7.342659999998432, 34.44072000000233 -7.335279999999329, 34.44995000000199 -7.335279999999329, 34.458550000001196 -7.329139999998006, 34.46839000000182 -7.326059999999416, 34.47207000000162 -7.308239999998477, 34.48929000000135 -7.298399999997855, 34.49297000000115 -7.294709999998304, 34.505270000001474 -7.288569999998799, 34.507110000002285 -7.279959999998027, 34.52248000000145 -7.271359999998822, 34.52740000000085 -7.263369999998758, 34.529240000001664 -7.257219999997687, 34.54399000000194 -7.257219999997687, 34.555060000000594 -7.251069999998435, 34.56551000000218 -7.241849999998522, 34.57227000000057 -7.235089999998309, 34.58456000000115 -7.225869999998395, 34.59132000000136 -7.209889999998268, 34.600540000001274 -7.201279999999315, 34.6128400000016 -7.193909999998141, 34.604850000001534 -7.188369999998031, 34.61161000000175 -7.176079999999274, 34.62390000000232 -7.165629999997691, 34.630050000001575 -7.153949999998076, 34.63835000000108 -7.146269999999277, 34.643880000001445 -7.133969999998953, 34.6500300000007 -7.121679999998378, 34.65310000000136 -7.109999999998763, 34.66048000000228 -7.102619999997842, 34.66171000000213 -7.085409999997864, 34.673380000002 -7.07372999999825, 34.688750000001164 -7.063279999998485, 34.70166000000063 -7.063279999998485, 34.71334000000206 -7.049759999998059, 34.720720000001165 -7.038079999998445, 34.73117000000093 -7.028859999998531, 34.739770000001954 -7.02762999999868, 34.74715000000106 -7.020259999999325, 34.75207000000228 -7.009189999998853, 34.76067000000148 -7.006119999998191, 34.764970000001995 -6.997509999999238, 34.77973000000202 -6.984599999997954, 34.792020000000775 -6.972309999999197, 34.789560000001075 -6.970469999998386, 34.80124000000069 -6.968619999997827, 34.815380000001824 -6.962469999998575, 34.815380000001824 -6.9551, 34.82583000000159 -6.945259999998598, 34.8399700000009 -6.937269999998534, 34.84857000000193 -6.933579999998983, 34.84919000000082 -6.92558999999892, 34.85841000000073 -6.921899999999368, 34.864550000002055 -6.915759999998045, 34.87439000000086 -6.916369999999006, 34.88361000000077 -6.913909999999305, 34.88545000000158 -6.907149999999092, 34.9020500000006 -6.897929999999178, 34.906630000001314 -6.897929999999178, 34.90943000000152 -6.897929999999178, 34.964750000001004 -6.95387, 35.03144000000066 -7.029169999997976, 35.06402000000162 -7.06728, 35.28469000000223 -7.186529999999038, 35.336020000000644 -7.208969999997862, 35.39134000000195 -7.235399999997753, 35.41286000000218 -7.244619999997667, 35.411010000001625 -7.286419999998543, 35.4024100000006 -7.299319999998261, 35.385810000001584 -7.303009999997812, 35.37598000000071 -7.312229999997726, 35.37352000000101 -7.32636999999886, 35.36061000000154 -7.323299999998199, 35.35200000000077 -7.325759999997899, 35.35016000000178 -7.339889999999286, 35.34647000000223 -7.341739999998026, 35.338480000002164 -7.341119999999137, 35.33664000000135 -7.357109999999011, 35.32496000000174 -7.367559999998775, 35.31881000000067 -7.371859999999288, 35.315740000001824 -7.382309999999052, 35.308970000001864 -7.392139999998108, 35.29914000000099 -7.397059999999328, 35.29299000000174 -7.409969999998793, 35.29299000000174 -7.434559999997873, 35.28193000000101 -7.440699999999197, 35.2727100000011 -7.448079999998299, 35.25550000000112 -7.44746, 35.25427000000127 -7.454839999998512, 35.24443000000065 -7.444389999998748, 35.22138000000086 -7.458219999998619, 35.22138000000086 -7.465599999997721, 35.21032000000196 -7.479119999998147, 35.201710000001185 -7.48341999999866, 35.19372000000112 -7.493259999999282, 35.19556000000193 -7.485269999999218, 35.18880000000172 -7.482189999998809, 35.16852000000108 -7.482809999997699, 35.16667000000234 -7.487729999998919, 35.15807000000132 -7.48464999999851, 35.1488500000014 -7.49018999999862, 35.14024000000063 -7.497559999997975, 35.13409000000138 -7.493869999998424, 35.127950000001874 -7.496949999998833, 35.12365000000136 -7.496329999998125, 35.1193400000011 -7.501859999998487, 35.11565000000155 -7.506169999998747, 35.1193400000011 -7.51415999999881, 35.108280000002196 -7.519079999998212, 35.103980000001684 -7.531369999998788, 35.103360000000976 -7.539359999998851, 35.11627000000226 -7.550429999999324, 35.11996000000181 -7.548579999998765, 35.13102000000072 -7.571939999997994, 35.14516000000185 -7.598369999997885, 35.156840000001466 -7.619269999999233, 35.156840000001466 -7.626029999999446, 35.156840000001466 -7.634639999998399, 35.153770000000804 -7.642629999998462, 35.16053000000102 -7.653079999998226, 35.16360000000168 -7.661679999999251, 35.15868000000228 -7.661679999999251, 35.15807000000132 -7.669059999998353, 35.1488500000014 -7.669679999999062, 35.143930000002 -7.677049999998417, 35.13963000000149 -7.686889999999039, 35.13963000000149 -7.703479999998308, 35.12979000000087 -7.71331999999893, 35.09875000000102 -7.733909999999014, 35.08092000000215 -7.745589999998629, 35.05818000000181 -7.758499999998094, 35.04527000000235 -7.762799999998606, 35.01884000000064 -7.762189999997645, 35.00901000000158 -7.760959999997795, 34.99917000000096 -7.768329999998969, 34.99302000000171 -7.773859999999331, 34.991180000000895 -7.779399999999441, 34.97766000000229 -7.783089999998992, 34.969050000001516 -7.787389999997686, 34.94815000000199 -7.797839999999269, 34.93955000000096 -7.807669999998325, 34.9291000000012 -7.833489999999074, 34.915570000001026 -7.845169999998689, 34.89590000000135 -7.863609999998516, 34.868240000001606 -7.880819999998494, 34.84611000000223 -7.902949999997873, 34.83136000000195 -7.916469999998299, 34.80247000000236 -7.944749999998749, 34.79632000000129 -7.937369999997827, 34.792630000001736 -7.926919999998063, 34.78864000000067 -7.916779999997743, 34.783110000002125 -7.909399999998641, 34.783110000002125 -7.900179999998727, 34.780030000001716 -7.895269999999073, 34.776960000001054 -7.889119999998002, 34.7732700000015 -7.880509999999049, 34.7708100000018 -7.875599999999395, 34.76098000000093 -7.874369999997725, 34.753600000001825 -7.881739999998899, 34.74684000000161 -7.886659999998301, 34.7425400000011 -7.894649999998364, 34.73639000000185 -7.894649999998364, 34.729010000000926 -7.892189999998664, 34.71979000000101 -7.897109999998065, 34.708730000002106 -7.900179999998727, 34.707500000002256 -7.907559999997829, 34.70320000000174 -7.913709999998901, 34.70197000000189 -7.918619999998555, 34.69336000000112 -7.921079999998256, 34.69275000000198 -7.93152999999802, 34.687220000001616 -7.928459999999177, 34.681070000002364 -7.926619999998366, 34.67677000000185 -7.933989999997721, 34.67431000000215 -7.938909999998941, 34.66263000000072 -7.937679999999091, 34.657710000001316 -7.941979999997784, 34.650330000002214 -7.952429999999367, 34.64296000000104 -7.954889999999068, 34.63804000000164 -7.95980999999847, 34.633120000002236 -7.960419999999431, 34.62390000000232 -7.95980999999847, 34.61591000000226 -7.95980999999847, 34.61222000000089 -7.967179999997825, 34.61222000000089 -7.973949999997785, 34.604230000000825 -7.979479999998148, 34.600540000001274 -7.985629999999219, 34.59255000000121 -7.992999999998574, 34.59220000000096 -7.995099999998274))'
        }

        answer = webpy_esapp_helpers.scatterTimeseries(params)

    def testCreateTimeseriesDrawProperties(self):

        params = {'tsdrawproperties':
            {
                'charttype': "line",
                'color': "#000000",
                'linestyle': "Solid",
                'linewidth': 2,
                'productcode': "olci-wrr",
                'subproductcode': "chl-oc4me",
                'tsname_in_legend': "olci-wrr - V02.0 - chl-oc4me",
                'version': "V02.0",
                'yaxe_id': "olci-wrr - V02.0"
            }
        }
        answer = webpy_esapp_helpers.createTimeseriesDrawProperties(params)

    def testMatplotlib(self):
        # from PIL import Image

        # datasetcompleteness = {
        #     "firstdate": "",
        #     "intervals": "",
        #     "lastdate": "",
        #     "missingfiles": 0,
        #     "totfiles": 1
        # }
        #
        # datasetcompleteness = {
        #     "firstdate": "01-01",
        #     "intervals": [
        #                      {
        #                          "fromdate": "01-01",
        #                          "intervalpercentage": 100.0,
        #                          "intervaltype": "present",
        #                          "missing": False,
        #                          "todate": "12-21",
        #                          "totfiles": 36
        #                      }
        #                  ],
        #     "lastdate": "12-21",
        #     "missingfiles": 0,
        #     "totfiles": 36
        #
        # }

        # datasetcompleteness = {
        #     "firstdate": "1999-01-01",
        #     "intervals": [
        #         {
        #             "fromdate": "1999-01-01",
        #             "intervalpercentage": 99.57386363636364,
        #             "intervaltype": "present",
        #             "missing": False,
        #             "todate": "2018-06-11",
        #             "totfiles": 701
        #         },
        #         {
        #             "fromdate": "2018-06-21",
        #             "intervalpercentage": 0.42613636363636365,
        #             "intervaltype": "missing",
        #             "missing": True,
        #             "todate": "2018-07-11",
        #             "totfiles": 3
        #         }
        #     ],
        #     "lastdate": "2018-07-11",
        #     "missingfiles": 3,
        #     "totfiles": 704
        # }

        datasetcompleteness = {
            "firstdate": "1984-01-01",
            "intervals": [
                {
                    "fromdate": "1984-01-01",
                    "intervalpercentage": 2.891566265060241,
                    "intervaltype": "present",
                    "missing": False,
                    "todate": "1984-12-01",
                    "totfiles": 12
                },
                {
                    "fromdate": "1985-01-01",
                    "intervalpercentage": 3.1325301204819276,
                    "intervaltype": "missing",
                    "missing": True,
                    "todate": "1986-01-01",
                    "totfiles": 13
                },
                {
                    "fromdate": "1986-02-01",
                    "intervalpercentage": 8.19277108433735,
                    "intervaltype": "present",
                    "missing": False,
                    "todate": "1988-11-01",
                    "totfiles": 34
                },
                {
                    "fromdate": "1988-12-01",
                    "intervalpercentage": 2.891566265060241,
                    "intervaltype": "missing",
                    "missing": True,
                    "todate": "1989-11-01",
                    "totfiles": 12
                },
                {
                    "fromdate": "1989-12-01",
                    "intervalpercentage": 1.0,
                    "intervaltype": "present",
                    "missing": False,
                    "todate": "1990-01-01",
                    "totfiles": 2
                },
                {
                    "fromdate": "1990-02-01",
                    "intervalpercentage": 2.1686746987951806,
                    "intervaltype": "missing",
                    "missing": True,
                    "todate": "1990-10-01",
                    "totfiles": 9
                },
                {
                    "fromdate": "1990-11-01",
                    "intervalpercentage": 80.0,
                    "intervaltype": "present",
                    "missing": False,
                    "todate": "2018-06-01",
                    "totfiles": 332
                },
                {
                    "fromdate": "2018-07-01",
                    "intervalpercentage": -0.27710843373493965,
                    "intervaltype": "missing",
                    "missing": True,
                    "todate": "2018-07-01",
                    "totfiles": 1
                }
            ],
            "lastdate": "2018-07-01",
            "missingfiles": 35,
            "totfiles": 415
        }

        totfiles = None
        missingfiles = None
        firstdate = ''
        lastdate = ''
        intervals = []

        # mpl.use('agg')
        mpl.rcParams['savefig.pad_inches'] = 0
        plt.autoscale(tight=True)

        yinch = 0.38
        fig, ax = plt.subplots(figsize=(3.4, yinch), frameon=False, facecolor='w', dpi=128)

        for attr, value in datasetcompleteness.items():
            if attr == 'missingfiles':
                missingfiles = value
            if attr == 'totfiles':
                totfiles = value
            if attr == 'firstdate':
                firstdate = value
            if attr == 'lastdate':
                lastdate = value
            if attr == 'intervals':
                intervals = value

        left = np.zeros(1)  # left alignment of data starts at zero
        for interval in intervals:
            d = interval['intervalpercentage']
            if interval['missing']:
                color = '#FF0000'
            else:
                color = '#81AF34'

            plt.barh(0, d, color=color, height=5, linewidth=0, align='center', left=left)
            # accumulate the left-hand offsets
            left += d

        # completeness = ('A')
        # segments = 5
        # # generate some multi-dimensional data & arbitrary labels
        # data = 3 + 10 * np.random.rand(segments, len(completeness))
        # y_pos = np.arange(len(completeness))
        #
        # # fig = plt.figure(figsize=(3.4, 0.38), frameon=False)   # dpi=80,
        # yinch = 0.38
        # fig, ax = plt.subplots(figsize=(3.4, yinch), frameon=False, facecolor='w', dpi=128)
        # # ax = fig.add_subplot(111)
        # # ax.axis('off')
        #
        # colors = 'rg'
        # left = np.zeros(len(completeness))  # left alignment of data starts at zero
        # for i, d in enumerate(data):
        #     color = '#81AF34'
        #     plt.barh(y_pos, d, color=color, height=5, linewidth=0, align='center', left=left)
        #     # plt.barh(y_pos, d, color=colors[i % len(colors)], height=5, linewidth=0, align='center', left=left)
        #     # accumulate the left-hand offsets
        #     left += d

        font1 = {  # 'family': 'sans-serif',
            'color': 'black',
            'weight': 'bold',
            'size': 6}

        font2 = {  # 'family': 'sans-serif',
            'color': 'black',
            'weight': 'bold',
            'size': 6.5}

        font3 = {  # 'family': 'sans-serif',
            'color': '#FF0000',
            'weight': 'bold',
            'size': 6.5}

        plt.gcf().text(0.02, 0.7, firstdate, fontdict=font1)
        plt.gcf().text(0.3, 0.72, 'Files: ' + str(totfiles), fontdict=font2)
        plt.gcf().text(0.55, 0.72, 'Missing: ' + str(missingfiles), fontdict=font3)
        plt.gcf().text(0.83, 0.7, lastdate, fontdict=font1)

        # left, width = .15, 1
        # bottom, height = .15, 1
        # right = left + width
        # top = bottom + height
        #
        # ax.text(right, top, '01-01-2017',
        #         horizontalalignment='left',
        #         verticalalignment='top',
        #         # transform=fig.transAxes,
        #         fontdict=font1)

        # fig.text(right, top, 'Files: 148',
        #         horizontalalignment='left',
        #         verticalalignment='bottom',
        #         # transform=fig.transAxes,
        #         fontdict=font2)

        # ax.text(right, 0.5 * (bottom + top), 'Missing: 2',
        #         horizontalalignment='center',
        #         verticalalignment='center',
        #         transform=ax.transAxes,
        #         fontdict=font3)

        # ax.text(left, top, '01-07-2018',
        #         horizontalalignment='right',
        #         verticalalignment='top',
        #         # transform=fig.transAxes,
        #         fontdict=font1)

        # plt.text(.01, .025, '2014-06-01', fontdict=font1)
        # plt.text(0, 2, 'Files: 148', fontdict=font2)
        # plt.text(0, 3, 'Missing: 2', fontdict=font3)
        # plt.text(0, 4, '2018-07-01', fontdict=font1)

        # plt.text(2, 0.65, r'$\cos(2 \pi t) \exp(-t)$', fontdict=font)
        # plt.text(0.6, 0.5, "test", size=50, rotation=30.,
        #          ha="center", va="center",
        #          bbox=dict(boxstyle="round",
        #                    ec=(1., 0.5, 0.5),
        #                    fc=(1., 0.8, 0.8),
        #                    )
        #          )
        # plt.tight_layout()

        # plt.gca().axes.get_xaxis().set_visible(False)
        plt.axis('off')
        plt.margins(0)
        fig.subplots_adjust(left=0.07, right=0.95, bottom=0.15, top=0.9)  # , wspace=0.2, hspace=0.2
        # ypixels = int(yinch * fig.get_dpi())
        ax.set_ylim(0, 4)
        # plt.box(on=None)
        plt.draw()
        # buf = io.BytesIO()
        buf = io.StringIO()
        plt.savefig(buf, format='png', bbox_inches=0, pad_inches=0)
        plt.savefig('/srv/www/eStation2/testmatlibplot.png', bbox_inches=0, pad_inches=0)  # bbox_inches='tight'
        # buf.seek(0)
        # img = Image.open(buf)
        encoded = base64.b64encode(str(buf))
        # buf.close()
        # encoded = base64.b64encode(open("/var/www/eStation2/completeness.png", "rb").read())
        datasetcompletenessimage = "data:image/png;base64," + encoded
        print(datasetcompletenessimage)

    def testPlotly(self):

        trace1 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 11842, None,
                  None, None, None, None, None, None, None, None],
            "name": "Building/Use",
            "type": "bar",
            "uid": "e59e0e",
            "visible": True
        }
        trace2 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, 6630, 4328, 2771, 2788, 2665, 4755, 7716, None, None, None, None, None, None, None, None, None,
                  None, None, None, 8724, 10291, 12345, 11874, None],
            "name": "Noise",
            "type": "bar",
            "uid": "b46848"
        }
        trace3 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, None, None, None, None, None, None, 24481, None, None, None,
                  None, 12348, 10532, None, None, None, None, None],
            "name": "Dirty Conditions",
            "type": "bar",
            "uid": "67c879",
            "visible": True
        }
        trace4 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, 5948, None, None, None, 6576, None, None, 15232, 16196, 16178, 14256, 13486, 13213, 12761,
                  11141, None, None, 10061, None, None, None, None, None],
            "name": "Sewer",
            "type": "bar",
            "uid": "da3ac3",
            "visible": True
        }
        trace5 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, 1490, 1676, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None],
            "name": "Taxi Complaint",
            "type": "bar",
            "uid": "0f18f1",
            "visible": True
        }
        trace6 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, None, None, None, 14899, 15691, 14542, None, 12927, 13667,
                  11387, None, None, None, None, None, None, None, None],
            "name": "General Construction/Plumbing",
            "type": "bar",
            "uid": "c695f5",
            "visible": True
        }
        trace7 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, None, 12845, 44009, 76667, 82382, 21828, 52730, 51453,
                  40379, 24158, 9904, 9186, 9380, 10945, 12526, 9097, None, None],
            "name": "Street Light Condition",
            "type": "bar",
            "uid": "9fa287",
            "visible": True
        }
        trace8 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, None, 17009, 13963, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None, None],
            "name": "Missed Collection (All Materials)",
            "type": "bar",
            "uid": "603090",
            "visible": True
        }
        trace9 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, 4035, None, None, 1945, 5427, 9257, 14605, 18638, 19246, 19358, 19221, 18068, 19030,
                  20480, 21078, 20400, 17487, 15718, 13349, 11109, 8615, None, None],
            "name": "Water System",
            "type": "bar",
            "uid": "8c5771",
            "visible": True
        }
        trace10 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, 1802, 3517, 7463, 11370, None, None, None, None, None, None, None, None,
                  8769, None, 8703, 9188, 10986, 8838, 7195, None],
            "name": "Illegal Parking",
            "type": "bar",
            "uid": "ddf793",
            "visible": True
        }
        trace11 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, 2736, None, None, None, 2346, 6899, 35215, 29454, 34193, 34529, 29504, 25923, 39173, 52609,
                  37891, 24564, 17117, 26067, 29566, 9260, 8062, None, 6596, None],
            "name": "Street Condition",
            "type": "bar",
            "uid": "628823",
            "visible": True
        }
        trace12 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, 24963, 20001, 12133, 11277, 15430, 30329, 60150, 143260, 222263, 242672, 244957, 225790, 227665,
                  218406, 216547, 194797, 151869, 133464, 104735, 94243, 83764, 74412, 57444, None],
            "name": "Other",
            "type": "bar",
            "uid": "99c04f",
            "visible": True
        }
        trace13 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, 3749, None, 2010, 2284, 1705, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None],
            "name": "Noise - Vehicle",
            "type": "bar",
            "uid": "10597d",
            "visible": True
        }
        trace14 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, 5471, 3416, 2816, 2875, 4095, 7652, 13432, 17141, 17593, 15573, 14515, 13872, None, 11899, None,
                  12145, 13125, 14664, 15488, 16770, 17193, 15296, 11664, None],
            "name": "Blocked Driveway",
            "type": "bar",
            "uid": "fd2e1a",
            "visible": True
        }
        trace15 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, 8485, 5796, 3797, 3289, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, 6897, 8956, 12070, 13982, None],
            "name": "Noise - Street/Sidewalk",
            "type": "bar",
            "uid": "c2a24f",
            "visible": True
        }
        trace16 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, 6707, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, None, None, None],
            "name": "Sanitation Condition",
            "type": "bar",
            "uid": "fded78",
            "visible": True
        }
        trace17 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, 14817, 9553, 5097, 2458, None, None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None, None, None, 13290, 18779, None],
            "name": "Noise - Commercial",
            "type": "bar",
            "uid": "395ea3",
            "visible": True
        }
        trace18 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, None, None, None, 14250, 13382, 12287, None, None, None,
                  None, None, None, None, None, None, None, None, None],
            "name": "Damaged Tree",
            "type": "bar",
            "uid": "7c28f0",
            "visible": True
        }
        trace19 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                  9712, 9076, None, None, None, None, None, None],
            "name": "Broken Muni Meter",
            "type": "bar",
            "uid": "703c33",
            "visible": True
        }
        trace20 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, 5142, 3285, 3282, 3787, 3234, 4863, 8932, 14104, 13382, None, None, None, 14962, 33431, 17646,
                  12326, 10232, None, None, None, None, None, 6165, None],
            "name": "Traffic Signal Condition",
            "type": "bar",
            "uid": "a29d51",
            "visible": True
        }
        trace21 = {
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "y": [None, None, None, None, None, None, None, None, None, None, None, None, None, 15577, None, None, None,
                  None, 11916, None, None, None, None, None, None],
            "name": "Graffiti",
            "type": "bar",
            "uid": "1f5a32",
            "visible": True
        }
        data = py.Data(
            [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8, trace9, trace10, trace11, trace12, trace13,
             trace14, trace15, trace16, trace17, trace18, trace19, trace20, trace21])
        layout = {
            "autosize": True,
            "barmode": "stack",
            "height": 472,
            "legend": {
                "x": 1.02045209903,
                "y": 0.00968523002421
            },
            "showlegend": True,
            "title": "The 6 Most Common 311 Complaints",
            "width": 1152,
            "xaxis": {
                "autorange": True,
                "range": [0.5, 23.5],
                "title": "Hour in Day",
                "type": "linear"
            },
            "yaxis": {
                "autorange": True,
                "exponentformat": "SI",
                "range": [0, 458912.631579],
                "showexponent": "last",
                "title": "Number of Complaints",
                "type": "linear"
            }
        }
        fig = py.Figure(data=data, layout=layout)
        plot_url = py.plot(fig)

    def test_SaveWorkspace(self):
        params = {
            "userid": 'jurvtk',
            "workspaceid": '11',
            "workspacename": 'My workspace',
            "isNewWorkspace": 'false',
            "pinned": 'false',
            "maps": [{"newtemplate": 'false',
                      "userid": "jurvtk",
                      "map_tpl_id": 1,
                      "map_tpl_name": "10 Day RFE_LTA - 2.0",
                      "istemplate": 'true',
                      "mapviewPosition": "4,2",
                      "mapviewSize": "800,700",
                      "productcode": "chirps-dekad",
                      "subproductcode": "10davg",
                      "productversion": "2.0",
                      "mapsetcode": "CHIRP-Africa-5km",
                      "legendid": 75,
                      "legendlayout": "vertical",
                      "legendObjPosition": "0,0",
                      "showlegend": 'true',
                      "titleObjPosition": "95,3",
                      "titleObjContent": "<div><span style=\"color:rgb(0,0,0); font-size: 20px; font-weight: bold;\">{selected_area}</span></div><div><span style=\"color:rgb(0,0,0); font-size: 20px;\">{product_name}</span></div><div><span style=\"color:rgb(51,102,255); font-size: 20px;\">{product_date}</span></div>",
                      "disclaimerObjPosition": "267,582",
                      "disclaimerObjContent": "Disclaimer",
                      "logosObjPosition": "437,561",
                      "logosObjContent": "[{\"src\":\"resources/img/logo/MESA_h110.jpg\",\"width\":\"65\",\"height\":\"50\"},{\"src\":\"resources/img/logo/AUC_h110.jpg\",\"width\":\"65\",\"height\":\"50\"},{\"src\":\"resources/img/logo/ACP_h110.jpg\",\"width\":\"65\",\"height\":\"50\"},{\"src\":\"resources/img/logo/logo_en.gif\",\"width\":\"65\",\"height\":\"50\"}]",
                      "showObjects": 'true',
                      "showtoolbar": 'true',
                      "showgraticule": 'false',
                      "scalelineObjPosition": "109,591",
                      "vectorLayers": "33,10",
                      "outmask": 'false',
                      "outmaskFeature": 'null',
                      "auto_open": 'false',
                      "zoomextent": "13.847351074218743,-17.871856689453118,43.983459472656236,5.664825439453127",
                      "mapsize": "790,617",
                      "mapcenter": "28.91540527343749,-6.1035156249999964"}],

            "graphs": [{"newtemplate": 'false',
                        "userid": "jurvtk",
                        "graph_tpl_id": 1,
                        "graph_tpl_name": "Profile NDVI",
                        "istemplate": 'true',
                        "graphviewposition": "817,1",
                        "graphviewsize": "617,522",
                        "graphproperties": "{\"localRefresh\":false,\"title\":\"Zambia - South Luangwa - National Park\",\"subtitle\":2017,\"filename\":\"Zambia - South Luangwa - National Park_2017\",\"graph_title_font_size\":\"20\",\"graph_title_font_color\":\"#000080\",\"graph_subtitle_font_size\":\"18\",\"graph_subtitle_font_color\":\"#808080\",\"xaxe_font_size\":\"22\",\"xaxe_font_color\":\"#000000\",\"legend_title_font_size\":\"14\",\"legend_title_font_color\":\"#000000\",\"width\":\"1000\",\"height\":\"800\"}",
                        "graph_type": "xy",
                        "selectedtimeseries": "[{\"productcode\":\"vgt-ndvi\",\"version\":\"sv2-pv2.2\",\"subproductcode\":\"ndvi-linearx2\",\"mapsetcode\":\"SPOTV-Africa-1km\",\"date_format\":\"YYYYMMDD\",\"frequency_id\":\"e1dekad\",\"cumulative\":false,\"difference\":false,\"reference\":false,\"colorramp\":false,\"legend_id\":null,\"zscore\":false},{\"productcode\":\"vgt-ndvi\",\"version\":\"sv2-pv2.2\",\"subproductcode\":\"10dmin-linearx2\",\"mapsetcode\":\"SPOTV-Africa-1km\",\"date_format\":\"MMDD\",\"frequency_id\":\"e1dekad\",\"cumulative\":false,\"difference\":false,\"reference\":false,\"colorramp\":false,\"legend_id\":null,\"zscore\":false},{\"productcode\":\"vgt-ndvi\",\"version\":\"sv2-pv2.2\",\"subproductcode\":\"10davg-linearx2\",\"mapsetcode\":\"SPOTV-Africa-1km\",\"date_format\":\"MMDD\",\"frequency_id\":\"e1dekad\",\"cumulative\":false,\"difference\":false,\"reference\":false,\"colorramp\":false,\"legend_id\":null,\"zscore\":false},{\"productcode\":\"vgt-ndvi\",\"version\":\"sv2-pv2.2\",\"subproductcode\":\"10dmax-linearx2\",\"mapsetcode\":\"SPOTV-Africa-1km\",\"date_format\":\"MMDD\",\"frequency_id\":\"e1dekad\",\"cumulative\":false,\"difference\":false,\"reference\":false,\"colorramp\":false,\"legend_id\":null,\"zscore\":false}]",
                        "yearts": "",
                        "tsfromperiod": "",
                        "tstoperiod": "",
                        "yearstocompare": "[2017]",
                        "tsfromseason": "",
                        "tstoseason": "",
                        "wkt_geom": "POLYGON((31.271120000001247 -12.94510999999875, 31.271350000000893 -12.944299999999203, 31.27534000000196 -12.932859999998982, 31.27838000000156 -12.925909999998112, 31.283210000001418 -12.921009999998205, 31.289450000002034 -12.91537999999855, 31.293980000002193 -12.912889999997788, 31.300240000002304 -12.908639999997831, 31.307890000001862 -12.903339999998934, 31.315560000000914 -12.89940999999817, 31.32361000000128 -12.89650999999867, 31.337930000001506 -12.889699999997902, 31.348120000000563 -12.888489999999365, 31.35341000000153 -12.888729999998759, 31.361900000001697 -12.88995999999861, 31.37213000000156 -12.890459999998711, 31.374220000001515 -12.889039999998204, 31.382040000002235 -12.891999999998006, 31.38702000000194 -12.894329999999172, 31.399420000001555 -12.896859999998924, 31.406110000001718 -12.896739999998317, 31.408210000001418 -12.896009999998569, 31.41305000000102 -12.89144, 31.41541000000143 -12.885889999997744, 31.416330000001835 -12.879659999998694, 31.414050000001225 -12.87177999999767, 31.42000000000189 -12.84975999999915, 31.421250000001237 -12.845109999998385, 31.423960000001898 -12.839889999999286, 31.426840000001903 -12.834149999998772, 31.429720000001907 -12.828419999998005, 31.432690000001458 -12.81992999999784, 31.436030000000756 -12.810379999998986, 31.436440000001312 -12.796239999997852, 31.43870000000061 -12.786199999998644, 31.44068000000152 -12.779959999998027, 31.439400000001115 -12.768959999999424, 31.439190000000963 -12.75930999999764, 31.437850000002072 -12.745209999999133, 31.438560000002326 -12.729, 31.44105000000127 -12.713439999997718, 31.441530000001876 -12.704349999998158, 31.441560000001118 -12.703779999998005, 31.441140000000814 -12.699699999999211, 31.44068000000152 -12.695189999998547, 31.44079000000056 -12.690819999997984, 31.440870000002178 -12.68793999999798, 31.439570000002277 -12.685269999998127, 31.439040000001114 -12.684189999998125, 31.439140000002226 -12.681249999997817, 31.439250000001266 -12.677629999998317, 31.441500000000815 -12.667249999998603, 31.44695000000138 -12.658539999998538, 31.452070000001186 -12.65085999999792, 31.457250000001295 -12.645599999998012, 31.46089000000211 -12.634159999997792, 31.464890000001105 -12.624089999999342, 31.47005000000172 -12.618139999998675, 31.474230000001626 -12.615649999997913, 31.477610000001732 -12.609379999998055, 31.47958000000108 -12.602109999997992, 31.480500000001484 -12.59588999999869, 31.48214000000189 -12.589999999998327, 31.484890000001542 -12.586849999997867, 31.488720000001194 -12.584709999999177, 31.495590000002267 -12.579099999999016, 31.497370000000956 -12.577649999999267, 31.50706000000173 -12.569539999998597, 31.512910000001284 -12.563239999997677, 31.51941000000079 -12.55449999999837, 31.52799000000232 -12.54399999999805, 31.532750000002125 -12.535979999998744, 31.539150000002337 -12.522419999999329, 31.545170000001235 -12.507489999998143, 31.55334000000221 -12.494589999998425, 31.555790000002162 -12.491189999998824, 31.559140000001207 -12.486549999997806, 31.56293000000187 -12.481999999998152, 31.56774000000223 -12.47707999999875, 31.568240000002334 -12.476729999998497, 31.572250000001077 -12.473889999999301, 31.581660000001648 -12.469579999999041, 31.592060000000856 -12.462139999997817, 31.598910000000615 -12.45339999999851, 31.606810000001133 -12.44463999999789, 31.616500000001906 -12.436869999997725, 31.625560000002224 -12.433249999998225, 31.639860000001136 -12.426769999998214, 31.6516900000006 -12.4210299999977, 31.657970000002024 -12.4184899999982, 31.663910000001124 -12.416999999997643, 31.66848000000209 -12.416219999999157, 31.6723600000023 -12.416839999998047, 31.672730000002048 -12.417519999999058, 31.672920000000886 -12.417849999997998, 31.674920000001293 -12.421269999998913, 31.68166000000201 -12.423899999997957, 31.692510000000766 -12.421269999998913, 31.69818000000123 -12.423229999998512, 31.705690000000686 -12.428949999997712, 31.71169000000191 -12.42916999999943, 31.716330000001108 -12.432519999998476, 31.728650000000926 -12.432629999999335, 31.732160000001386 -12.432209999999031, 31.73569000000134 -12.432839999997668, 31.741000000001804 -12.43445999999858, 31.74808000000121 -12.43638, 31.755120000001625 -12.436249999998836, 31.76423000000068 -12.434339999997974, 31.772970000001806 -12.431759999997666, 31.780320000001666 -12.430239999997866, 31.786290000001827 -12.429779999998573, 31.795090000001437 -12.429939999998169, 31.806040000001303 -12.431789999998728, 31.816710000000967 -12.436749999998938, 31.8316500000019 -12.444379999999, 31.84983000000102 -12.454349999998158, 31.86294000000089 -12.458569999998872, 31.87178000000131 -12.46045999999842, 31.880670000002283 -12.46440999999868, 31.88745000000199 -12.468409999997675, 31.89390000000094 -12.473449999997683, 31.90104000000065 -12.477789999999004, 31.913840000001073 -12.483729999998104, 31.92413000000124 -12.487659999998868, 31.934110000001965 -12.492969999999332, 31.941670000001977 -12.500049999998737, 31.952150000000984 -12.5122399999982, 31.95542000000205 -12.516649999997753, 31.9587500000016 -12.523479999998017, 31.963850000001912 -12.530959999998231, 31.97211000000061 -12.538369999998395, 31.98178000000189 -12.545059999998557, 31.99109000000135 -12.551759999998467, 31.99829000000136 -12.558859999999186, 32.00260000000162 -12.562559999998484, 32.004830000001675 -12.56767999999829, 32.00536000000102 -12.57524999999805, 32.00771000000168 -12.585539999998218, 32.011020000001736 -12.591679999997723, 32.01822000000175 -12.598069999998188, 32.023590000000695 -12.602099999998245, 32.03068000000167 -12.60436, 32.037530000001425 -12.61077, 32.03823000000193 -12.611649999998917, 32.04478000000199 -12.619919999999183, 32.05240000000231 -12.629759999997987, 32.058530000002065 -12.635839999999007, 32.064650000002075 -12.641229999999268, 32.06576000000132 -12.643609999999171, 32.066240000001926 -12.648769999997967, 32.06594000000223 -12.651189999998678, 32.06746000000203 -12.655989999999292, 32.07224000000133 -12.664499999998952, 32.079100000000835 -12.67192999999861, 32.08414000000084 -12.67630999999892, 32.084310000002006 -12.683539999998175, 32.08617000000231 -12.687639999998282, 32.090500000002066 -12.69202999999834, 32.09270000000106 -12.695779999998194, 32.09381000000212 -12.69782, 32.092460000001665 -12.70060999999805, 32.087940000001254 -12.703119999998307, 32.08096000000114 -12.706019999997807, 32.07516000000214 -12.714069999998173, 32.07395000000179 -12.722359999997934, 32.072290000001885 -12.726879999998346, 32.06645000000208 -12.733209999998508, 32.064140000002226 -12.739459999998871, 32.06419000000096 -12.741869999998016, 32.06564000000071 -12.743559999998979, 32.06670000000122 -12.743879999998171, 32.06721000000107 -12.750079999997979, 32.06561000000147 -12.757339999998294, 32.05873000000065 -12.76437999999871, 32.054980000000796 -12.76962999999887, 32.04936000000089 -12.770439999998416, 32.04623000000174 -12.772229999998672, 32.04346000000078 -12.77469999999812, 32.04567000000134 -12.77878999999848, 32.047520000001896 -12.782539999998335, 32.04909000000225 -12.789049999999406, 32.048760000001494 -12.7900899999986, 32.045570000002044 -12.789129999999204, 32.04451000000154 -12.789149999998699, 32.041730000000825 -12.790929999999207, 32.04034000000138 -12.791649999999208, 32.03377000000182 -12.796949999998105, 32.02760000000126 -12.804669999997714, 32.02566000000115 -12.811939999997776, 32.02336000000105 -12.819229999999152, 32.018630000002304 -12.827939999999217, 32.015190000001894 -12.831799999998111, 32.015010000000984 -12.839049999998679, 32.011310000001686 -12.84635999999773, 32.01003000000128 -12.852239999998346, 32.00531000000228 -12.860959999998158, 32.000880000001416 -12.867599999997765, 32.00199000000066 -12.869989999999234, 32.004150000000664 -12.87235999999939, 32.010550000000876 -12.87463999999818, 32.016530000000785 -12.874159999999392, 32.02715000000171 -12.87601999999788, 32.036080000001675 -12.880659999998898, 32.04469000000063 -12.887019999998302, 32.05696000000171 -12.899519999999029, 32.063240000001315 -12.911449999997785, 32.06513000000086 -12.914129999999204, 32.07455000000118 -12.927409999998417, 32.08928000000196 -12.953989999998157, 32.09144000000197 -12.957069999998566, 32.10497000000214 -12.976409999999305, 32.1166000000012 -12.991329999998925, 32.12315000000126 -12.999109999998836, 32.12718000000132 -13.00558, 32.13123000000087 -13.012729999998555, 32.13126000000193 -13.014109999998254, 32.132040000002235 -13.017199999998411, 32.13169000000198 -13.017549999998664, 32.13065000000097 -13.017909999998665, 32.12711000000127 -13.017989999998463, 32.108570000002146 -13.0094199999985, 32.09856000000218 -13.003419999999096, 32.08718000000226 -12.999869999997827, 32.083660000002055 -12.999599999999191, 32.076640000001134 -13.001479999998992, 32.07275000000118 -13.00086999999803, 32.06920000000173 -12.999909999998636, 32.057920000001104 -13.00014999999803, 32.05229000000145 -13.000599999999395, 32.03625000000102 -13.008869999997842, 32.02962000000116 -13.011759999999413, 32.021560000001045 -13.013989999997648, 32.01172000000224 -13.015579999999318, 32.00254000000132 -13.015079999999216, 31.998240000000806 -13.01206, 31.99493000000075 -13.006619999998293, 31.988710000001447 -12.997099999998682, 31.97918000000209 -12.981429999998, 31.976510000002236 -12.972529999999097, 31.975000000002183 -12.968419999999242, 31.973480000000563 -12.963629999998375, 31.96466000000146 -12.963129999998273, 31.960480000001553 -12.965619999999035, 31.9570100000019 -12.96809999999823, 31.951850000001286 -12.974069999998392, 31.950620000001436 -12.981329999998707, 31.947880000001533 -12.98483, 31.944030000000566 -12.986289999998917, 31.939140000002226 -12.988799999999173, 31.934290000001056 -12.992349999998623, 31.9315600000009 -12.99619999999777, 31.929520000001503 -12.999679999998989, 31.925720000001093 -13.003199999999197, 31.92120000000068 -13.005709999999453, 31.918750000000728 -13.006799999999203, 31.915610000001834 -13.008239999999205, 31.91142000000218 -13.010389999997642, 31.90976000000228 -13.0145599999978, 31.910870000001523 -13.016599999999016, 31.90711000000192 -13.022189999997863, 31.901820000000953 -13.022299999998722, 31.89585000000079 -13.023449999998775, 31.889960000002247 -13.028049999998984, 31.888640000001033 -13.032219999999143, 31.885200000000623 -13.036079999998037, 31.884530000001178 -13.037469999999303, 31.87445000000116 -13.043879999999263, 31.873120000002018 -13.04769, 31.870710000001054 -13.050159999998868, 31.861960000002 -13.053439999997863, 31.855020000000877 -13.058399999998073, 31.853080000000773 -13.066019999998389, 31.852820000001884 -13.070159999999305, 31.84899000000223 -13.072649999998248, 31.84407000000101 -13.073089999998047, 31.833880000001955 -13.075369999998657, 31.82267000000138 -13.07868999999846, 31.819250000002285 -13.08357999999862, 31.81800000000112 -13.090499999998428, 31.813170000001264 -13.09541999999783, 31.80935000000136 -13.098249999999098, 31.8062000000009 -13.099349999998594, 31.80055000000175 -13.099459999999453, 31.791730000000825 -13.099289999998291, 31.78147000000172 -13.098109999998996, 31.777620000000752 -13.099579999998241, 31.774100000002363 -13.099639999998544, 31.7729900000013 -13.09759, 31.770800000002055 -13.094539999998233, 31.769000000002052 -13.092499999998836, 31.763640000001033 -13.089849999998478, 31.757990000001882 -13.089619999998831, 31.751000000002023 -13.092509999998583, 31.75032000000101 -13.093559999999343, 31.75079000000187 -13.098719999998139, 31.75199000000066 -13.105249999998705, 31.75137000000177 -13.109049999999115, 31.748920000001817 -13.109789999998611, 31.746080000000802 -13.109159999998155, 31.740520000001197 -13.113059999997859, 31.73783000000185 -13.118969999997717, 31.739380000000892 -13.125139999998282, 31.7433400000009 -13.128849999999147, 31.746970000001966 -13.1332599999987, 31.744940000002316 -13.137439999998605, 31.740410000002157 -13.139939999999115, 31.735180000001492 -13.142799999997806, 31.735240000001795 -13.145549999999275, 31.738220000001093 -13.152729999997973, 31.741900000000896 -13.15954999999849, 31.741610000000946 -13.1619699999992, 31.739540000002307 -13.164419999999154, 31.73537000000215 -13.16725999999835, 31.73052000000098 -13.171489999998812, 31.729230000000825 -13.17703999999867, 31.72936000000118 -13.182889999998224, 31.72802000000229 -13.18601999999919, 31.72422000000188 -13.189879999998084, 31.721810000000914 -13.192689999998038, 31.71694000000207 -13.195879999999306, 31.715550000000803 -13.196599999999307, 31.70053000000189 -13.203789999997753, 31.693600000002334 -13.209779999999228, 31.68181000000186 -13.219309999998586, 31.671340000000782 -13.225029999997787, 31.667190000001938 -13.228899999998248, 31.66479000000072 -13.232389999999214, 31.663150000002133 -13.237939999999071, 31.662240000001475 -13.244849999999133, 31.66244000000188 -13.253799999998591, 31.66403000000173 -13.262049999999363, 31.66450000000077 -13.267209999998158, 31.66707000000133 -13.272329999997964, 31.665820000001986 -13.279239999998026, 31.664510000002338 -13.284089999999196, 31.666110000001936 -13.292679999998654, 31.66947000000073 -13.301229999999123, 31.67062000000078 -13.305339999998978, 31.67001000000164 -13.309489999997822, 31.667930000001434 -13.311249999998836, 31.66338000000178 -13.313069999998334, 31.65780000000086 -13.316619999997783, 31.655430000000706 -13.321139999998195, 31.654130000000805 -13.3263399999978, 31.654970000001413 -13.33252999999786, 31.65302000000156 -13.339799999997922, 31.648870000000898 -13.34436999999889, 31.639870000000883 -13.352799999998751, 31.637150000002293 -13.357689999998911, 31.635090000001583 -13.359789999998611, 31.63340000000062 -13.363619999998264, 31.63137000000097 -13.367789999998422, 31.62753000000157 -13.36992999999893, 31.622630000001664 -13.372089999998934, 31.6173200000012 -13.371159999998781, 31.611320000001797 -13.371619999998074, 31.59795000000122 -13.373939999997674, 31.59270000000106 -13.376109999999244, 31.5895500000006 -13.377889999997933, 31.57358000000204 -13.390599999998813, 31.567700000001423 -13.396229999998468, 31.56145000000106 -13.401859999998123, 31.556250000001455 -13.406089999998585, 31.55525000000125 -13.409209999997984, 31.5546800000011 -13.415429999999105, 31.555520000001707 -13.421609999999419, 31.558170000002065 -13.430179999999382, 31.560060000001613 -13.435649999999441, 31.56376000000091 -13.44350999999915, 31.56670000000122 -13.448629999998957, 31.56673000000228 -13.45035999999891, 31.568640000001324 -13.456519999997909, 31.568780000001425 -13.463409999998476, 31.567840000001524 -13.468599999998332, 31.565270000000965 -13.480709999997998, 31.56101000000126 -13.496289999999135, 31.56130000000121 -13.509739999997691, 31.563720000001922 -13.524159999999029, 31.56300000000192 -13.53968999999779, 31.56181000000106 -13.550389999998515, 31.559720000001107 -13.567999999999302, 31.554340000000593 -13.58085999999821, 31.551360000001296 -13.590559999998732, 31.549850000001243 -13.594539999998233, 31.547680000001492 -13.600279999998747, 31.542880000000878 -13.607269999998607, 31.536660000001575 -13.613929999997708, 31.525510000001304 -13.621719999999186, 31.517860000001747 -13.62771999999859, 31.517540000000736 -13.627859999998691, 31.505600000002232 -13.633129999998346, 31.459240000001955 -13.648459999998522, 31.417090000000826 -13.661639999998442, 31.378860000000714 -13.677489999998215, 31.33104000000094 -13.691099999998187, 31.291030000002138 -13.706289999998262, 31.260850000000573 -13.718199999999342, 31.227160000002186 -13.731539999998859, 31.194460000000618 -13.741749999999229, 31.161400000000867 -13.751289999998335, 31.13152000000082 -13.761449999998149, 31.116750000001048 -13.766179999998712, 31.092210000000705 -13.722829999998794, 31.08274000000165 -13.726779999999053, 31.06695000000218 -13.733929999998509, 31.05927000000156 -13.739239999998972, 31.05442000000221 -13.744149999998626, 31.0509800000018 -13.749369999997725, 31.047210000000632 -13.755629999997836, 31.044420000001992 -13.75774999999885, 31.044420000001992 -13.758089999999356, 31.040530000002036 -13.758159999999407, 31.036270000002332 -13.756859999997687, 31.028150000001915 -13.758019999999306, 31.019290000002 -13.75713999999789, 31.01184000000103 -13.756219999999303, 31.00720000000183 -13.753889999998137, 31.003590000002077 -13.749809999999343, 30.998520000001008 -13.744039999997767, 30.993170000001555 -13.741719999998168, 30.982900000000882 -13.741199999998571, 30.97226000000228 -13.739989999998215, 30.967290000002322 -13.738689999998314, 30.958420000000842 -13.737459999998464, 30.948060000000623 -13.732119999998758, 30.94517000000087 -13.72907, 30.940820000001622 -13.723619999998846, 30.93674000000101 -13.713349999998172, 30.93800000000192 -13.705059999998412, 30.93851000000177 -13.694719999997687, 30.940240000001722 -13.691189999997732, 30.94192000000112 -13.687759999998889, 30.943200000001525 -13.680849999998827, 30.949360000002343 -13.670069999998304, 30.951710000001185 -13.663479999999254, 30.95292000000154 -13.652439999998023, 30.95528000000195 -13.646879999998418, 30.952730000000884 -13.642789999998058, 30.949860000000626 -13.640079999999216, 30.94764000000214 -13.63528999999835, 30.946530000001076 -13.632199999998193, 30.948590000001786 -13.62942, 30.954170000000886 -13.625189999998838, 30.956230000001597 -13.621709999999439, 30.955870000001596 -13.621369999998933, 30.95937000000231 -13.619589999998425, 30.959360000000743 -13.619239999998172, 30.9614300000012 -13.616449999997712, 30.961350000001403 -13.611979999997857, 30.960880000002362 -13.606119999998555, 30.956770000000688 -13.594129999997676, 30.957220000002053 -13.58068, 30.95868000000155 -13.56445999999778, 30.96100000000115 -13.556149999998524, 30.96230000000105 -13.550619999998162, 30.959030000001803 -13.545849999998609, 30.954350000001796 -13.54109999999855, 30.95180000000073 -13.536999999998443, 30.94999000000098 -13.5353099999993, 30.946960000001127 -13.524329999998372, 30.94793000000209 -13.519149999998263, 30.949910000001182 -13.512219999998706, 30.949070000000575 -13.505, 30.947510000001785 -13.497439999999187, 30.94774000000143 -13.490889999999126, 30.949710000000778 -13.4825899999978, 30.95206000000144 -13.475999999998749, 30.94945000000189 -13.468799999998737, 30.94818000000123 -13.457799999998315, 30.950160000002143 -13.450189999997747, 30.95633000000089 -13.440439999998489, 30.968260000001465 -13.435759999998481, 30.980630000001838 -13.436589999999342, 30.997330000001966 -13.441479999997682, 31.020730000002004 -13.445919999998296, 31.03176000000167 -13.449179999997796, 31.039910000001328 -13.450769999997647, 31.043430000001536 -13.44966999999815, 31.045160000001488 -13.447919999998703, 31.048250000001644 -13.443389999998544, 31.050850000001446 -13.431629999999132, 31.05471000000216 -13.411919999998645, 31.06518000000142 -13.38727999999901, 31.069150000001173 -13.373419999998077, 31.079210000001694 -13.345339999998032, 31.08998000000065 -13.318619999998191, 31.098480000000563 -13.301589999999123, 31.104200000001583 -13.28700999999819, 31.10924000000159 -13.27382999999827, 31.1163800000013 -13.259929999998349, 31.121020000002318 -13.244689999997718, 31.13090000000193 -13.22624999999789, 31.14046000000235 -13.209889999998268, 31.149820000002364 -13.201109999998152, 31.15672000000086 -13.193069999999352, 31.16247000000112 -13.180559999998877, 31.16853000000083 -13.165639999999257, 31.174820000002 -13.144509999998263, 31.177490000001853 -13.136869999998453, 31.183610000001863 -13.125049999998737, 31.187000000001717 -13.11844999999812, 31.19069000000127 -13.108729999998104, 31.196360000001732 -13.092429999998785, 31.20035000000098 -13.079959999999119, 31.20267000000058 -13.072339999998803, 31.20738000000165 -13.060879999999088, 31.210760000001756 -13.053589999997712, 31.214520000001357 -13.047319999997853, 31.225970000001325 -13.038159999998243, 31.233610000001136 -13.031819999998334, 31.240570000001753 -13.027219999998124, 31.245420000001104 -13.022999999999229, 31.249590000001263 -13.019469999999274, 31.25402000000213 -13.012159999998403, 31.25597000000198 -13.003849999999147, 31.25890000000072 -12.991739999997662, 31.26282000000174 -12.976159999998345, 31.267400000000634 -12.958509999998569, 31.271120000001247 -12.94510999999875))",
                        "selectedregionname": "Zambia - South Luangwa - National Park",
                        "disclaimerObjPosition": "0,611",
                        "disclaimerObjContent": "",
                        "logosObjPosition": "434,583",
                        "logosObjContent": "[]",
                        "showObjects": 'false',
                        "showtoolbar": 'true'}]
        }
        workspace = webpy_esapp_helpers.saveWorkspace(params)
        print(workspace)
        self.assertEqual(1, 1)

    def test_UpdateGraphProperties(self):
        params = {
            'graphproperty': {
                'graph_height': "800",
                'graph_subtitle': "",
                'graph_subtitle_font_color': "#808080",
                'graph_subtitle_font_size': "22",
                'graph_title': "",
                'graph_title_font_color': "#000000",
                'graph_title_font_size': 24,
                'graph_tpl_id': "-1",
                'graph_type': "xy",
                'graph_width': "1000",
                'legend_font_color': "#000000",
                'legend_font_size': "18",
                'legend_position': "",
                'xaxe_font_color': "#000000",
                'xaxe_font_size': "22"
            }
        }
        extraparams = {
            'userid': 'jurvtk',
            'graph_tpl_name': 'default',
            'istemplate': 'false',
            'graph_tpl_id': -1
        }

        return webpy_esapp_helpers.updateGraphProperties(params, extraparams)

    def test_saveMapTemplate(self):
        params = {
            'newtemplate': 'false',
            'userid': 'jurvtk',
            'map_tpl_id': 1,
            'map_tpl_name': '10 Day RFE_LTA - 2.0',
            'istemplate': 'true',
            'mapviewPosition': '20, 20',
            'mapviewSize': '800, 700',
            'productcode': 'chirps - dekad',
            'subproductcode': '10davg',
            'productversion': '2.0',
            'mapsetcode': 'CHIRP - Africa - 5km',
            'legendid': 75,
            'legendlayout': 'vertical',
            'legendObjPosition': '0, 47',
            'showlegend': 'true',
            'titleObjPosition': '77, 0',
            'titleObjContent': '< div > < span style = "color:rgb(0,0,0); font-size: 20px; font-weight: bold;" > {selected_area} < / span > < / div > < div > < span style = "color:rgb(0,0,0); font-size: 20px;" > {product_name} < / span > < / div > < div > < span style = "color:rgb(51,102,255); font-size: 20px;" > {product_date} < / span > < / div >',
            'disclaimerObjPosition': '267, 582',
            'disclaimerObjContent': 'Disclaimer',
            'logosObjPosition': '437, 561',
            'logosObjContent': [{"src": "resources/img/logo/MESA_h110.jpg", "width": "65", "height": "50"},
                                {"src": "resources/img/logo/AUC_h110.jpg", "width": "65", "height": "50"},
                                {"src": "resources/img/logo/ACP_h110.jpg", "width": "65", "height": "50"},
                                {"src": "resources/img/logo/logo_en.gif", "width": "65", "height": "50"}],
            'showObjects': 'true',
            'showtoolbar': 'true',
            'showgraticule': 'false',
            'scalelineObjPosition': '109, 591',
            'vectorLayers': '33, 10',
            'outmask': 'false',
            'outmaskFeature': '',
            'auto_open': 'false',
            'zoomextent': '4.08935546875, -37.62817382812499, 52.307128906249986, 0.030517578125',
            'mapsize': '790, 617',
            'mapcenter': '28.198242187499993, -18.798828124999996'

        }

        maptemplates = webpy_esapp_helpers.saveMapTemplate(params)
        print(maptemplates)
        self.assertEqual(1, 1)

    def test_Workspace(self):
        crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
        userinfo = {'userid': 'jurvtk', 'isdefault': True}
        defaultworkspace = crud_db.read('user_workspaces', **userinfo)
        if hasattr(defaultworkspace, "__len__") and defaultworkspace.__len__() > 0:
            defaultworkspaceid = defaultworkspace[0]['workspaceid']
        else:
            userdefaultworkspace = {
                'userid': 'jurvtk',
                'workspacename': 'default',
                'isdefault': True
            }
            if crud_db.create('user_workspaces', userdefaultworkspace):
                defaultworkspace = crud_db.read('user_workspaces', **userinfo)
                defaultworkspaceid = defaultworkspace[0]['workspaceid']

        print(defaultworkspaceid)

    def test_getGraphTimeseries(self):
        params = {
            "graphtype": 'xy',
            'selectedTimeseries': '[{"productcode": "vgt-ndvi", "version": "sv2-pv2.1", "subproductcode": "ndvi-linearx2", ' + \
                                  '"mapsetcode": "SPOTV-Africa-1km", "date_format": "YYYYMMDD", ' + \
                                  '"frequency_id": "e1dekad", "cumulative": "false", "difference": "false", ' + \
                                  '"reference": "false", "colorramp": "false", "legend_id": "null", "zscore": "false"}, ' + \
                                  '{"productcode": "vgt-ndvi", "version": "sv2-pv2.1", ' + \
                                  '"subproductcode": "10davg-linearx2", "mapsetcode": "SPOTV-Africa-1km", ' + \
                                  '"date_format": "MMDD", "frequency_id": "e1dekad", "cumulative": "false", ' + \
                                  '"difference": "false", "reference": "false", "colorramp": "false", "legend_id": "null", "zscore": "false"}, ' + \
                                  '{"productcode": "chirps-dekad", "version": "2.0", "subproductcode": "10d", ' + \
                                  '"mapsetcode": "CHIRP-Africa-5km", "date_format": "YYYYMMDD", ' + \
                                  '"frequency_id": "e1dekad", "cumulative": "false", "difference": "false", ' + \
                                  '"reference": "false", "colorramp": "false", "legend_id": "null", "zscore": "false"}, ' + \
                                  '{"productcode": "chirps-dekad", "version": "2.0", "subproductcode": "10davg", ' + \
                                  '"mapsetcode": "CHIRP-Africa-5km", "date_format": "MMDD", "frequency_id": "e1dekad", ' + \
                                  '"cumulative": "false", "difference": "false", "reference": "false", "colorramp": "false", ' + \
                                  '"legend_id": "null", "zscore": "false"}] ',
            'yearTS': "",
            'tsFromPeriod': "",
            'tsToPeriod': "",
            'yearsToCompare': "[2017]",
            'tsFromSeason': "",
            'tsToSeason': "",
            'WKT': "POLYGON((16.74152372288516 -9.266614142688914, 16.74152372288516 -8.839151632855637, 16.314061213051883 -8.839151632855637, 16.314061213051883 -9.266614142688914, 16.74152372288516 -9.266614142688914))"
        }
        ts = webpy_esapp_helpers.getGraphTimeseries(params)
        print(ts)
        self.assertEqual(1, 1)

    def test_ProductNavigatorDataSets(self):
        products = webpy_esapp_helpers.ProductNavigatorDataSets()
        print(products)
        self.assertEqual(1, 1)

    def test_getDataSets(self):
        datasets = webpy_esapp_helpers.getDataSets(True)
        self.assertEqual(1, 1)

    def test_DataSets(self):
        datasets = webpy_esapp_helpers.DataSets()
        print(datasets)
        self.assertEqual(1, 1)

    def test_TimeseriesProducts(self):
        tsproducts = webpy_esapp_helpers.TimeseriesProducts()
        # print tsproducts
        self.assertEqual(1, 1)

    def test_getAllColorSchemes(self):
        result = webpy_esapp_helpers.getAllColorSchemes()
        self.assertEqual(1, 1)

    def test_getProcessing(self):
        result = webpy_esapp_helpers.getProcessing(True)
        self.assertEqual(1, 1)

    def test_GetLegends(self):
        result = webpy_esapp_helpers.GetLegends()
        self.assertEqual(1, 1)

    def test_SaveLegend(self):
        params = {
            'legendid': -1,
            'legend_descriptive_name': 'TESTING CREATE NEW LEGEND',
            'title_in_legend': 'TEST',
            'minvalue': 0,
            'maxvalue': 3,
            'legendClasses': [
                {"legend_id": -1, "from_step": 0, "to_step": 1, "color_rgb": "255 0 0", "color_label": "1",
                 "group_label": "", "id": -1},
                {"legend_id": -1, "from_step": 1, "to_step": 2, "color_rgb": "255 0 100", "color_label": "2",
                 "group_label": "", "id": -2},
                {"legend_id": -1, "from_step": 2, "to_step": 3, "color_rgb": "255 0 255", "color_label": "3",
                 "group_label": "", "id": -3}]
        }
        result = webpy_esapp_helpers.SaveLegend(params)
        self.assertEqual(1, 1)

    def test_DeleteLegend(self):
        params = {
            'legend': {
                'colourscheme': "JUR <table cellspacing=0 cellpadding=0 width=100%><tr></tr></table>",
                'id': -223,
                'legend_descriptive_name': "JUR Test legend",
                'legendid': 232,
                'legendname': "JUR",
                'maxvalue': 3,
                'minvalue': 0
            }
        }
        result = webpy_esapp_helpers.DeleteLegend(params)
        self.assertEqual(1, 1)

    def test_CopyLegend(self):
        params = {
            'legendid': 237,
            'legendname': "test legend"
        }
        result = webpy_esapp_helpers.copyLegend(params)
        self.assertEqual(1, 1)

    def test_AssignLegends(self):
        params = {
            'productcode': 'vgt-ndvi',
            'productversion': 'sv2-pv2.1',
            'subproductcode': 'ndvi-linearx2',
            'legendids': [81, 144]
        }
        result = webpy_esapp_helpers.AssignLegends(params)
        self.assertEqual(1, 1)

    def test_GetAssignedDatasets(self):
        params = {
            'legendid': 111
        }
        assigneddatasets_json = webpy_esapp_helpers.GetAssignedDatasets(params['legendid'])
        self.assertEqual(1, 1)

    def test_GetProductLayer(self):

        date = '20181112'
        params = {
            'productcode': 'pml-modis-sst',
            'productversion': '3.0',
            'subproductcode': 'sst-fronts',
            'mapsetcode': 'SPOTV-IOC-1km',
            'date': date,
            'WIDTH': '256',
            'HEIGHT': '256',
            'BBOX': "-11.25, 53.4375, -8.4375, 56.25",
            'CRS': "EPSG:4326",
            'legendid': "136"
        }

        # date = '20180625'  # uncompressed with piramid (adds .ovr file)
        # date = '20180701'
        # params = {
        #     'productcode': 'chirps-dekad',
        #     'productversion': '2.0',
        #     'subproductcode': '1moncum',
        #     'mapsetcode': 'CHIRP-Africa-5km',
        #     'date': date,
        #     'WIDTH': '0',
        #     'HEIGHT': '1024',
        #     'BBOX': "-40, -30, 40, 75",
        #     'CRS': "EPSG:4326",
        #     'legendid': "67"
        # }
        # params = {
        #     'productcode': 'modis-chla',
        #     'productversion': 'v2013.1',
        #     'subproductcode': 'chla-day',
        #     'mapsetcode': 'MODIS-Africa-4km',
        #     'date': date,
        #     'WIDTH': '256',
        #     'HEIGHT': '256',
        #     'BBOX': "-45,-22.5,-22.5,0",
        #     'CRS': "EPSG:4326",
        #     'legendid': "211"
        # }
        #
        # params = {
        #     'productcode': 'modis-chla',
        #     'productversion': 'v2013.1',
        #     'subproductcode': 'chla-day',
        #     'mapsetcode': 'MODIS-Africa-4km',
        #     'date': date,
        #     'WIDTH': '0',
        #     'HEIGHT': '1024',
        #     'BBOX': "-40, -30, 40, 75",  # "-30, -40, 40, 75", Lat min, Lon min , Lat max, Lon max, (llx, lly, urx, ury)
        #     'CRS': "EPSG:4326",
        #     'legendid': "211"
        # }
        # params = {
        #     'productcode': 'vgt-ndvi',
        #     'productversion': 'sv2-pv2.2',
        #     'subproductcode': 'ndv',
        #     'mapsetcode': 'SPOTV-Africa-1km',
        #     'date': date,
        #     'WIDTH': '1024',
        #     'HEIGHT': '1024',
        #     'BBOX': "-30, -40, 75, 40",  # Lon min , Lat min, Lon max, Lat max (llx, lly, urx, ury)
        #     'CRS': "EPSG:4326",
        #     'legendid': "9"
        # }
        #
        # params = {
        #     'productcode': 'pml-modis-sst',
        #     'productversion': '3.0',
        #     'subproductcode': 'sst-fronts',
        #     'mapsetcode': 'SPOTV-IOC-1km',
        #     'date': '20150517',
        #     'WIDTH': '256',
        #     'HEIGHT': '256',
        #     'BBOX': "-22.5,36.5625,-19.6875,39.375",
        #     'CRS': "EPSG:4326",
        #     'legendid': "136"
        # }

        # vals = params['BBOX'].split(',')
        # ratio = (float(vals[3]) - float(vals[1])) / (float(vals[2]) - float(vals[0]))  # ratio width/height (X/Y)
        # params['WIDTH'] = str(int(float(params['HEIGHT']) * ratio))

        result = webpy_esapp_helpers.getProductLayer(params)
        # print (result)
        # Copy the file for analysis in Windows
        command = 'cp ' + result + ' /srv/www/eStation2/Tests/mapscript/'
        os.system(command)
        self.assertEqual(1, 1)

    def test_GetTimeseriesWDGEE(self):
        params = {
            'userid': 'jurvtk',
            'istemplate': 'false',
            'graph_tpl_id': -1,
            'graph_tpl_name': 'default',
            'graphtype': 'xy',
            'selectedTimeseries': '[{"productcode": "wd-gee", "version": "1.0", "subproductcode": "occurr","mapsetcode": "WD-GEE-ECOWAS-AVG", "date_format": "YYYYMMDD","frequency_id": "e1month", "cumulative": "false", "difference": "false", "reference": "false", "colorramp": "false", "legend_id": "null", "zscore": "false"}]',
            'tsdrawprops': '[{"productcode": "wd-gee", "subproductcode": "occurr", "version": "1.0","tsname_in_legend": "LANDSAT Water Detection", "charttype": "column","color": "0 0 255", "linestyle": "null", "linewidth": 0, "yaxe_id": "WBD"}]',
            'yAxes': '',
            'yearTS': '',
            'tsFromPeriod': '',
            'tsToPeriod': '',
            'yearsToCompare': '[2018]',
            'tsFromSeason': '',
            'tsToSeason': '',
            'WKT': 'MULTIPOLYGON(((-0.751988747999974 15.061730194000063, -0.76306 15.05394, -0.787459999999896 15.03941, -0.79659 15.03311, -0.809565904999914 15.023171180000105, -0.809566943999897 15.02317038400004, -0.81274 15.02074, -0.823746302999922 15.013262512000054, -0.82375 15.013260000000102, -0.827693017999877 15.009446403000055, -0.83746 15, -0.83961 14.99792, -0.841047527999962 14.995627391000014, -0.84309 14.99237, -0.852789909999956 14.984249662, -0.85617 14.98142, -0.856953918999949 14.980616469000026, -0.880422030999966 14.956561235, -0.88415 14.95274, -0.926377175999932 14.919985027000067, -0.932305649999932 14.915386402000067, -1.01049 14.854740000000106, -1.011340773999933 14.85400699400003, -1.03498 14.83364, -1.039789999999897 14.82949, -1.06702103799995 14.807187400000032, -1.067364161999933 14.806906377000047, -1.08786 14.79012, -1.089268582999978 14.789724185000097, -1.10800615699992 14.784458889000092, -1.12860226 14.778671343000056, -1.152129999999886 14.77206, -1.182522857999913 14.764798557000091, -1.24689 14.74942, -1.25422383699987 14.74771423100006, -1.290207769999938 14.739344768, -1.31495 14.73359, -1.521090074999933 14.603764589000093, -1.521102645999918 14.60375667200006, -1.674909999999898 14.506890000000112, -1.749010266999989 14.484866724000085, -1.75768 14.48229, -1.803634359999933 14.485226473000097, -1.82153 14.48637, -1.860529999999869 14.48558, -1.88701 14.486270000000104, -1.90192 14.48821, -1.97537 14.48088, -1.975370083999962 14.480878686000068, -1.97916 14.4219, -1.987300544999897 14.295028673000061, -1.993669949999941 14.195760777000032, -1.99367 14.19576, -2.029619625999914 14.181180263000044, -2.10194 14.15185, -2.105280224999944 14.150498414000012, -2.10582 14.15028, -2.135620020999937 14.16659937800003, -2.23914 14.22329, -2.264555678999926 14.23720513200007, -2.29198 14.25222, -2.47647 14.29787, -2.525765854999975 14.256688606000097, -2.661767818999976 14.143073568000034, -2.67233 14.13425, -2.673103295999965 14.133904341000047, -2.819084127999872 14.068651707000086, -2.83703 14.060630000000103, -2.841395229999904 14.042821570000115, -2.85134828199989 14.00221701000001, -2.85135 14.00221, -2.84795 14.00143, -2.840479021999954 13.999711482000095, -2.83243 13.997860000000102, -2.832431382999943 13.997856246000069, -2.851456234999944 13.946224213000065, -2.85924983599989 13.925072960000065, -2.864026283999948 13.912110035000069, -2.878899149999882 13.871746183000084, -2.885240804999938 13.854535402000067, -2.89591 13.82558, -2.897609159999945 13.80147719300001, -2.900969056999941 13.753816602000072, -2.90304 13.724440000000115, -2.893757179 13.703794910000084, -2.892166238999891 13.700256644000063, -2.87197 13.65534, -2.876881699999927 13.653784721000065, -2.92531 13.63845, -2.93718 13.63469, -2.944106457999908 13.628573128000028, -2.94411 13.62857, -2.947278960999938 13.627979121000081, -2.95371 13.62678, -2.954359708999959 13.627210489000078, -2.955884587999918 13.628220855000095, -2.959101738999919 13.630352498000079, -2.95943 13.63057, -2.979999355999894 13.649619113000014, -2.99515 13.66365, -3.001329899999973 13.666749951000071, -3.00133 13.66675, -3.00652 13.66757, -3.017249999999876 13.66322, -3.02277 13.65759, -3.023640001999951 13.654120002000099, -3.023721112 13.653985653000078, -3.023723719999936 13.653981333000075, -3.03909 13.62853, -3.045566853 13.623572409000062, -3.045569999999884 13.62357, -3.047491690999919 13.623684386000093, -3.047491991999919 13.623684404000088, -3.05145 13.62392, -3.055254557999888 13.629205106, -3.059929531999984 13.635699350000081, -3.05993 13.6357, -3.062126518999946 13.64253389200006, -3.066429515999914 13.655921537000026, -3.06874 13.66311, -3.0829 13.67684, -3.10302 13.69368, -3.10728 13.69543, -3.111735125999871 13.695682177000023, -3.122119999999882 13.69627, -3.132070951999879 13.695699978000079, -3.13434 13.69557, -3.138990767999928 13.694152550000112, -3.14648 13.69187, -3.164890027999917 13.68697432700003, -3.168929999999875 13.6859, -3.18562 13.68533, -3.205034891999929 13.694324017000099, -3.20984 13.69655, -3.217433944999897 13.70142301300011, -3.219529920999946 13.702767995000016, -3.22893 13.7088, -3.23936 13.71249, -3.250813049999977 13.715570938000013, -3.250813767999944 13.715571131000033, -3.26159 13.71847, -3.27264 13.71824, -3.272642077999933 13.71823927300008, -3.274492951999946 13.717591467000034, -3.27964 13.71579, -3.28484 13.70626, -3.284149843999955 13.702802649000049, -3.28379 13.701, -3.283787024999953 13.700995509000094, -3.283772530999897 13.700973631000053, -3.28063 13.69623, -3.271563158999925 13.687637306000084, -3.26189 13.67847, -3.258002910999892 13.672475955000081, -3.2563 13.66985, -3.255438597999898 13.654257163000068, -3.25512 13.64849, -3.258269999999868 13.63119, -3.25649 13.625020000000106, -3.256490097999944 13.62501753400008, -3.25725 13.60592, -3.25904 13.59094, -3.25998067799992 13.58165538200008, -3.26058 13.57574, -3.266823547999877 13.563419082000038, -3.26847 13.56017, -3.270625261999953 13.559159721000043, -3.27103 13.55897, -3.272965747999876 13.555730734000107, -3.272965865999879 13.555730537000088, -3.277717533999947 13.547779133000063, -3.278959999999898 13.5457, -3.28199984399987 13.534140594000036, -3.281999999999897 13.53414, -3.281358103999878 13.531392216, -3.276549999999872 13.51081, -3.271406528999933 13.485062657000057, -3.26969 13.47647, -3.268840420999879 13.469882017000074, -3.26289 13.42374, -3.261705759999927 13.40815713900004, -3.26125 13.40216, -3.261138423999967 13.388291492000107, -3.26098 13.3686000000001, -3.260134787999959 13.36270189300005, -3.2596 13.35897, -3.254404695999881 13.3521042900001, -3.24436 13.33883, -3.24367 13.328730000000107, -3.23847 13.31665, -3.238030512999899 13.309731222000039, -3.23777 13.30563, -3.243141693999945 13.29203262900009, -3.243999181999925 13.289862072000076, -3.244 13.28986, -3.246208279999934 13.288765, -3.256034791999923 13.283892417000061, -3.25608 13.28387, -3.266609374999945 13.282806734000118, -3.266609474999939 13.282806724000125, -3.27341 13.28212, -3.30599 13.27914, -3.309013381999875 13.278958990000078, -3.322945781999977 13.278124856000076, -3.3414 13.27702, -3.35379 13.27469, -3.37023 13.27503, -3.374786449999931 13.274448941000045, -3.37721685799994 13.274139004000062, -3.38756 13.27282, -3.39256158099991 13.27243050700001, -3.396993496999869 13.272085377000053, -3.40374 13.27156, -3.42477 13.2672, -3.431489999999883 13.26338, -3.431491576999917 13.263377070000018, -3.43487 13.2571, -3.434219999999897 13.24906, -3.425119999999879 13.23063, -3.42425516 13.225967073000092, -3.42032 13.20475, -3.419827608999952 13.197161775000069, -3.41959 13.1935, -3.420998115999964 13.185505680000105, -3.422711455999888 13.17577850700006, -3.42272 13.17573, -3.426196680999965 13.17146858200006, -3.426196697999956 13.171468562000058, -3.432955760999931 13.16318388100008, -3.43322 13.16286, -3.434056 13.162596141000023, -3.442301639999869 13.159993644000082, -3.445382344999871 13.159021308, -3.44884 13.15793, -3.4648 13.158050000000117, -3.46883 13.16003, -3.47822 13.15983, -3.480572442999971 13.160660086000064, -3.48556 13.162420000000111, -3.495716238999933 13.164596868000103, -3.49571641299994 13.16459690500011, -3.49923 13.16535, -3.532239999999888 13.17199, -3.542870414999896 13.177557494000084, -3.548214452999929 13.180356340000117, -3.55078 13.1817, -3.560424551999972 13.185624990000036, -3.57921 13.19327, -3.581256596999935 13.19518015800007, -3.58281 13.19663, -3.583533601999875 13.196922114000046, -3.586981190999921 13.19831388500009, -3.586981318999932 13.198313936, -3.59039 13.19969, -3.590682128999902 13.199768828000032, -3.59984 13.20224, -3.603482780999968 13.204502091000066, -3.60699 13.20668, -3.611453185999892 13.210017464000074, -3.612971746999932 13.21115300700005, -3.6261 13.22097, -3.66068 13.25423, -3.67144 13.262500000000102, -3.686419999999885 13.27067, -3.70655 13.27781, -3.720139984999946 13.282359691000082, -3.722646487999953 13.283198824000053, -3.722649999999874 13.2832, -3.727038095999973 13.287384325000062, -3.73514 13.29511, -3.736974911999937 13.29749426800008, -3.739717878999983 13.301058455000017, -3.739981209999911 13.301400625000085, -3.745063551999976 13.308004575000083, -3.748802902999927 13.312863454000038, -3.7647 13.33352, -3.77696 13.34543, -3.782805535999927 13.349120435000046, -3.797709999999881 13.35853, -3.808440440999902 13.36150622900007, -3.81379 13.36299, -3.820094109999928 13.362560455000079, -3.820094277999942 13.362560444000067, -3.83419 13.3616, -3.845307709999958 13.362054536000045, -3.847285069999941 13.36213537900008, -3.847949749999884 13.362162553000104, -3.847950597999954 13.362162588000018, -3.852289999999897 13.362340000000131, -3.865203536 13.366578715000102, -3.87715 13.3705, -3.892994710999943 13.374377950000067, -3.911414302999958 13.37888609600003, -3.912369999999896 13.379120000000114, -3.93091 13.37869, -3.930911613999967 13.37868979700005, -3.931635060999895 13.378598963000073, -3.946599999999876 13.37672, -3.955740368999955 13.380632719000047, -3.960766353999873 13.382784194000067, -3.96085 13.38282, -3.96753 13.38703, -3.97062722699999 13.390369275000069, -3.973799999999869 13.39379, -3.97394744499999 13.396267789000063, -3.97421 13.40068, -3.974490908999911 13.403747707000065, -3.97484 13.40756, -3.97404456299995 13.408613912, -3.97007 13.41388, -3.95827 13.42151, -3.94821 13.42312, -3.948230002999935 13.42404, -3.93758941699997 13.426864537000071, -3.91975 13.431600000000117, -3.917899424999916 13.433815287000087, -3.91564 13.43652, -3.915643861999968 13.436675234000106, -3.91584 13.44456, -3.916391773999948 13.445132116000039, -3.92018 13.44906, -3.926918699999931 13.451036319000053, -3.926918821999919 13.451036355000056, -3.939819999999884 13.45482, -3.940643521999988 13.455386890000042, -3.945043385999952 13.458415633000087, -3.94627 13.45926, -3.946270933999926 13.459261724000015, -3.946830067999912 13.460293425000032, -3.95021 13.46653, -3.949610002999975 13.47091, -3.955673626999953 13.491541530000106, -3.95679 13.49534, -3.96229 13.49935, -3.962291099999931 13.499350210000046, -3.962555630999873 13.499400766000065, -3.95839403399998 13.595064348000037, -4.010393158999875 13.697074098000087, -4.041392658999911 13.836087348, -4.092865783999912 13.897474098000032, -4.100512658999889 13.92133134800001, -4.09450478399998 13.94598572300005, -4.094519773999906 13.945977514000077, -4.114389283999969 13.935096598000044, -4.169390158999931 13.920097098000028, -4.270446033999917 13.881709223000016, -4.282659783999918 13.875692723000029, -4.300355408999906 13.874318473000102, -4.30601728399995 13.869736098000033, -4.307433283999956 13.86263334800006, -4.303894283999966 13.85713484800003, -4.298524408999924 13.84571784800005, -4.299883409999921 13.840867348000089, -4.306489158999909 13.839264223000043, -4.306502148999925 13.839264223000043, -4.317578033999922 13.839264098000044, -4.324184908999911 13.836743848000054, -4.32843078399992 13.828954098000082, -4.32843078399992 13.822996598, -4.329374658999967 13.816122973000063, -4.350786533999923 13.802283598000031, -4.363785908999915 13.791174473000126, -4.3746736599999 13.771624597000027, -4.376352658999906 13.755074973, -4.412423783999913 13.706255348000084, -4.447342033999973 13.683237973000047, -4.461969658999948 13.660680848, -4.480056283999971 13.653510098000083, -4.491091283999964 13.646541348, -4.551869783999933 13.608156598000065, -4.578265158999955 13.60348822300007, -4.578264413999875 13.60349065200009, -4.578278148999942 13.60348822300007, -4.5618466499999 13.657100348000043, -4.555721735999953 13.672156842000064, -4.5707249099999 13.66705034800006, -4.58106590899996 13.655888473000047, -4.586473908999949 13.641171473000043, -4.590502034999901 13.62829622300012, -4.605856283999969 13.62050247200007, -4.625222033999933 13.619805348000042, -4.63131015899998 13.61895559800007, -4.631311727999929 13.618957192000025, -4.631323148999968 13.61895559800007, -4.634111023999907 13.621787723000097, -4.639608023999898 13.62397834800008, -4.645923339 13.624076721000051, -4.652094283999872 13.623912973000088, -4.657651408999868 13.621872598000024, -4.659429658999926 13.620739097000111, -4.659438867999881 13.620741507000048, -4.659442648999914 13.620739097000111, -4.663311551999954 13.621751668000044, -4.67179528399987 13.618363473000016, -4.68798290899997 13.615591097000049, -4.687990599999978 13.615592005000039, -4.687995898999873 13.615591097000049, -4.734392023999902 13.621065598000044, -4.770383779999918 13.629064904000117, -4.797376659999912 13.623067723000048, -4.7973853149999 13.623068686000039, -4.7973896499999 13.623067723000048, -4.835144899999904 13.627269098000042, -4.85604852499992 13.630614348000066, -4.877388024999931 13.634067598000073, -4.878388148999903 13.691073098000047, -4.892724898999973 13.720949973000103, -4.891772898999903 13.73666147300004, -4.86939539899987 13.774553098000126, -4.883388273999913 13.82208559800003, -4.882388273999965 13.850087223000088, -4.897010023999883 13.872518348000014, -4.842390273999939 13.926094598000134, -4.854390023999912 13.966099473000085, -4.867607773999936 13.985912223000085, -4.870656774999873 14.02683422300008, -4.869844898999958 14.042585723000045, -4.881206649999967 14.062274473000087, -4.905203148999931 14.104906598000085, -4.913798781999958 14.112172327000053, -4.924114909999901 14.110352099000082, -4.935381659999962 14.100330098000057, -4.945709409999893 14.089397098000063, -4.960731033999878 14.062064348000021, -4.974813658999949 14.042020473000079, -4.988631409999897 14.02812609800003, -4.988631284999883 14.000770473000046, -4.986578409999936 13.985846973000022, -4.9855524099999 13.97590109800008, -4.9831174099999 13.954310098000107, -5.051372909999913 13.943096848000025, -5.051379772999951 13.943097855000104, -5.051385899999929 13.943096848000025, -5.126383399999895 13.954096848000049, -5.137718274999941 14.060045973000086, -5.118926773999874 14.11529322300008, -5.188135399999965 14.163511723000084, -5.197335399999901 14.260759973000077, -5.265872023999975 14.319994474000111, -5.325958898999943 14.36191447300007, -5.512377149999963 14.43614322300003, -5.665573024999901 14.530376974, -5.661751149999873 14.557778474000045, -5.621374149999951 14.588156473000083, -5.613374399999913 14.658164099000018, -5.594374774999949 14.683165599000077, -5.602375774999899 14.718168849000094, -5.607374649999883 14.760172849000071, -5.572376524999868 14.841180599000054, -5.546377779999887 14.928187285000064, -5.54672391099993 14.928143974000037, -5.546723460999885 14.928145656000083, -5.546736899999928 14.928143974000037, -5.543118899999968 14.941668849000067, -5.543106884999872 14.941665205000035, -5.54310591 14.941668849000067, -5.539562034999932 14.940593974000038, -5.528224836999897 14.936951762000035, -5.515602524999935 14.939638724000048, -5.515599693999974 14.939636561000043, -5.515589534999918 14.939638724000048, -5.507274034999966 14.93328772400001, -5.503723410999896 14.932156974000065, -5.498143274999961 14.930379769000098, -5.49041477499992 14.934312849, -5.48959002499987 14.93586122400005, -5.485481399999941 14.943573974000046, -5.479972524999937 14.94847309900004, -5.47322115 14.95086709900005, -5.463771274999885 14.952170724000098, -5.460700399999894 14.954114099000037, -5.460694703999877 14.95410948300001, -5.460687409999878 14.954114099000037, -5.454051781999937 14.94873678800009, -5.449257649999907 14.949290724, -5.439046899999909 14.962842099000113, -5.439034419999956 14.962841424000047, -5.43903391099991 14.962842099000113, -5.424883587999886 14.962076768000017, -5.417387899999909 14.963464224000063, -5.417384871999928 14.963462380000095, -5.41737491 14.963464224000063, -5.410996013999949 14.959579652000087, -5.387587024999931 14.967404724000062, -5.387578435999956 14.967403253000029, -5.387574034999943 14.967404724000062, -5.377561689999908 14.96568970300008, -5.349380398999926 14.973193474000027, -5.349369067999874 14.973193033000072, -5.3493674099999 14.973193474000027, -5.272381419999903 14.970193832000078, -5.2083845249999 15.021199349000028, -5.13638627499995 15.139210599000037, -5.100386649999905 15.193216349000068, -5.129696149999916 15.290196099000056, -5.153502898999875 15.359597974000053, -5.154464149999939 15.371006099000098, -5.159221899999949 15.381464099000041, -5.16018377499995 15.39477397500005, -5.164124274999949 15.406013599000104, -5.1668499 15.413787975000048, -5.172572149999922 15.43850709900002, -5.178291773999945 15.46132397400008, -5.185712149999915 15.474075099000046, -5.188092899999901 15.47645622400006, -5.191998773999956 15.48036297500009, -5.203608024999937 15.4861541, -5.21183015 15.4890439750001, -5.2306941499999 15.492878974000064, -5.258265773999909 15.493785100000068, -5.266969267999912 15.494734674000028, -5.302753784999908 15.493682975000056, -5.302756981999892 15.49368326300008, -5.302766774999924 15.493682975000056, -5.314080773999905 15.494701350000113, -5.330160149999898 15.496148724000065, -5.339527899999894 15.496991974000025, -5.339747149999909 15.503155099000054, -5.34165402499994 15.510760974000092, -5.345458898999908 15.51836697400006, -5.3469539 15.525813724000074, -5.349275899999896 15.537381099000058, -5.35403302499995 15.551255975000103, -5.349196024999941 15.555144974000015, -5.34850914999987 15.555933350000046, -5.345809898999903 15.559030975, -5.339036774999926 15.563895100000039, -5.333716024999973 15.569240100000073, -5.330329899999924 15.572640973999981, -5.324041024999872 15.575563974000076, -5.318236023999901 15.582364975000033, -5.31436602499997 15.586252099000049, -5.309529024999961 15.589655975000042, -5.304206774999955 15.595486100000059, -5.301304899999934 15.59937097500007, -5.298401773999984 15.60131710000006, -5.294531774999967 15.603264975000045, -5.288726774999901 15.609095975000045, -5.284373024999979 15.614924100000067, -5.279051774999971 15.61929910000002, -5.273731023999915 15.623674098999984, -5.272225774999981 15.62532284999999, -5.268408773999909 15.629504099000016, -5.265010399999937 15.632298474000024, -5.263088024999945 15.633879100000073, -5.257766774999936 15.639708974000044, -5.256314899999893 15.643105975000012, -5.254769399999901 15.644517600000015, -5.254448274999902 15.644810975000055, -5.2537111499999 15.645484225000061, -5.25099377399988 15.647965975000048, -5.244221774999914 15.654769100000024, -5.239868024999936 15.66011197500005, -5.235029899999915 15.66400110000005, -5.230460149999914 15.669508100000073, -5.230400926999891 15.669563780000047, -5.230180034999933 15.669829975000042, -5.228942035999978 15.67093539400004, -5.228696649999932 15.671166100000036, -5.226302898999933 15.674855975000057, -5.226295960999892 15.674846647999985, -5.226289909999934 15.674855975000057, -5.224606909999949 15.672593475, -5.222923784999949 15.670330975000027, -5.220021909999929 15.668882974000027, -5.218086909999954 15.66840310000002, -5.213249909999945 15.66405097500008, -5.209864785 15.659210975000107, -5.207447034999973 15.656792098999986, -5.203577034999967 15.656317100000038, -5.201400534999891 15.65341297400009, -5.199223909999944 15.650508974000061, -5.193420034999946 15.646158974000016, -5.190518034999911 15.645195975000021, -5.183746784999926 15.638425100000049, -5.179877909999902 15.636009975000078, -5.171873034999976 15.628598975000088, -5.166818909999961 15.62391997499999, -5.163916909999926 15.62295697399999, -5.161740034999923 15.620416224000095, -5.155214950999977 15.612800544000052, -5.1542571499999 15.613282974000086, -5.154253132999884 15.613278454000053, -5.154244159999934 15.613282974000086, -5.150374159999927 15.60892897400008, -5.137026409999976 15.59474772500009, -5.123926716999932 15.59147286400001, -5.113207274999951 15.592690349000023, -5.053646774999947 15.59945509900011, -5.040102898999947 15.60045597500006, -5.024625024999949 15.60049197500011, -5.016084024999913 15.603856975000085, -4.993725898999969 15.604225100000079, -4.993725650999949 15.604224890000054, -4.993712909999971 15.604225100000079, -4.988816909999969 15.600088975000048, -4.986987409999927 15.60003759900006, -4.974804034999948 15.599695725000018, -4.97285491 15.599640975000042, -4.970920968999934 15.598676003000023, -4.955455024999878 15.598710973999985, -4.955454973999963 15.598710945000093, -4.955442034999948 15.598710973999985, -4.952055909999899 15.596780099000014, -4.939480034999974 15.596323975000118, -4.936093784999912 15.594392975000048, -4.933683682999913 15.591015692000028, -4.931754024999947 15.594886974000062, -4.931741467999871 15.594886104000082, -4.931741034999931 15.594886974000062, -4.918196783999974 15.59394897500006, -4.912392988999926 15.591538007000068, -4.909987023999975 15.591544100000036, -4.909987026999886 15.591544067000044, -4.909974034999976 15.591544100000036, -4.91004478399995 15.59071047499999, -4.910688789999966 15.583121975000054, -4.904654024999957 15.584433100000084, -4.903691899999956 15.58515335, -4.897832397999906 15.591503853000077, -4.896492148999926 15.593654100000023, -4.893392148999936 15.594654224000081, -4.893387913999959 15.594651400000018, -4.893379159999938 15.594654224000081, -4.890087077999965 15.59245917, -4.888192274999938 15.594354225000032, -4.887992274999903 15.596154474000045, -4.884492398999953 15.598254600000061, -4.878792524999881 15.59845460000001, -4.878792060999928 15.59845416000006, -4.878779534999978 15.59845460000001, -4.876879534999887 15.596654475000022, -4.87957941 15.591953975000038, -4.878779825999914 15.589255129000023, -4.878760620999913 15.589257275, -4.866079659999968 15.591653974000067, -4.860879783999962 15.591253975000015, -4.847380159999886 15.586253474000088, -4.68839103199997 15.57825348300004, -4.662609273999919 15.580095600000035, -4.658095398999933 15.580418223999985, -4.658083398999906 15.580757100000042, -4.622933773999961 15.58293060000004, -4.536734648999868 15.589076349000052, -4.482783773999955 15.607001099000072, -4.455180398999971 15.627241099000074, -4.447562648999934 15.640541349, -4.445658148999911 15.655217725000014, -4.44932556699996 15.658749782000044, -4.44375377399993 15.669894099000018, -4.435421898999948 15.681130224000057, -4.42709014899998 15.692366350000086, -4.411854398999964 15.697411849, -4.411845383999918 15.697410533000081, -4.411841409999937 15.697411849, -4.396129783999896 15.695118600000072, -4.377637159999949 15.679225225, -4.367376283999903 15.65935135000008, -4.35044871599996 15.649756342000032, -4.337177898999897 15.65455185000009, -4.328570148999916 15.67732309899999, -4.297536898999937 15.711794350000034, -4.281303273999953 15.727420974999987, -4.268412523999899 15.732936474999988, -4.251881898999926 15.742430350000106, -4.243880023999907 15.743828600000072, -4.237356147999947 15.747685849, -4.230206273999897 15.752022350000075, -4.217124648999942 15.76353247500002, -4.214981649 15.771098225000046, -4.213791773999958 15.777058724000014, -4.207125898999891 15.77980997499999, -4.207118669999915 15.779807598000062, -4.207112909999978 15.77980997499999, -4.197356638999906 15.776601869000032, -4.185939273999907 15.777975850000033, -4.166389772999906 15.786644725000016, -4.1356953989999 15.806914724, -4.135407398999973 15.807275725000025, -4.054409147999905 15.81727585000003, -4.054408743999943 15.817274296000065, -4.054396158999964 15.81727585000003, -4.050820158999954 15.80352259900009, -4.026750658999902 15.753840850000088, -4.024094658999957 15.734346099, -4.002396033999901 15.720941850000017, -3.961677908999889 15.703008224000044, -3.948347033999937 15.688793849000078, -3.930214533999958 15.680528100000046, -3.913979772999966 15.680527101000067, -3.913966783999939 15.680527100000077, -3.904907033999962 15.676152724000062, -3.895276157999888 15.669117099000047, -3.891955158999906 15.651209474000026, -3.874364533999909 15.616421099000021, -3.85700078399995 15.595956225000052, -3.851933908999939 15.589820724, -3.842887158999872 15.584082225000017, -3.835983283999923 15.574901349000058, -3.839078158999911 15.56571947400009, -3.851456907999903 15.551488100000043, -3.86273765899989 15.546007475000081, -3.873287283999957 15.530071975000055, -3.870688408999939 15.51492847400003, -3.871551533999963 15.514088100000052, -3.868562157999975 15.51017534900005, -3.863459033999987 15.505630849000084, -3.85459760599997 15.504366591000107, -3.840971523999912 15.505335974000019, -3.83026152399998 15.5089285990001, -3.830253178999925 15.50892704100005, -3.830248533999963 15.5089285990001, -3.82197890899991 15.507384599000062, -3.815185532999948 15.506147100000078, -3.81141265899987 15.500641724000019, -3.80471578399991 15.495704599000078, -3.795250870999894 15.492104647000119, -3.787318398999929 15.494472224000077, -3.787312418999875 15.494470132000089, -3.787305408999913 15.494472224000077, -3.781802158999938 15.492546599000093, -3.774702283999943 15.492046600000023, -3.770605709999899 15.4897482020001, -3.763815522999948 15.491046474000044, -3.763811659999902 15.49104472900008, -3.76380253399995 15.491046474000044, -3.757602658999872 15.488246225000083, -3.753414814999957 15.488046798000013, -3.744215897999908 15.493546725000058, -3.74420313199991 15.493546592000058, -3.74420290899999 15.493546725000058, -3.734703157999917 15.493447725000038, -3.705104202999962 15.490446642000066, -3.675517398999943 15.490546600000073, -3.675517215999918 15.490546557000073, -3.675504408999927 15.490546600000073, -3.668304533999901 15.488846475000102, -3.658014059999971 15.483551748000053, -3.652602898999874 15.490507600000043, -3.646627022999894 15.49785835000003, -3.637331149 15.507445224000023, -3.597418147999917 15.536250099, -3.570731772999977 15.575237850000079, -3.561304022999906 15.615782725000045, -3.551012272999969 15.632720350000014, -3.537068522999903 15.637833849000074, -3.5101762729999 15.68577147400002, -3.48242189799987 15.730269724000053, -3.482409595999911 15.730268620000047, -3.48240890799994 15.730269724000053, -3.453060532999928 15.72763647500004, -3.424748033999919 15.726819474000038, -3.39517265799995 15.712150225000087, -3.368407396999885 15.698857079000035, -3.3564643979999 15.701730225000077, -3.350820522999925 15.70971597400002, -3.334124897999914 15.723152349000017, -3.334113478999939 15.723151084, -3.334111907999898 15.723152349000017, -3.307990113999949 15.7202591610001, -3.296704772999931 15.72377247499999, -3.298364772999889 15.739105849000012, -3.304072647999902 15.7575316, -3.300256772999944 15.769449724000069, -3.300828772999921 15.776667474000064, -3.308633647999898 15.780343850000023, -3.313614522999899 15.784021099000014, -3.320754397999934 15.78657935000011, -3.323725397999908 15.79057572500001, -3.317289522999971 15.800121600000082, -3.314633522999941 15.810344600000022, -3.309320647999897 15.81960847400002, -3.305062772999946 15.827166225000084, -3.296013022999915 15.831841725000046, -3.291614022999909 15.835505975000089, -3.283425272999949 15.836540100000022, -3.278113397999931 15.84101260000007, -3.274129522999885 15.853790850000067, -3.296324022999954 15.869465225000042, -3.298943022999936 15.884814725000055, -3.294420147999915 15.895181725000029, -3.286325272999903 15.897930975000051, -3.286317371999871 15.897929247000079, -3.286312282999916 15.897930975000051, -3.275838532999899 15.895639725, -3.266315783999971 15.886020850000037, -3.260602782999968 15.871362475000083, -3.245575157999951 15.858910349999988, -3.236569282999881 15.857351225000045, -3.230505407999885 15.85703322400012, -3.22264052299991 15.85703322400012, -3.20960189799996 15.860169600000077, -3.209590615999929 15.860169189000047, -3.209588907999944 15.860169600000077, -3.198242157999914 15.859756475, -3.191354282999953 15.857461350000094, -3.186759282999901 15.852298850000082, -3.189341283999937 15.840485725000079, -3.188793282999882 15.83270697500005, -3.193018157999973 15.827494475000051, -3.19274615799992 15.821743975000047, -3.186616783999938 15.817818560999982, -3.168327647999973 15.81934872500004, -3.105019897999966 15.825696475000072, -3.100592022999905 15.834931350000048, -3.101084022999913 15.84652947500011, -3.098132147999934 15.861680849999985, -3.085340397999971 15.863574100000037, -3.085337687999925 15.863572579, -3.085327407999984 15.863574100000037, -3.073519657999896 15.856945475000046, -3.067615782999923 15.835165475000068, -3.054343834999941 15.83303911600008, -3.043508272999929 15.850298975000058, -3.034938521999891 15.86862472500006, -3.019487772999923 15.879985850000011, -3.010181022999944 15.896113350000022, -3.010169176999938 15.896111367000046, -3.010168032999928 15.896113350000022, -2.988266532999944 15.892447975000053, -2.978744657999925 15.867708725000014, -2.959700032999876 15.85396447500004, -2.953741032999943 15.824236600000077, -2.939132281999917 15.793525725000038, -2.921869657999878 15.765374099, -2.888669282999928 15.735943350000085, -2.850157907999915 15.709070974000028, -2.820941532999882 15.665563849000037, -2.83820590799999 15.581109850000118, -2.820941157999869 15.512010349000079, -2.727982906999898 15.414759225000125, -2.597425532999921 15.366236849000103, -2.532427782999918 15.319231599000034, -2.450429407999934 15.301229974000037, -2.308339281999906 15.28040022400009, -2.134385612999949 15.272723496000054, -2.012210396999905 15.327746475000055, -1.9073007719999 15.39940547400002, -1.817455646999974 15.423242850000037, -1.686457395999923 15.428243599000098, -1.686456307999919 15.428243145000053, -1.686444406999925 15.428243599000098, -1.502874030999976 15.351619724000017, -1.395938030999901 15.288802974000077, -1.305451780999931 15.260228475000048, -1.21445353099989 15.176220599, -1.160958281 15.034716224000022, -1.07729357799991 14.99632803200008, -1.07729290599994 14.996327724000054, -0.975039030999937 14.998887224000086, -0.751988747999974 15.061730194000063)))'
        }
        webpy_esapp_helpers.getGraphTimeseries(params)
        self.assertEqual(1, 1)
