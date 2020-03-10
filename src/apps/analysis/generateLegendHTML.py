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
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.utils import old_div
import math
import re
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

    # print ('legend_id: ' + str(legend_id))
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
        legendName = row['legend_name']     # .decode('utf-8')

    # legendName = legendName.encode('utf-8', errors='ignore')
    legendNameHorizontal = u''.join(legendName).encode('utf-8')
    legendNameHorizontal = re.sub('<br>|<BR>|</br>|</BR>', ' ', legendNameHorizontal.decode())
    # legendNameHorizontal = legendNameHorizontal.decode('utf-8')

    ######################################
    # Create horizontal legend
    ######################################

    if TotSteps >= 30:
        fontSizeLabels = 12
        fontSizeTitle = 15
        # stepWidth = 28
        legendWidth = 500  # 775
        legendTableBegin = '<table style="border-spacing:0px; background:white; padding: 5px 35px 5px 5px;"> '
        legendHeader = '<tr><td colspan='+str(TotSteps)+' style="font-weight: bold; background:white; padding: 0px 5px 5px 0px; font-size:' + str(fontSizeTitle) + 'px;">' + legendNameHorizontal + '</td></tr>'

        if TotColorLabels > 0:
            ColumnSpan = math.ceil(TotSteps / float(TotColorLabels))
        else:
            ColumnSpan = 1

        if TotSteps > 30:
            stepWidth = old_div(legendWidth, TotSteps)
        else:
            stepWidth = 15

        if stepWidth < 4:
            stepWidth = 1

        legendColors = '<tr style="border-spacing: 0px;">'
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

        legendColorLabels = '<tr style="border-spacing: 0px;">'
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
                legendColorLabels += '<td colspan="' + str(int(ColSpan)) + '" style="font-weight: bold; font-size:' + \
                                     str(fontSizeLabels) + 'px; line-height:24px; max-width:' + \
                                     str(stepWidth + 5) + 'px;" align="left">' + row.color_label + '</td>'
                skipcolumns = int(ColSpan - 1)
            elif skipcolumns > 0:
                skipcolumns -= 1
            else:
                legendColorLabels += '<td width="1px;"></td>'

        legendColorLabels += '</tr>'

        legendTableEnd = '</table>'

        legendHTMLHorizontal = legendTableBegin + legendHeader + legendColors + legendColorLabels + legendTableEnd
    else:
        mainTable = '<table style="background: white; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing:0px; cellpadding:0px; margin: 0px; padding: 2px 10px 2px 2px; ">'
        mainTable += '<tr><td colspan=1 style="font-weight: bold; font-size:15px; ">' + legendNameHorizontal + '</td></tr>'   # line-height:24px !important;;  padding-left: 15px;
        mainTable += '<tr><td>'
        mainTable += '<table class="table-header-rotated">'
        mainTableBody = '<tbody>'
        colorRow = '<tr><td width=28px; height=15px;></td>'
        tickRow = '<tr><td width=28px; height=6px;></td>'
        footer = '<tfoot><tr>'

        row_counter = 0
        for row in legend_steps:
            row_counter += 1

            if row.color_label == None:
                color_label = ''
            else:
                color_label = row.color_label.strip()

            if row_counter == 1:
                borderleft = ' border-left:1px solid black; '
                if len(color_label) > 4:
                    colorRow = '<tr><td width=45px; height=15px;></td>'
                    tickRow = '<tr><td width=45px; height=6px;></td>'
            else:
                borderleft = ''

            borderright = ''
            if row_counter == legend_steps.__len__():
                borderright = ' border-right:1px solid black; '
                # if row.group_label != None and row.group_label.strip() != '':
                #     absoluteMaxHeader = '<th class="rotate-45"><div><span>'+row.group_label+'</span></div></th>'

            # Add color column
            # convert row['color_rgb'] from RGB to html color
            color_rgb = row.color_rgb.split(' ')
            # color_html = functions.rgb2html(color_rgb)
            r = color_rgb[0]
            g = color_rgb[1]
            b = color_rgb[2]
            color_html = 'rgb('+r+','+g+','+b+')'

            colorRow += '<td width=20px; height=15px; style="border-top:1px solid black; ' + borderleft + borderright + ' background-color: ' + color_html + '"></td>'
            tickRow += '<td width=20px; height=6px; style="border-top:1px solid black; border-right:1px solid black; ' + borderleft + ' "></td>'
            absoluteMaxHeader = ''

            left = ''
            if row_counter == 1:
                height = "32px"
                if len(color_label) > 4:
                    textalign = 'center'
                    bottom = '25px'
                    left = ' left:-20px !important; '
                elif len(color_label) == 4:
                    textalign = 'center'
                    bottom = '12px'
                    left = ' left:-18px !important; '
                else:
                    textalign = 'center'
                    bottom = '17px'
                    left = ' left:-15px !important; '

                # footer += '<th class="rotate-45" height="32px"><div><span style="text-align:start; bottom: 26px;">' + color_label + '</span></div></th>'
            elif row_counter == legend_steps.__len__():
                if row.group_label != None and row.group_label.strip() != '':
                    height = "25px"
                    textalign = 'justify'
                    if len(row.group_label) >= 4:
                        bottom = '28px'
                    elif len(row.group_label) == 1:
                        bottom = '40px'
                    elif len(row.group_label) == 2:
                        bottom = '38px'
                    elif len(row.group_label) == 3:
                        bottom = '34px'
                    # absoluteMaxHeader = '<th class="rotate-45"><div><span>'+row.group_label+'</span></div></th>'
                    absoluteMaxHeader = '<th class="rotate-45" height="' + height + '"><div><span style="text-align:' + textalign + '; bottom: ' + bottom + ';">' + row.group_label + '</span></div></th>'
            else:
                height = "25px"
                textalign = 'justify'
                if len(color_label) >= 4:
                    bottom = '28px'
                elif len(color_label) == 1:
                    bottom = '40px'
                elif len(color_label) == 2:
                    bottom = '38px'
                elif len(color_label) == 3:
                    bottom = '34px'

            footer += '<th class="rotate-45" height="'+height+'"><div><span style="text-align:'+textalign+'; bottom: ' + bottom + ';' + left + '">' + color_label + '</span></div></th>'
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
        fontSizeLabels = 12
        fontSizeTitle = 15
        stepWidth = 28
        stepHeight = 1
        rowspanlabel = 15
        lineheight = 12
        classlegendstyle = "legend-style"

        if TotSteps <= 35:
            stepHeight = 10
            rowspanlabel = 2
            classlegendstyle = ''
        elif TotSteps <= 65:
            stepHeight = 3
            rowspanlabel = 4
            classlegendstyle = ''
        elif TotSteps <= 130:
            stepHeight = 2
            rowspanlabel = 6
            classlegendstyle = ''

        mainTableBegin = '<table style="border-spacing:0px; background:white; padding:0;"> '
        mainTableEnd = '</table>'
        legendHeaderRow = '<tr><td style="font-weight: bold;background:white; padding: 5px; font-size:' + str(fontSizeTitle) + 'px;">' + legendName + '</td></tr>'
        legendTableBegin = '<table style="border-spacing:0px; background:white; padding: 0px 1px 0px 1px;"> '
        legendTableEnd = '</table>'

        # if TotColorLabels > 0:
        #     rowspanlabel = math.ceil(TotSteps / float(TotColorLabels))
        # else:
        #     rowspanlabel = 1

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
            if TotSteps <= 24:
                border = "border:1px solid black; "

            # legendColorColumn = '<td width='+str(stepWidth)+'px; height='+str(stepHeight)+'px; style="'+border+' background-color: '+color_html+'"></td>'
            legendColorColumn = '<td width=' + str(stepWidth) + 'px; class="' + classlegendstyle + '" style="' + border + ' background-color: ' + color_html + '"></td>'

            # Add label column
            Counter += 1
            if Counter == 1 and row.color_label != None and row.color_label.strip() != '':
                rowspan = 1
            else:
                rowspan = rowspanlabel

            legendColorLabelColumn = '<td class="' + classlegendstyle + '"></td>'
            if rowspanlabel > 1:
                if row.color_label != None and row.color_label.strip() != '':
                    legendColorLabelColumn = '<td rowspan="' + str(rowspan) + 'px;" style="font-weight: bold; font-size:' + str(fontSizeLabels) + 'px; line-height:' + str(lineheight) + 'px;" valign="top" align="left">' + row.color_label + '</td>'
            else:
                # legendstep_dict = functions.row2dict(row)
                if row.color_label != None and row.color_label.strip() != '':
                    legendColorLabelColumn = '<td rowspan="' + str(rowspan) + 'px;" style="font-weight: bold; font-size:' + str(fontSizeLabels) + 'px; line-height:' + str(lineheight) + 'px;" align="left">' + row.color_label+'</td>'

            legendHTMLVertical += '<tr style="height:'+str(stepHeight)+'px;">' + legendColorColumn + legendColorLabelColumn + '</tr>'

            # Add an empty row for the label on last class to have the lable shown at the bottom of the table
            if TotSteps == Counter and row.color_label != None and row.color_label.strip() != '':
                legendHTMLVertical += '<tr style="height:1px;"></tr>'

        legendHTMLVertical = mainTableBegin + legendHeaderRow + '<tr><td>' + legendTableBegin + legendHTMLVertical + legendTableEnd + '</td></tr>' + mainTableEnd

    else:
        mainTableBackgroundColor = 'transparent'
        fontSizeHeader = 15
        fontSizeLabels = 12
        firstColumnWidth = 35
        legendColorTableBackgroundColor = 'white'
        legendLabelTableBackgroundColor = 'white'
        extraFirstRowHeight = 10
        absoluteMaxRowColorTableHeight = 7
        colorColumnWidth = 35
        colorColumnHeight = 12
        tickColumnWidth = 8
        tickColumnHeight = 12
        labelColumnHeight = 12
        lineheight = 12

        mainTableBegin = '<table style="background: ' + mainTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px; ">'
        legendHeaderRow = '<tr><td colspan=2 style="font-weight: bold; background: white; padding:2px;"><span style=" font-size:' + str(fontSizeHeader) + 'px;">' + legendName + '</span></td></tr>'     # line-height: 24px;
        legendRowBegin = '<tr>'
        firstColumnBegin = '<td width=' + str(firstColumnWidth) + 'px; style="border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;">'
        secondColumnBegin = '<td valign="top" align="left" style="border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;" >'

        legendColorTable = '<table style="background: ' + legendColorTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding-left: 3px;">'
        legendColorTable += '<tr><td colspan=2 height=' + str(extraFirstRowHeight) + 'px; style=""></td></tr>'

        legendLabelTable = '<table style="background: ' + legendLabelTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px; ">'

        row_counter = 0
        # print ('legend_steps: ' + str(legend_steps.__len__()))
        for row in legend_steps:
            row_counter += 1
            if row_counter == 1:
                bordertop = ' border-top:1px solid black; '
                lineheight = 15
            elif row_counter == legend_steps.__len__():
                lineheight = 13
            else:
                bordertop = ' '
                lineheight = 12

            borderbottom = ' '
            borderbottomtick = ' '
            absoluteMaxRowColorTable = ''
            absoluteMaxRowLegendLabelTable = ''
            if row_counter == legend_steps.__len__():
                borderbottom = ' border-bottom:1px solid black; '
                if row.group_label != None and row.group_label.strip() != '':
                    borderbottomtick = ' border-bottom:1px solid black; '
                    absoluteMaxRowColorTable = '<tr><td colspan=2 height=' + str(absoluteMaxRowColorTableHeight) + 'px; style=""></td></tr>'
                    absoluteMaxRowLegendLabelTable = '<tr><td height='+str(labelColumnHeight)+'px; style="font-weight: bold; font-size:'+str(fontSizeLabels)+'px; line-height:' + str(lineheight) + 'px; padding:0px; margin: 0px; padding-left:5px;" valign="middle" align="left">'+row.group_label+'</td></tr>'

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
            legendLabelTable += '<tr><td height='+str(labelColumnHeight)+'px; style="font-weight: bold; font-size:'+str(fontSizeLabels)+'px; line-height:' + str(lineheight) + 'px; padding:0px; margin: 0px; padding-left:5px;" valign="middle" align="left">'+color_label+'</td></tr>'

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
