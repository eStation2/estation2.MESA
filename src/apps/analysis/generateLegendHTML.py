# import sys
# import os
# from os import sys, path
# import datetime
# import json
# from config import es_constants
# from lib.python import es_logging as log
#
# logger = log.my_logger(__name__)

from __future__ import print_function
import math
from database import querydb
from lib.python import functions


def generateLegendHTML(legend_id):
    legendHTMLHorizontal = ''
    LegendName = ''
    TotSteps = 0
    TotColorLabels = 0
    TotGroupLabels = 0
    fontSizeTitle = 22
    fontSizeLabels = 22
    legends_HTML = {'legendHTML': '', 'legendHTMLVertical': ''}

    if legend_id == None:
        return legends_HTML

    # print('legend_id: ' + str(legend_id))
    legend_info = querydb.get_legend_info(legendid=legend_id)
    if hasattr(legend_info, "__len__") and legend_info.__len__() < 1:
        return legends_HTML

    legend_steps = querydb.get_legend_steps(legendid=legend_id)
    if hasattr(legend_steps, "__len__") and legend_steps.__len__() < 1:
        return legends_HTML

    getTotSteps = querydb.get_legend_totals(legendid=legend_id)
    if hasattr(getTotSteps, "__len__") and getTotSteps.__len__() < 1:
        return legends_HTML


    for row in getTotSteps:
        TotSteps = row['totsteps']
        TotColorLabels = row['totcolorlabels']
        TotGroupLabels = row['totgrouplabels']

    if TotSteps >= 25:
        legendWidth = 750
        tableStyle = ' style="background: white; border-spacing:0px;"'
        stepWidth = legendWidth/TotSteps
        if stepWidth < 3:
            stepWidth = 1
    else:
        # tableStyle = ' style="border: 1px solid white; margin: 0px; padding: 0px; "'
        tableStyle = ' style="background: white; margin: 0px; padding: 0px; "'
        stepWidth = 50


    if TotColorLabels > 0:
        ColumnSpan = math.ceil(TotSteps/float(TotColorLabels))
    else:
        ColumnSpan = 2
    # print "ColumnSpan: "+str(ColumnSpan)

    for row in legend_info:
        # legend_dict = functions.row2dict(row)
        LegendName = row['legend_name']

    legendHeader = '<b style="line-height:26px; font-size:'+str(fontSizeTitle)+'px;">'+LegendName+'</b>'

    legendTableBegin = '<table' + tableStyle + '> '
    legendTableEnd = '</table>'


    ######################################
    # Create horizontal legend
    ######################################

    legendGroupLabels = ''
    if TotGroupLabels > 0:
        legendGroupLabels = '<tr>'
        PrevGroupLabel = ''
        Counter = 0
        for row in legend_steps:
            GroupLabel = row.group_label
            if GroupLabel is not None and GroupLabel != '':
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
            border = "border:0px solid black; "

        legendColors = legendColors + '<td width='+str(stepWidth)+'px; height=22px; style="'+border+' background-color: '+color_html+'"></td>'
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
            # legendColorLabels += '<td height=26px; colspan="' + str(int(ColSpan)) + '" style="font-size:'+str(fontSizeLabels)+'px; max-width:'+str(stepWidth+5)+'px;" line-height:26px; align="left">'+row.color_label+'</td>'
            legendColorLabels += '<td colspan="' + str(int(ColSpan)) + '" height=80px; style="font-size:'+str(fontSizeLabels)+'px; ">'\
                                 + '<div style="top: 0; display: block; transform: rotate(90deg); -ms-transform: rotate(90deg);  -webkit-transform: rotate(90deg); white-space: nowrap;" >'\
                                 + row.color_label\
                                 + '</div>'\
                                 + '</td>'
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

    legendHTMLHorizontal = legendHeader + legendTableBegin + legendGroupLabels + legendColors + legendColorLabels + legendTableEnd


    ######################################
    # Create vertical legend
    ######################################
    if TotSteps >= 25:
        stepWidth = 25
        stepHeight = 1
    else:
        stepWidth = 35
        stepHeight = 28

    mainTableBackgroundColor = 'transparent'
    fontSizeHeader = 22
    fontSizeLabels = 22
    firstColumnWidth = 35
    legendColorTableBackgroundColor = 'white'
    legendLabelTableBackgroundColor = 'white'
    extraFirstRowHeight = 12
    colorColumnWidth = 35
    colorColumnHeight = 32
    tickColumnWidth = 8
    tickColumnHeight = 32
    labelColumnHeight = 32

    mainTableBegin = '<table style="background: ' + mainTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px; ">'
    legendHeaderRow = '<tr><td colspan=2 style=""><b style=" font-size:' + str(fontSizeHeader) + 'px;">' + LegendName + '</b></td></tr>'
    legendRowBegin = '<tr>'
    firstColumnBegin = '<td width=' + str(firstColumnWidth) + 'px; style="border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;">'
    secondColumnBegin = '<td valign="top" align="left" style="border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;" >'

    legendColorTable = '<table style="background: ' + legendColorTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;">'
    legendColorTable += '<tr><td colspan=2 height=' + str(extraFirstRowHeight) + 'px; style=""></td></tr>'

    legendLabelTable = '<table style="background: ' + legendLabelTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px; ">'

    row_counter = 0
    # print('legend_steps: ' + str(legend_steps.__len__()))
    for row in legend_steps:
        row_counter += 1
        if row_counter == 1:
            bordertop = ' border-top:1px solid black; '
        else:
            bordertop = ' '

        if row_counter == legend_steps.__len__():
            borderbottom = ' border-bottom:1px solid black; '
        else:
            borderbottom = ' '

        # Add color column
        # convert row['color_rgb'] from RGB to html color
        color_rgb = row.color_rgb.split(' ')
        # color_html = functions.rgb2html(color_rgb)
        r = color_rgb[0]
        g = color_rgb[1]
        b = color_rgb[2]
        color_html = 'rgb('+r+','+g+','+b+')'

        legendColorTable += '<tr> ' + \
            '<td width='+str(colorColumnWidth)+'px; height='+str(colorColumnHeight)+'px; style="padding:0px; margin: 0px; border-left:1px solid black; '+borderbottom+bordertop+' background-color: '+color_html+'"></td>' + \
            '<td width='+str(tickColumnWidth)+'px; height='+str(tickColumnHeight)+'px; style="padding:0px; margin: 0px; border-top:1pt solid black; border-left:1px solid black; "></td>' + \
        '</tr>'

        if row.color_label == None:
            color_label = ''
        else:
            color_label = row.color_label.strip()
        legendLabelTable += '<tr><td height='+str(labelColumnHeight)+'px; style="font-size:'+str(fontSizeLabels)+'px;  padding:0px; margin: 0px; padding-left:5px;" valign="middle" align="left">'+color_label+'</td></tr>'

    legendColorTable += '</table>'
    legendLabelTable += '<tr><td height=' + str(extraFirstRowHeight) + 'px; style=""></td></tr>'
    legendLabelTable += '</table>'

    columnEnd = '</td>'
    legendRowEnd = '</tr>'
    mainTableEnd = '</table>'

    legendHTMLVertical = mainTableBegin + legendHeaderRow + legendRowBegin + firstColumnBegin + legendColorTable + columnEnd + secondColumnBegin + legendLabelTable + columnEnd + legendRowEnd + mainTableEnd
    # print legendHTMLVertical


    legends_HTML = {'legendHTML': legendHTMLHorizontal, 'legendHTMLVertical': legendHTMLVertical}
    return legends_HTML