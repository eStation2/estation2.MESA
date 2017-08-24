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
    legendHTMLVertical = ''
    legendName = ''
    TotSteps = 0
    TotColorLabels = 0
    TotGroupLabels = 0
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

    for row in legend_info:
        # legend_dict = functions.row2dict(row)
        legendName = row['legend_name']


    ######################################
    # Create horizontal legend
    ######################################

    if TotSteps >= 25:
        fontSizeLabels = 20
        fontSizeTitle = 20
        # stepWidth = 28
        legendWidth = 775
        legendTableBegin = '<table style="border-spacing:0px; background:white; padding: 5px 35px 5px 5px;"> '
        legendHeader = '<tr><td colspan='+str(TotSteps)+' style="background:white; padding: 0px 5px 5px 0px; font-size:' + str(fontSizeTitle) + 'px;">' + legendName + '</td></tr>'

        if TotColorLabels > 0:
            ColumnSpan = math.ceil(TotSteps / float(TotColorLabels))
        else:
            ColumnSpan = 1

        if TotSteps > 60:
            stepWidth = legendWidth / TotSteps
        else:
            stepWidth = 50

        if stepWidth < 4:
            stepWidth = 1

        legendColors = '<tr>'
        for row in legend_steps:
            # convert row['color_rgb'] from RGB to html color
            color_rgb = row.color_rgb.split(' ')
            color_html = functions.rgb2html(color_rgb)
            r = color_rgb[0]
            g = color_rgb[1]
            b = color_rgb[2]
            color_html = 'rgb(' + r + ',' + g + ',' + b + ')'

            border = ""
            if TotSteps <= 30:
                border = "border:1px solid black; "

            legendColors = legendColors + '<td width=' + str(stepWidth) + 'px; height=15px; style="' + border + ' background-color: ' + color_html + '"></td>'
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
                legendColorLabels += '<td colspan="' + str(int(ColSpan)) + '" style="font-size:' + str(
                    fontSizeLabels) + 'px; line-height:24px; max-width:' + str(
                    stepWidth + 5) + 'px;" align="left">' + row.color_label + '</td>'
                skipcolumns = int(ColSpan - 1)
            elif skipcolumns > 0:
                skipcolumns -= 1
            else:
                legendColorLabels += '<td width="1px;"></td>'

        legendColorLabels += '</tr>'

        legendTableEnd = '</table>'

        legendHTMLHorizontal = legendTableBegin + legendHeader + legendColors + legendColorLabels + legendTableEnd
    else:
        mainTable = '<table style="background: white; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing:0px; cellpadding:0px; margin: 0px; padding: 10px; ">'
        mainTable += '<tr><td colspan=1 style="font-size:22px; line-height:24px !important;">' + legendName + '</td></tr>'   # line-height:26px;
        mainTable += '<tr><td>'
        mainTable += '<table class="table table-striped table-header-rotated">'
        mainTableBody = '<tbody>'
        colorRow = '<tr><td width=34px; height=22px;></td>'
        tickRow  = '<tr><td width=34px; height=6px;></td>'
        footer = '<tfoot><tr>'

        row_counter = 0
        for row in legend_steps:
            row_counter += 1
            if row_counter == 1:
                borderleft = ' border-left:1px solid black; '
            else:
                borderleft = ''

            borderright = ''
            absoluteMaxHeader = ''
            if row_counter == legend_steps.__len__():
                borderright = ' border-right:1px solid black; '
                if row.group_label != None and row.group_label.strip() != '':
                    absoluteMaxHeader = '<th class="rotate-45"><div><span>'+row.group_label+'</span></div></th>'

            # Add color column
            # convert row['color_rgb'] from RGB to html color
            color_rgb = row.color_rgb.split(' ')
            # color_html = functions.rgb2html(color_rgb)
            r = color_rgb[0]
            g = color_rgb[1]
            b = color_rgb[2]
            color_html = 'rgb('+r+','+g+','+b+')'

            colorRow += '<td width=34px; height=22px; style="border-top:1px solid black; ' + borderleft + borderright + ' background-color: ' + color_html + '"></td>'
            tickRow += '<td width=34px; height=6px; style="border-top:1px solid black; border-right:1px solid black; ' + borderleft + ' "></td>'
            if row.color_label == None:
                color_label = ''
            else:
                color_label = row.color_label.strip()

            footer += '<th class="rotate-45"><div><span>'+color_label+'</span></div></th>'     # style="line-height:65px !important;"
            footer += absoluteMaxHeader

        colorRow += '</tr>'
        tickRow += '</tr>'
        footer += '</tr></tfoot>'
        mainTableBody += colorRow + tickRow + '</tbody>'
        mainTable += mainTableBody + footer + '</table></td></tr></table>'
        legendHTMLHorizontal = mainTable


    ######################################
    # Create vertical legend
    ######################################
    if TotSteps >= 25:
        fontSizeLabels = 20
        fontSizeTitle = 20
        stepWidth = 28
        stepHeight = 1
        if TotSteps <= 60:
            stepHeight = 3
        elif TotSteps <= 115:
            stepHeight = 2

        mainTableBegin = '<table style="border-spacing:0px; background:white; padding:0;"> '
        mainTableEnd = '</table>'
        legendHeaderRow = '<tr><td style="background:white; padding: 5px; font-size:' + str(fontSizeTitle) + 'px;">' + legendName + '</td></tr>'
        legendTableBegin = '<table style="border-spacing:0px; background:white; padding: 5px 5px 15px 10px;"> '
        legendTableEnd = '</table>'

        if TotColorLabels > 0:
            ColumnSpan = math.ceil(TotSteps / float(TotColorLabels))
        else:
            ColumnSpan = 1

        Counter = 0
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
            legendColorLabelColumn = '<td height="1px;"></td>'
            if ColumnSpan > 1:
                if row.color_label != None and row.color_label.strip() != '':
                    # legendColorLabelColumn = '<td rowspan="' + str(ColumnSpan) + '" style="font-size:9px; line-height:10px; " valign="top" align="center">'+row.color_label+'</td>'
                    legendColorLabelColumn = '<td rowspan=5 style="font-size:'+str(fontSizeLabels)+'px; line-height:10px; " valign="top" align="left">'+row.color_label+'</td>'
            else:
                legendstep_dict = functions.row2dict(row)
                if row.color_label != None and row.color_label.strip() != '':
                    # ColorLabel = '&nbsp;'+legendstep_dict['color_label'].strip()+'&nbsp;'
                    legendColorLabelColumn = '<td rowspan="' + str(ColumnSpan) + '" style="font-size:'+str(fontSizeLabels)+'px; line-height:10px; " align="left">'+row.color_label+'</td>'

            legendHTMLVertical += '<tr>' + legendColorColumn + legendColorLabelColumn + '</tr>'

        legendHTMLVertical = mainTableBegin + legendHeaderRow + '<tr><td>' + legendTableBegin + legendHTMLVertical + legendTableEnd + '</td></tr>' + mainTableEnd

    else:
        mainTableBackgroundColor = 'transparent'
        fontSizeHeader = 20
        fontSizeLabels = 20
        firstColumnWidth = 35
        legendColorTableBackgroundColor = 'white'
        legendLabelTableBackgroundColor = 'white'
        extraFirstRowHeight = 14
        absoluteMaxRowColorTableHeight = 18
        colorColumnWidth = 35
        colorColumnHeight = 26
        tickColumnWidth = 8
        tickColumnHeight = 26
        labelColumnHeight = 26

        mainTableBegin = '<table style="background: ' + mainTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 3px; padding: 0px; ">'
        legendHeaderRow = '<tr><td colspan=2 style="background: white; padding:3px;"><span style=" font-size:' + str(fontSizeHeader) + 'px;">' + legendName + '</span></td></tr>'     # line-height: 24px;
        legendRowBegin = '<tr>'
        firstColumnBegin = '<td width=' + str(firstColumnWidth) + 'px; style="border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;">'
        secondColumnBegin = '<td valign="top" align="left" style="border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;" >'

        legendColorTable = '<table style="background: ' + legendColorTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding-left: 3px;">'
        legendColorTable += '<tr><td colspan=2 height=' + str(extraFirstRowHeight) + 'px; style=""></td></tr>'

        legendLabelTable = '<table style="background: ' + legendLabelTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 3px; ">'

        row_counter = 0
        # print('legend_steps: ' + str(legend_steps.__len__()))
        for row in legend_steps:
            row_counter += 1
            if row_counter == 1:
                bordertop = ' border-top:1px solid black; '
            else:
                bordertop = ' '

            borderbottom = ' '
            borderbottomtick = ' '
            absoluteMaxRowColorTable = ''
            absoluteMaxRowLegendLabelTable = ''
            if row_counter == legend_steps.__len__():
                borderbottom = ' border-bottom:1px solid black; '
                if row.group_label != None and row.group_label.strip() != '':
                    borderbottomtick = ' border-bottom:1px solid black; '
                    absoluteMaxRowColorTable = '<tr><td colspan=2 height=' + str(absoluteMaxRowColorTableHeight) + 'px; style=""></td></tr>'
                    absoluteMaxRowLegendLabelTable = '<tr><td height='+str(labelColumnHeight)+'px; style="font-size:'+str(fontSizeLabels)+'px;  padding:0px; margin: 0px; padding-left:5px;" valign="middle" align="left">'+row.group_label+'</td></tr>'

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
                '<td width='+str(tickColumnWidth)+'px; height='+str(tickColumnHeight)+'px; style="padding:0px; margin: 0px; border-top:1pt solid black; border-left:1px solid black; '+borderbottomtick+'"></td>' + \
            '</tr>'

            legendColorTable += absoluteMaxRowColorTable

            if row.color_label == None:
                color_label = ''
            else:
                color_label = row.color_label.strip()
            legendLabelTable += '<tr><td height='+str(labelColumnHeight)+'px; style="font-size:'+str(fontSizeLabels)+'px;  padding:0px; margin: 0px; padding-left:5px;" valign="middle" align="left">'+color_label+'</td></tr>'

            legendLabelTable += absoluteMaxRowLegendLabelTable

        legendColorTable += '</table>'
        # legendLabelTable += '<tr><td height=' + str(extraFirstRowHeight) + 'px; style=""></td></tr>'
        legendLabelTable += '</table>'

        columnEnd = '</td>'
        legendRowEnd = '</tr>'
        mainTableEnd = '</table>'

        legendHTMLVertical = mainTableBegin + legendHeaderRow + legendRowBegin + firstColumnBegin + legendColorTable + columnEnd + secondColumnBegin + legendLabelTable + columnEnd + legendRowEnd + mainTableEnd
        # print legendHTMLVertical


    legends_HTML = {'legendHTML': legendHTMLHorizontal, 'legendHTMLVertical': legendHTMLVertical}
    return legends_HTML