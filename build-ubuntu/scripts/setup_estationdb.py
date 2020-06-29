import psycopg2

DB_HOST = "jeodb01.cidsn.jrc.it"
DB_PORT = 65431
DB_NAME = "estationdb"
RW_USER = "estation"
RW_PASS = ""
FILE_DUMP_STRUCTURE="/var/www/eStation2/database/dbInstall/products_dump_structure_only.sql"

DSN = f"postgresql://{RW_USER}:{RW_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

conn = psycopg2.connect(DSN)
curs = conn.cursor()

# SQL = """
# CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);
# INSERT INTO test
#             (num, data)
#      VALUES (121, 'aaa')
#           , (212, 'bbb')
#           , (313, 'ccc')
#           ;
# """

for line in open(FILE_DUMP_STRUCTURE):
    curs.execute(line)
# curs.execute(SQL)