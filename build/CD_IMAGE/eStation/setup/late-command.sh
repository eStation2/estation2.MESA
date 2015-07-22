#!/bin/sh
# this is the late command script to be run by install preseed

# install pygrib python module 
pip install /media/cdrom/eStation/Python-Modules/ruffus.tar.gz
pip install /media/cdrom/eStation/Python-Modules/pygrib.tar.gz
pip install /media/cdrom/eStation/Python-Modules/SQLAlchemy.tar.gz
pip install /media/cdrom/eStation/Python-Modules/sqlsoup.tar.gz
pip install /media/cdrom/eStation/Python-Modules/web.py.tar.gz
pip install /media/cdrom/eStation/Python-Modules/psutil.tar.gz
pip install /media/cdrom/eStation/Python-Modules/reloader.tar.gz
pip install /media/cdrom/eStation/Python-Modules/greenwich.tar.gz

# Create Thematic User

username=analyst
password=mesa2015
fullname='eStation Thematic User'
pass=$(perl -e 'print crypt($ARGV[0], "password")' $password)
useradd -c "$fullname" -s /bin/bash -m -p $pass $username

# Create eStation group and add Users
addgroup estation
adduser adminuser estation
adduser analyst estation




