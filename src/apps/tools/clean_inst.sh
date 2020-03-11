#!/bin/bash
yum remove -y eStation2-Docs.x86_64
yum remove -y eStation2-Layers.x86_64
yum remove -y eStation2-Apps.x86_64

rm -fr /var/www/eStation2*
rm -fr /tmp/eStation2/*
rm -fr /eStation2/*

/etc/init.d/postgresql-9.3 restart
sleep 1
/etc/init.d/postgresql-9.3 restart
sleep 1
/etc/init.d/postgresql-9.3 restart
dropdb -U estation estationdb

dropdb -U bucardo bucardo

