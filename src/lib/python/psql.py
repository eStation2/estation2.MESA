#
#	purpose: Define functions to access postgresql db
#	author:  M. Clerici
#	date:	 24.02.2014
#   descr:	 Functions to access DB
#

import sys

import psycopg2
import psycopg2.extras
#from lib.python import es_logging as log
#from lib.python.es_constants import *

myglobals = {
    'host': 'h05-dev-vm19',
    'port': '5432',
    'dbUser': 'estation',
    'dbPass': 'mesadmin',
    'dbName': 'estationdb',
    'schema': 'products',
    'basedir': '/srv/www/eStation2/',
    'data_path': '',
    'static_data_path': ''
}

psycopg2_dns = "dbname='%s' user='%s' host='%s' password='%s'" % (myglobals['dbName'],
                                                                 myglobals['dbUser'],
                                                                 myglobals['host'],
                                                                 myglobals['dbPass'])


#psycopg2_dns = "dbname='%s' user='%s' host='%s' password='%s'" % (DB_DATABASE, Testing git........
#                                                             DB_USER,
#                                                             DB_HOST,
#                                                             DB_PASS)


def connect_db(use_dns):

    # DNS="dbname = '%s' user = '%s' host = '%s'" % (nameDB,userDB,hostDB)
    try:
        conn = psycopg2.connect(use_dns)
        conn.set_isolation_level(0)
        # cur = conn.cursor()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return cur
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        raise Exception("Database connection failed!\n ->%s" % exceptionValue)


def get_list_sub_products():

    cursor = connect_db(psycopg2_dns)
    sql = "select DISTINCT sub_prod_descr_name from ps.products_data"
    cursor.execute(sql)
    res = cursor.fetchall()
    return res


def get_list_ingest_active_trigger():

    cursor = connect_db(psycopg2_dns)
    sql = "select DISTINCT sub_prod_descr_name from ps.products_data"
    cursor.execute(sql)

    res = cursor.fetchall()
    return res


def get_list_eumetcast():

    cursor = connect_db(psycopg2_dns)
    #" date_revision, date_publication, entry_date" \
    #      " COALESCE(date_creation,'01/01/2000')   " \
    sql = " select eumetcast_id from products.eumetcast "
    cursor.execute(sql)
    rows = cursor.fetchall()

    print sql
    for row in rows:
        print row

    return rows