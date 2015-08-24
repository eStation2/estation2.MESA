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
pip install /media/cdrom/eStation/Python-Modules/Pillow.tar.gz
pip install /media/cdrom/eStation/Python-Modules/greenwich.tar.gz

# install eStation 2.0.4
sudo dpkg -i /media/4F3D-5FE8/eStation/repository/amd64/eStation-Apps-*.deb

# install bucardo package and configure it
/media/cdrom/eStation/setup/bucardo_config.sh



