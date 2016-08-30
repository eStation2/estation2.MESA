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

    if TotSteps >= 25:
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
        # legend_dict = functions.row2dict(row)
        LegendName = row['legend_name']

    legendHeader = '<b style="font-size:12px;">'+LegendName+'</b>'

    legendTableBegin = '<table' + tableStyle + '> '

    legendGroupLabels = ''
    if TotGroupLabels > 0:
        legendGroupLabels = '<tr>'
        PrevGroupLabel = ''
        Counter = 0
        for row in legend_steps:
            GroupLabel = row.group_label
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
    skipcolumns = 0
    ColSpan = ColumnSpan
    if ColumnSpan > 15:
        ColSpan = 10
    labelcounter = 0
    rowcounter = 0
    # ColSpan = 5
    for row in legend_steps:
        rowcounter += 1
        if row.color_label != None and row.color_label.strip() != '':
            labelcounter += 1
            if labelcounter == TotColorLabels:
                ColSpan = TotSteps - rowcounter
            legendColorLabels += '<td colspan="' + str(int(ColSpan)) + '" style="font-size:9px; line-height:10px; max-width:30px;" align="left">'+row.color_label+'</td>'
            # legendColorLabels += '<td colspan="' + str(int(ColSpan)) + '" height=25px; valign="top" style="font-size:9px; ">'\
            #                      + '<span style="top: 0; display: block; transform: rotate(90deg); -ms-transform: rotate(90deg);  -webkit-transform: rotate(90deg); white-space: nowrap;" >'\
            #                      + row.color_label\
            #                      + '</span>'\
            #                      + '</td>'
            skipcolumns = int(ColSpan-1)
        elif skipcolumns > 0:
            skipcolumns -= 1
        else:
            legendColorLabels += '<td width="1px;"></td>'

        # legendstep_dict = functions.row2dict(row)
        # if legendstep_dict['color_label'].strip() != '':
        #     # ColorLabel = '&nbsp;'+legendstep_dict['color_label']+'&nbsp;'
        #     legendColorLabels += '<td colspan="' + str(ColumnSpan) + '" style="font-size:9px; line-height:10px; max-width:30px;" align="left">'+legendstep_dict['color_label']+'</td>'

    legendColorLabels += '</tr>'

    legendTableEnd = '</table>'

    legendHTML = legendHeader + legendTableBegin + legendGroupLabels + legendColors + legendColorLabels + legendTableEnd

    # Create vertical legend
    legendHTMLVertical = ''
    legendColorLabelColumn = ''
    legendGroupLabelColumn = ''
    PrevGroupLabel = ''
    Counter = 0
    ColorLabelCounter = 1

    if TotSteps > 36:
        stepWidth = 20
        stepHeight = 1
    else:
        stepWidth = 30
        stepHeight = 20
    #
    # if stepHeight < 3:
    #     stepWidth = 20
    #     stepHeight = 1

    for row in legend_steps:

        # Add color column
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

        legendColorColumn = '<td width='+str(stepWidth)+'px; height='+str(stepHeight)+'px; style="'+border+' background-color: '+color_html+'"></td>'

        # Add label column
        Counter += 1
        if ColumnSpan > 1:
            legendColorLabelColumn = '<td height="1px;"></td>'
            if row.color_label != None and row.color_label.strip() != '':
                # legendColorLabelColumn = '<td rowspan="' + str(ColumnSpan) + '" style="font-size:9px; line-height:10px; " valign="top" align="center">'+row.color_label+'</td>'
                legendColorLabelColumn = '<td rowspan=5 style="font-size:9px; line-height:10px; " valign="top" align="center">'+row.color_label+'</td>'

            # if Counter == 1:
            #     # print ColorLabelCounter
            #     # print legend_steps[int((ColumnSpan * ColorLabelCounter)-1)]
            #     legendstep_withlabel_dict = functions.row2dict(legend_steps[int((ColumnSpan * ColorLabelCounter)-1)])
            #     if legendstep_withlabel_dict['color_label'] != '':
            #         legendColorLabelColumn = '<td rowspan="' + str(ColumnSpan-1) + '" style="font-size:9px; line-height:10px; " align="center">'+legendstep_withlabel_dict['color_label']+'</td>'
            #     # if Counter > 1:
            #     # ColorLabelCounter += 1
            # elif Counter == (int(ColumnSpan) * ColorLabelCounter):
            #     # print 'Counter: ' + str(Counter)
            #     # print 'ColumnSpan: ' + str(ColumnSpan)
            #     # print 'ColorLabelCounter: ' + str(ColorLabelCounter)
            #     # print '(int(ColumnSpan) * ColorLabelCounter): ' + str(int(ColumnSpan) * ColorLabelCounter)
            #     if TotColorLabels == ColorLabelCounter + 1:
            #         # print legend_steps[TotSteps-1]
            #         legendstep_withlabel_dict = functions.row2dict(legend_steps[TotSteps-1])
            #     else:
            #         # print legend_steps[int((ColumnSpan * (ColorLabelCounter+1))-1)]
            #         legendstep_withlabel_dict = functions.row2dict(legend_steps[int((ColumnSpan * (ColorLabelCounter+1))-1)])
            #     ColorLabelCounter += 1
            #     if legendstep_withlabel_dict['color_label'] != '':
            #         legendColorLabelColumn = '<td rowspan="' + str(ColumnSpan) + '" style="font-size:9px; line-height:10px; " align="center">'+legendstep_withlabel_dict['color_label']+'</td>'
            # else:
            #     legendColorLabelColumn = ''
        else:
            legendstep_dict = functions.row2dict(row)
            if legendstep_dict['color_label'] != '':
                # ColorLabel = '&nbsp;'+legendstep_dict['color_label'].strip()+'&nbsp;'
                legendColorLabelColumn = '<td rowspan="' + str(ColumnSpan) + '" style="font-size:9px; line-height:10px; " align="center">'+legendstep_dict['color_label']+'</td>'

        # if TotGroupLabels > 0:
        #     legendGroupLabelColumn = ''
        #     GroupLabel = row.group_label.strip()
        #     # if Counter == 0:
        #     #     Counter += 1
        #     #     PrevGroupLabel = GroupLabel
        #     if GroupLabel == PrevGroupLabel:
        #         Counter += 1
        #         PrevGroupLabel = GroupLabel
        #     else:
        #         legendGroupLabelColumn = '<td rowspan="'+str(Counter)+'"" style="font-size:9px; line-height:10px; " align="center">'+PrevGroupLabel+'</td>'
        #         PrevGroupLabel = GroupLabel
        #         Counter = 1

        legendHTMLVertical += '<tr>' + legendColorColumn + legendColorLabelColumn + legendGroupLabelColumn + '</tr>'

    legendHTMLVertical = legendHeader + legendTableBegin + legendHTMLVertical + legendTableEnd
    # print legendHTMLVertical
    legends_HTML = {'legendHTML': legendHTML, 'legendHTMLVertical': legendHTMLVertical}
    return legends_HTML