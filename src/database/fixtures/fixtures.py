# -*- coding: utf-8 -*-
#
#	purpose: Create fixtures from postgresql dump.sql
#	author:  Marco Beri marcoberi@gmail.com
#	date:	 27.08.2014
#

from __future__ import absolute_import


def create_fixtures(from_file, to_file):
    to_ = file(to_file, "w")
    to_.write("BEGIN;\n")
    skip_until = skip_end_while = None
    into_create_table = None
    tables_primary_key = {}
    for line in file(from_file, "r").readlines():
        line = line.rstrip()
        if line.startswith("ALTER TABLE ONLY"):
            into_alter_table = line.split(" ")[3]
        pos = line.find("PRIMARY KEY")
        if pos > 0:
            tables_primary_key[into_alter_table] = line.split("(")[1].split(")")[0]
    for line in file(from_file, "r").readlines():
        line = line.rstrip()
        if skip_end_while:
            if line.endswith(skip_end_while):
                skip_end_while = None
            continue
        if not line:
            continue
        if skip_until:
            if line.startswith(skip_until):
                skip_until = None
            continue
        skip = False
        for skip_start in ("--", "SET ", "CREATE SCHEMA", "CREATE UNIQUE", "    CONSTRAINT",
                "INSERT INTO products_data"):
            if line.startswith(skip_start):
                skip = True
        if skip:
            continue
        if line.startswith("CREATE FUNCTION"):
            skip_until = "$_$;"
            continue
        if line.startswith("COMMENT ") or line.startswith("ALTER "):
            if not line.endswith(";"):
                skip_end_while = ";"
            continue
        if line.startswith("CREATE TABLE"):
            into_create_table = line.split(" ")[2]
        elif into_create_table:
            if line.startswith(");"):
                to_.write("    PRIMARY KEY (" + tables_primary_key[into_create_table] + ")\n")
                into_create_table = None
            elif not line.endswith(","):
                line += ","
        line = line.replace("true,", "1,").replace("true)", "1)")
        line = line.replace("false,", "0,").replace("false)", "0)")
        line = line.replace("::character varying", "")
        line = line.replace("without time zone DEFAULT now()", "")
        if not "TESTING123" in line:
            to_.write(line + "\n")
    to_.write("END;\n")
    to_.close()

if __name__ == "__main__":
    import sys
    create_fixtures(sys.argv[1], sys.argv[2])
