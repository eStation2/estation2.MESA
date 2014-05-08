__author__ = "Jurriaan van 't Klooster"

import lib.python.functions as f


string_date = '20110506'
result = f.is_date_yyyymmdd(string_date)
print "is_date_yyyymmdd: %s = %s" % (string_date, result)

string_date = '201105061330'
result = f.is_date_yyyymmddhhmm(string_date)
print "is_date_yyyymmddhhmm: %s = %s" % (string_date, result)

string_date = '2011167'
result = f.is_date_yyyydoy(string_date)
print "is_date_yyyydoy: %s = %s" % (string_date, result)

year_month_day = '20110506'
result = f.conv_date_2_dekad(year_month_day)
print "conv_date_2_dekad: %s = %s" % (year_month_day, result)

year_month_day = '20110506'
result = f.conv_date_2_month(year_month_day)
print "conv_date_2_month: %s = %s" % (year_month_day, result)

dekad = '21'
result = f.conv_dekad_2_date(dekad)
print "conv_dekad_2_date: %s = %s" % (dekad, result)

month = '6'
result = f.conv_month_2_date(month)
print "conv_month_2_date: %s = %s" % (month, result)

year = '2001'
doy = '267'
yeardoy = year+doy
result = f.conv_date_yyyydoy_2_yyyymmdd(yeardoy)
print "conv_date_yyyydoy_2_yyyymmdd: year: %s doy: %s = %s" % (year, doy, result)

year_month_day = '20110506'
result = f.conv_date_yyyymmdd_2_doy(year_month_day)
print "conv_date_yyyymmdd_2_doy: %s = %s" % (year_month_day, result)

yyyy_mm_dkx = '2001_06_dk2'
result = f.conv_yyyy_mm_dkx_2_yyyymmdd(yyyy_mm_dkx)
print "conv_yyyy_mm_dkx_2_yyyymmdd: %s = %s" % (yyyy_mm_dkx, result)

yymmk = '06061'
result = f.conv_yymmk_2_yyyymmdd(yymmk)
print "conv_yymmk_2_yyyymmdd: %s = %s" % (yymmk, result)



