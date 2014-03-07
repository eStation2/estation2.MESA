#
#	purpose: Define functions to access postgresql db
#	author:  M. Clerici
#	date:	 24.02.2014
#   descr:	 Functions to access DB
#

from time import time
from datetime import datetime
import os, sys, psycopg2, psycopg2.extras
import json

sys.path.append('/srv/www/eStation2/config/')

import es2

def connectDB(useDSN):

    # DNS="dbname = '%s' user = '%s' host = '%s'" % (nameDB,userDB,hostDB)
    try:
        conn = psycopg2.connect(useDSN)
        conn.set_isolation_level(0)
        # cur = conn.cursor()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return cur
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        raise Exceptions.NoApplicableCode("Database connection failed!\n ->%s" % exceptionValue)


def getListSubProducts():

    psycopg2DSN = "dbname='%s' user='%s' host='%s' password='%s'" % (es2.DB_DATABASE,
                                                                 es2.DB_USER,
                                                                 es2.DB_HOST,
                                                                 es2.DB_PASS)
    cursor = connectDB(psycopg2DSN)
    sql="select DISTINCT sub_prod_descr_name from ps.products_data"
    cursor.execute(sql)
    res = cursor.fetchall()
    return res