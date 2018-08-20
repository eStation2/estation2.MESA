_author__ = "Jurriaan van 't Klooster"

from config import es_constants
from apps.productmanagement.datasets import Dataset
from apps.productmanagement.products import Product
from lib.python import functions
from database import querydb
import unittest
import datetime
import webpy_esapp_helpers
import webpy_esapp
from database import crud

import plotly.plotly as py
from plotly.graph_objs import *

import StringIO
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import base64

from lib.python import es_logging as log
logger = log.my_logger(__name__)


class TestWebpy(unittest.TestCase):

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

        for attr, value in datasetcompleteness.iteritems():
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
        fig.subplots_adjust(left=0.07, right=0.95, bottom=0.15, top=0.9)    # , wspace=0.2, hspace=0.2
        # ypixels = int(yinch * fig.get_dpi())
        ax.set_ylim(0, 4)
        # plt.box(on=None)
        plt.draw()
        # buf = io.BytesIO()
        buf = StringIO.StringIO()
        plt.savefig(buf, format='png', bbox_inches=0, pad_inches=0)
        plt.savefig('/srv/www/eStation2/testmatlibplot.png', bbox_inches=0, pad_inches=0)     # bbox_inches='tight'
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
        data = Data(
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
        fig = Figure(data=data, layout=layout)
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
        print workspace
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
        print maptemplates
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

        print defaultworkspaceid

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
            'yearsToCompare':"[2017]",
            'tsFromSeason': "",
            'tsToSeason': "",
            'WKT': "POLYGON((16.74152372288516 -9.266614142688914, 16.74152372288516 -8.839151632855637, 16.314061213051883 -8.839151632855637, 16.314061213051883 -9.266614142688914, 16.74152372288516 -9.266614142688914))"
        }
        ts = webpy_esapp_helpers.getGraphTimeseries(params)
        print ts
        self.assertEqual(1, 1)

    def test_ProductNavigatorDataSets(self):
        products = webpy_esapp_helpers.ProductNavigatorDataSets()
        print products
        self.assertEqual(1, 1)

    def test_getDataSets(self):
        datasets = webpy_esapp_helpers.getDataSets(True)
        self.assertEqual(1, 1)

    def test_DataSets(self):
        datasets = webpy_esapp_helpers.DataSets()
        print datasets
        self.assertEqual(1, 1)

    def test_TimeseriesProducts(self):
        tsproducts = webpy_esapp_helpers.TimeseriesProducts()
        # print tsproducts
        self.assertEqual(1, 1)

    def test_getAllColorSchemes(self):
        result = webpy_esapp_helpers.getAllColorSchemes()
        self.assertEqual(1, 1)

    def test_getProcessing(self):
        result = webpy_esapp_helpers.getProcessing(False)
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
            'legendClasses': [{"legend_id":-1,"from_step":0,"to_step":1,"color_rgb":"255 0 0","color_label":"1","group_label":"","id":-1},
                              {"legend_id":-1,"from_step":1,"to_step":2,"color_rgb":"255 0 100","color_label":"2","group_label":"","id":-2},
                              {"legend_id":-1,"from_step":2,"to_step":3,"color_rgb":"255 0 255","color_label":"3","group_label":"","id":-3}]
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

        # date = '20180625'  # uncompressed with piramid (adds .ovr file)
        date = '20180701'
        params = {
            'productcode': 'chirps-dekad',
            'productversion': '2.0',
            'subproductcode': '1moncum',
            'mapsetcode': 'CHIRP-Africa-5km',
            'date': date,
            'WIDTH': '0',
            'HEIGHT': '1024',
            'BBOX': "-40, -30, 40, 75",
            'CRS': "EPSG:4326",
            'legendid': "67"
        }
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

        vals = params['BBOX'].split(',')
        ratio = (float(vals[3]) - float(vals[1])) / (float(vals[2]) - float(vals[0]))  # ratio width/height (X/Y)
        params['WIDTH'] = str(int(float(params['HEIGHT']) * ratio))

        result = webpy_esapp_helpers.getProductLayer(params)
        # print(result)
        # Copy the file for analysis in Windows
        command = 'cp '+result+' /srv/www/eStation2/Tests/mapscript/'
        os.system(command)
        self.assertEqual(1, 1)
