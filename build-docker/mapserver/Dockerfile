#
# This creates an Ubuntu derived base image that installs the MAPSERVER_VERSION of MapServer
# Git checkout compiled with needed drivers.
#

# Ubuntu 18.04 Bionic Beaver
FROM ubuntu:18.04 AS ubuntu
# FROM d-registry.jrc.it:5000/public/ubuntu:18.04 AS ubuntu

USER root

#Setup user
ARG UID
ARG GID

ENV DEBIAN_FRONTEND=noninteractive
# ARG http_proxy=http://10.168.209.72:8012
# ARG https_proxy=http://10.168.209.72:8012
# ARG ftp_proxy=http://10.168.209.72:8012
# ARG no_proxy="127.0.0.1, localhost, jrc.ec.europa.eu, jrc.it, jrc.org"

RUN apt-get update && apt-get install -y --fix-missing --no-install-recommends build-essential ca-certificates curl wget \
    git libaio1 make cmake python3-numpy python3-dev software-properties-common  libc6-dev libfreetype6-dev libharfbuzz-dev \
    libcairo2-dev flex bison libfcgi-dev libxml2 libxml2-dev bzip2 apache2 gdal-bin libfribidi-dev libgeos-dev libgdal-dev \
    libproj-dev nano net-tools \
    && apt-get remove --purge -y $BUILD_PACKAGES  && rm -rf /var/lib/apt/lists/*
#postgis postgresql
#ARG MAPSERVER_VERSION
RUN mkdir /build
RUN cd /build && \
    git clone https://github.com/mapserver/mapserver.git mapserver && \
    cd /build/mapserver && \
    git checkout ${MAPSERVER_VERSION} \
    && mkdir /build/mapserver/build \
    && cd /build/mapserver/build \
    && cmake \
      -DCMAKE_BUILD_TYPE=Release \
      -DWITH_CLIENT_WFS=ON \
      -DWITH_CLIENT_WMS=ON \
      -DWITH_CURL=ON \
      -DWITH_GDAL=ON \
      -DWITH_GIF=ON \
      -DWITH_ICONV=ON \
      -DWITH_KML=ON \
      -DWITH_LIBXML2=ON \
      -DWITH_OGR=ON \
      -DWITH_ORACLESPATIAL=OFF \
      -DWITH_POINT_Z_M=OFF \
      -DWITH_PROJ=ON \
      -DWITH_SOS=ON  \
      -DWITH_THREAD_SAFETY=ON \
      -DWITH_WCS=ON \
      -DWITH_WFS=ON \
      -DWITH_WMS=ON \
      -DWITH_FCGI=ON \
      -DWITH_FRIBIDI=ON \
      -DWITH_CAIRO=ON \
      -DWITH_POSTGRES=ON \
      -DWITH_HARFBUZZ=ON \
      -DWITH_POSTGIS=ON \
      -DWITH_PROTOBUFC=OFF \
      ..  \
    && make  \
    && make install \
    && ldconfig \
    && rm -Rf /build/mapserver

# Externally accessible data is by default put in /u02
WORKDIR /data
#VOLUME ["/u02"]
COPY hello.py /usr/lib/cgi-bin/.

# Clean up
RUN  apt-get purge -y software-properties-common build-essential cmake ;\
 apt-get autoremove -y ; \
 apt-get clean ; \
 rm -rf /var/lib/apt/lists/partial/* /tmp/* /var/tmp/*

# Execute the gdal utilities as nobody, not root

# Enable these Apache modules
RUN  a2enmod actions cgi alias

RUN chmod o+x /usr/local/bin/mapserv
RUN chmod o+x /usr/lib/cgi-bin/hello.py
RUN ln -s /usr/local/bin/mapserv /usr/lib/cgi-bin/mapserv
RUN chmod 755 /usr/lib/cgi-bin

EXPOSE  80

#ENV HOST_IP `ifconfig eth0 | grep inet | grep Mask:255.255.0.0 | cut -d ' '-f 12 | cut -d ':' -f 2`

CMD apache2ctl -D FOREGROUND