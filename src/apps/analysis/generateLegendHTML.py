# import sys
# import os
# from os import sys, path
# import datetime
# import json
# from config import es_constants
# from lib.python import es_logging as log
#
# logger = log.my_logger(__name__)

import math
from database import querydb
from lib.python import functions


def generateLegendHTML(legend_id):
    legendHTML = ''
    LegendName = ''
    TotSteps = 0
    TotColorLabels = 0
    TotGroupLabels = 0

    legend_info = querydb.get_legend_info(legendid=legend_id)
    legend_steps = querydb.get_legend_steps(legendid=legend_id)
    getTotSteps = querydb.get_legend_totals(legendid=legend_id)

    for row in getTotSteps:
        TotSteps = row['totsteps']
        TotColorLabels = row['totcolorlabels']
        TotGroupLabels = row['totgrouplabels']
    # print "TotSteps: "+str(TotSteps)
    # print "TotColorLabels: "+str(TotColorLabels)
    # print "TotGroupLabels: "+str(TotGroupLabels)

    if TotSteps > 20:
        legendWidth=750
        tableStyle = ' style="border-spacing:0px;"'
    else:
        legendWidth=450
        tableStyle = ' style="border: 1px solid white; margin: 0px; padding: 0px; "'

    if TotSteps > 5:
        stepWidth = legendWidth/TotSteps
    else:
        stepWidth = 50

    if stepWidth < 3:
        stepWidth = 1

    if TotColorLabels > 0:
        ColumnSpan = math.ceil(TotSteps/float(TotColorLabels))
    else:
        ColumnSpan = 1
    # print "ColumnSpan: "+str(ColumnSpan)

    for row in legend_info:
        legend_dict = functions.row2dict(row)
        LegendName = legend_dict['legend_name']

    legendHeader = '<b style="font-size:12px;">'+LegendName+'</b>'

    legendTableBegin = '<table' + tableStyle + '> '

    legendGroupLabels = ''
    if TotGroupLabels > 0:
        legendGroupLabels = '<tr>'
        PrevGroupLabel = ''
        Counter = 0
        for row in legend_steps:
            GroupLabel = row['group_label']
            if GroupLabel.strip() == PrevGroupLabel:
                Counter += 1
                PrevGroupLabel = GroupLabel
            else:
                if Counter != 0:
                     legendGroupLabels += '<td colspan="'+str(Counter)+'" align="center">'+PrevGroupLabel+'</td><td rowspan="3" style="background-color: black;"><img src="resources/img/clearpixel.gif" width="1" height="15" /></td>'
                PrevGroupLabel = GroupLabel
                Counter = 1

        legendGroupLabels += '<td colspan="'+str(Counter)+'" align="center">'+PrevGroupLabel+'</td>'
        legendGroupLabels += '</tr>'

    legendColors = '<tr>'
    for row in legend_steps:
        # convert row['color_rgb'] from RGB to html color
        color_rgb = row.color_rgb.split(' ')
        color_html = functions.rgb2html(color_rgb)
        r = color_rgb[0]
        g = color_rgb[1]
        b = color_rgb[2]
        color_html = 'rgb('+r+','+g+','+b+')'

        border = ""
        if TotSteps <= 30:
            border = "border:1px solid black; "

        legendColors = legendColors + '<td width='+str(stepWidth)+'px; height=15px; style="'+border+' background-color: '+color_html+'"></td>'
    legendColors += '</tr>'

    legendColorLabels = '<tr>'
    for row in legend_steps:
        legendstep_dict = functions.row2dict(row)
        if legendstep_dict['color_label'].strip() != '':
            # ColorLabel = '&nbsp;'+legendstep_dict['color_label']+'&nbsp;'
            legendColorLabels += '<td colspan="' + str(ColumnSpan) + '" style="font-size:9px; max-width:50px;" align="center">'+legendstep_dict['color_label']+'</td>'

    legendColorLabels += '</tr>'

    legendTableEnd = '</table>'

    legendHTML = legendHeader + legendTableBegin + legendGroupLabels + legendColors + legendColorLabels + legendTableEnd
    return legendHTML