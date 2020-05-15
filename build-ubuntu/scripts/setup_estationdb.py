import psycopg2

DB_HOST = ""
DB_PORT = 5432
DB_NAME = ""
RW_USER = ""
RW_PASS = ""

DSN = f"postgresql://{RW_USER}:{RW_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

conn = psycopg2.connect(DSN)
curs = conn.cursor()

SQL = """
CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);
INSERT INTO test
            (num, data)
     VALUES (121, 'aaa')
          , (212, 'bbb')
          , (313, 'ccc')
          ;
"""
curs.execute(SQL)