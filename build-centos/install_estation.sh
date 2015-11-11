#!/bin/sh
mkdir -p /var/log/eStation2/

exec 1>/var/log/eStation2/install.log
exec 2>/var/log/eStation2/install.err

#Create dir eStation, unknown EFTS
mkdir -p /space/efts/fromTellicast/{forEstation,others,forFtpPush}
mkdir -p /space/tellicast/data/received/default
mkdir -p /data-space/{data,space}
mkdir -p /data/data_patch/temp
ln -s /data-space/data /data
ln -s /data-space/space /space
#Create dir Preprocessor EFTS out
mkdir -p /data-space/space/efts
#Create dir Tellicast
mkdir -p /data-space/space/tellicast/data/received/channel-default/training-data/{AMESD-E-Station,AMESD-System}
mkdir -p /data-space/space/tellicast/data/receiving
mkdir -p /data-space/space/tellicast/log
ln -s /space/tellicast/data/received/channel-default/ /space/tellicast/data/received/default
ln -s /space/tellicast/data/receiving/ /space/tellicast/data/tmp

#Create User/group
useradd -c "eStation Thematic User" -s /bin/bash -m -p '$1$QzIcDpOX$MTmh852fnqwQm3MSFyRq10' analyst
useradd -c "eStation Administrator" -s /bin/bash -m -p '$1$xyz$x1T904VZtQuY.2kHse72j.' adminuser
useradd -s /sbin/nologin -d /space/efts/fromTellicast -p '$1$xyz$NfS28ejxis.gJvpu2oz6X.' mesadata
useradd -s /sbin/nologin -m -p '$1$QIjnxX/M$MNO6daNjU90syMhF5x0qj/' ebs

groupadd estation
usermod -a -G estation analyst
usermod -a -G apache analyst
usermod -a -G estation adminuser

echo "adminuser All=(ALL) ALL" >> /etc/sudoers

#Install FrontUtils
cp -p /mnt/stage2/estation/FrontsUtils.so /usr/lib64/FrontsUtils.so

#Create tmp dir: all lines to be removed -> done in Apps.rpm
#mkdir -p -m 777 /tmp/eStation2/{services,processing}
#chown -R analyst:adminuser /tmp/eStation2/services/
#chown -R analyst:adminuser /tmp/eStation2/processing/
#echo "mkdir -p -m 777 /tmp/eStation2/{services,processing}
#chown analyst:adminuser /tmp/eStation2/
#chown analyst:adminuser /tmp/eStation2/services/
#chown analyst:adminuser /tmp/eStation2/processing/" >> /etc/rc.d/rc.local

#Export proj to /usr/local/src/tas/
tar -zxf /mnt/stage2/estation/proj.4-4.8.tar.gz -C /usr/local/src/tas/

#Export mapserver to /usr/local/src/tas/
tar -zxf /mnt/stage2/estation/mapserver-6.4.1.tar.gz -C /usr/local/src/tas/

#Export bucardo to /usr/local/src/tas/
tar -zxf /mnt/stage2/estation/Bucardo-5.4.1.tar.gz -C /usr/local/src/tas/

#Compil proj
cd /usr/local/src/tas/proj.4-4.8/
make
make install

#Compil mapserver
cd /usr/local/src/tas/mapserver-6.4.1/build/
make
make install

#Compil bucardo
cd /usr/local/src/tas/Bucardo-5.4.1/
perl Makefile.PL
make
make install
cp bucardo /usr/bin/

#Setup estation server
cp /mnt/stage2/estation/setup_eStation_Server.sh /usr/local/src/tas/
cp /mnt/stage2/estation/httpd.conf /usr/local/src/tas/
cp /mnt/stage2/estation/estation.sh /usr/local/src/tas/scripts/
ln -s /usr/local/src/tas/scripts/estation.sh /etc/init.d/estation

#Export Estation dans /var/www/ -> remove: done through .rpms
#tar -zxf /mnt/stage2/estation/estation_www.tar.gz -C /var/www/
#ln -s /var/www/eStation2-2.0.1/ /var/www/eStation2

#Config Postgresql -> moved upwards (before eStation install)
su postgres -c "/usr/pgsql-9.3/bin/initdb -D /var/lib/pgsql/9.3/data"

#Dump database -> removed: done in Apps.rpm
#tar -zxf /mnt/stage2/estation/estation_pgsql.tar.gz -C /var/lib/pgsql/9.3/data/

#Start the database
/etc/init.d/postgresql-9.3 start
chkconfig postgresql-9.3 on

#Install estation: from the rpms !! Still to be tested
rpm_files=($(ls /mnt/stage2/estation/eStation2*.rpm))
for rpm_file in ${rpm_files}
do
	yum install -y ${rpm_file}
done

#What PC?
pc=$(cat /etc/sysconfig/network | grep HOSTNAME | cut -d "-" -f 2)
sed -i "s/role = PC1.*/role = $pc/g" /eStation2/settings/system_settings.ini

#Install/Start apache
cd /usr/local/src/tas/
/usr/local/src/tas/setup_eStation_Server.sh
/etc/init.d/estation start
chkconfig estation on

#Config vsftpd
sed -i "s/anonymous_enable.*/anonymous_enable=NO/g" /etc/vsftpd/vsftpd.conf
service vsftpd start
chkconfig vsftpd on

