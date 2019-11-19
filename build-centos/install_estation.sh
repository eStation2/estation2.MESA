#!/bin/sh
mkdir -p /var/log/eStation2/

exec 1>/var/log/eStation2/install.log
exec 2>/var/log/eStation2/install.err

#Create User/group
useradd -c "eStation Thematic User" -s /bin/bash -m -p '$1$QzIcDpOX$MTmh852fnqwQm3MSFyRq10' analyst
useradd -c "eStation Administrator" -s /bin/bash -m -p '$1$xyz$x1T904VZtQuY.2kHse72j.' adminuser
useradd -s /sbin/nologin -d /space/efts/fromTellicast -p '$1$xyz$NfS28ejxis.gJvpu2oz6X.' mesadata
useradd -s /sbin/nologin -m -p '$1$QIjnxX/M$MNO6daNjU90syMhF5x0qj/' ebs

groupadd estation
usermod -a -G estation analyst
usermod -a -G apache analyst
usermod -a -G estation adminuser

echo "adminuser ALL=(ALL) ALL" >> /etc/sudoers

# Add python-anaconda path in .bashrc of adminuser
echo "export PATH=/usr/local/src/tas/anaconda/bin:$PATH" >> /home/adminuser/.bashrc
echo "export PATH=/usr/local/src/tas/anaconda/bin:$PATH" >> /home/analyst/.bashrc

#Install FrontUtils
cp -p /mnt/stage2/estation/FrontsUtils.so /usr/lib64/FrontsUtils.so

#Export proj to /usr/local/src/jrc/
tar -zxf /mnt/stage2/estation/proj.4-4.8.tar.gz -C /usr/local/src/jrc/

#Export mapserver to /usr/local/src/jrc/
tar -zxf /mnt/stage2/estation/mapserver-6.4.1.tar.gz -C /usr/local/src/jrc/

#Export bucardo to /usr/local/src/jrc/
tar -zxf /mnt/stage2/estation/Bucardo-5.4.1.tar.gz -C /usr/local/src/jrc/

#Compil proj
cd /usr/local/src/jrc/proj.4-4.8/
make
make install

#Compil mapserver
cd /usr/local/src/jrc/mapserver-6.4.1/build/
make
make install
cp /usr/local/src/jrc/mapserver-6.4.1/build/libmapserver.so* /usr/local/lib64

#Compil bucardo
cd /usr/local/src/jrc/Bucardo-5.4.1/
perl Makefile.PL
make
make install
cp bucardo /usr/bin/

#Setup estation server
cp /mnt/stage2/estation/setup_eStation_Server.sh /usr/local/src/tas/
cp /mnt/stage2/estation/httpd.conf /usr/local/src/tas/

#Config Postgresql -> moved upwards (before eStation install)
su postgres -c "/usr/pgsql-9.3/bin/initdb -D /var/lib/pgsql/9.3/data"

#Install estation: from the rpms
#yum install -y eStation2-Apps
yum --nogpgcheck localinstall -y /mnt/stage2/Packages/JRC/estation/eStation2-Apps-2.1.2-31.x86_64.rpm
#yum install -y eStation2-Docs 
yum --nogpgcheck localinstall -y /mnt/stage2/Packages/JRC/estation/eStation2-Docs-2.1.2-4.x86_64.rpm
yum --nogpgcheck localinstall -y /mnt/stage2/Packages/JRC/estation/eStation2-Layers-2.0.2-2.x86_64.rpm
yum --nogpgcheck localinstall -y /mnt/stage2/Packages/JRC/estation/eStation2-Layers-2.0.4-3.x86_64.rpm
yum --nogpgcheck localinstall -y /mnt/stage2/Packages/JRC/estation/eStation2-Layers-2.1.2-4.x86_64.rpm

#Install/Start apache (changed on 16.08.19 for 1.3.2 ISO)
#cd /usr/local/src/tas/
#/usr/local/src/tas/setup_eStation_Server.sh
/usr/local/src/tas/anaconda/bin/mod_wsgi-express setup-server /var/www/eStation2/webpy_esapp.py --port=80 --user analyst --group analyst --server-root=/usr/local/src/tas/eStation_wsgi_srv

# Symbolic link for wsgo_server (PT 2015/12/04)
ln -s /usr/local/src/tas/eStation_wsgi_srv /eStation2/eStation_wsgi_srv

#Config vsftpd
sed -i "s/anonymous_enable.*/anonymous_enable=NO/g" /etc/vsftpd/vsftpd.conf

\cp -p /mnt/stage2/estation/pg_hba.conf /var/lib/pgsql/9.3/data/
\cp -p /mnt/stage2/estation/postgresql.conf /var/lib/pgsql/9.3/data/
# Start postgres
/etc/init.d/postgresql-9.3 start
chkconfig postgresql-9.3 on

#######################
# Installation du FRAC
#######################

# Installation FMSG
yum -y install puma-frac-fmsg_tools-base 
yum -y install puma-frac-fmsg_conf-base 
yum -y install puma-frac-fmsg-base
chkconfig fmsg off
service fmsg stop

# Installation de decompx
yum -y install decompx
chkconfig decompx off
service decompx stop
