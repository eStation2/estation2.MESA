#!/bin/bash
#
#	Script to do bucardo installation 
#


echo "$(date +'%Y-%m-%d %H:%M:%S') Install bucardo from /media/cdrom"

file_tgz='Bucardo-5.4.1.tar.gz'
bucardo_tgz="/home/analyst/${file_tgz}"
target_dir="/usr/lib/bucardo/"
log_dir="/var/log/bucardo"
run_dir="/var/run/bucardo"

if [ -f ${bucardo_tgz} ]; then
	mkdir -p ${target_dir}
	echo "$(date +'%Y-%m-%d %H:%M:%S') Target directory ${target_dir} created"
	cp ${bucardo_tgz} ${target_dir}
	cd ${target_dir}
	gunzip ${file_tgz}
	tar -xvf "${file_tgz%.*}"	
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo files extracted"
	cd Bucardo-5.4.1
	# Build the package
	perl Makefile.PL
	make 
	make install
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo package ready to install"
	# Install the package
	mkdir -p /var/log/bucardo
	./bucardo install --batch --dbname estationdb --dbhost localhost
	echo "$(date +'%Y-%m-%d %H:%M:%S') Bucardo package installed"
	# Create log and run dir
    mkdir -p ${log_dir}
    chown adminuser:estation ${log_dir}
    chmod 777 ${log_dir}
    mkdir -p ${run_dir}
    chown adminuser:estation ${run_dir}
    chmod 777 ${run_dir}
    chmod 666 /home/adminuser/.pgpass
else
	echo "$(date +'%Y-%m-%d %H:%M:%S') Error: bucardo .tgz ${bucardo_tgz} not found. Exit"
	exit 1
fi

echo "$(date +'%Y-%m-%d %H:%M:%S') Create bucardo objects"


