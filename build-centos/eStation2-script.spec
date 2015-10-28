Summary: eStation 2.0 application from JRC
Name: eStation-Apps 
Version: 2.0.1
Release: 1
URL: http://estation.jrc.ec.europa.eu       
License: GPL 
Group: Applications/Internet
BuildRoot: /tmp/ 
Requires: bash perl
Source1: estation2-Apps.tar.gz
BuildArch: noarch
%description
The eStation 2.0 is an open source Earth Observation processing server
%pre
mkdir -p /var/log/eStation2
logfile=/var/log/eStation2/Station-Apps_2.0.1-preinst.log
exec 1> $logfile
exec 2> $logfile
echo "`date +'%Y-%m-%d %H:%M:%S'` - Starting preinst operations " 
# Check the analyst exists, otherwise create them
getent passwd analyst >/dev/null || \
useradd -c "eStation Thematic User" -s /bin/bash -m -p '$1$QzIcDpOX$MTmh852fnqwQm3MSFyRq10' analyst
# Check the adminuser exists, otherwise create them
getent passwd adminuser >/dev/null || \
useradd -c "adminuser User" -s /bin/bash -m -p '$1$QzIcDpOX$MTmh852fnqwQm3MSFyRq10' adminuser
# Check the ebs exists, otherwise create them --> Create as nologin
getent passwd ebs >/dev/null || \
useradd -c "ebs User" -s /bin/nologin -m -p '$1$QIjnxX/M$MNO6daNjU90syMhF5x0qj/' ebs
# Check the estation group exists, otherwise create them
getent group estation >/dev/null || \
groupadd estation
getent passwd estation >/dev/null || \
#useradd -c "estation" -s /bin/bash -m -p '$1$QIjnxX/M$MNO6daNjU90syMhF5x0qj/' analyst 
# Add Users to estation group
usermod -a -G estation analyst
usermod -a -G estation adminuser
usermod -a -G apache analyst
echo " `date +'%Y-%m-%d %H:%M:%S'` - Preinst operations completed" 
%setup -T -D -a 1
mkdir -p /tmp/estation2
cd /tmp/estation2
tar -zxf /root/rpmbuild/SOURCES/estation2.tar.gz -C /tmp/estation2
%install
%files
%defattr(-,root,root)
%clean
rm -rf ${RPM_BUILD_ROOT}
%post
mkdir -p /var/log/eStation2
logfile=/var/log/eStation2/Station-Apps_2.0.1-postinst.log
exec 1> $logfile
exec 2> $logfile
echo "`date +'%Y-%m-%d %H:%M:%S'` - Starting postinst operations " 
#if [ $1 -eq 1 ]; then
#/usr/local/src/tas/anaconda/bin/mod_wsgi-express setup-server /var/www/eStation2/webpy_esapp.py --port=80 --user analyst --group analyst --server-root=/usr/local/src/tas/eStation_wsgi_srv
#yes | cp httpd.conf /usr/local/src/tas/eStation_wsgi_srv/
#sed -i "s/HOSTNAME=.*/HOSTNAME=MESA/g" /etc/sysconfig/network
#sed -i "s/#listen_addresses.*/listen_addresses = '*'/g" /var/lib/pgsql/9.3/data/postgresql.conf
#sed -i "s/127.0.0.1.*/samenet                 trust/g" /var/lib/9.3/data/pg_hba.conf
#su postgres -c "/usr/pgsql-9.3/bin/initdb -D /var/lib/pgsql/9.3/data"
#tar -zxf /root/rpmbuild/SOURCES/estation_pgsql.tar.gz -C /var/lib/pgsql/9.3/data/
#yes | cp /mnt/stage2/estation/pg_hba.conf /var/lib/pgsql/9.3/data/
#/etc/init.d/postgresql-9.3 start
#chkconfig postgresql-9.3 on
#cd /usr/local/src/tas/
#/usr/local/src/tas/setup_eStation_Server.sh
#/etc/init.d/estation start
#chkconfig estation on
#    echo "First install complete"
#else
#    echo "Upgrade to $Version  complete"
#fi
#cp /mnt/stage2/estation/setup_eStation_Server.sh /usr/local/src/tas/
#cp /mnt/stage2/estation/httpd.conf /usr/local/src/tas/
#cp /mnt/stage2/estation/estation.sh /usr/local/src/tas/
#mkdir -p -m 777 /tmp/eStation2/
#mkdir -p -m 777 /tmp/eStation2/services/
#mkdir -p -m 777 /tmp/eStation2/processing/
#echo "mkdir -p -m 777 /tmp/eStation2/
#mkdir -p -m 777 /tmp/services/
#mkdir -p -m 777 /tmp/eStation2/processing/
#chown analyst:adminuser /tmp/eStation2/
#chown analyst:adminuser /tmp/eStation2/services/
#chown analyst:adminuser /tmp/eStation2/processing/" >> /etc/profile.d/custom.sh
#rm -rf ${RPM_BUILD_ROOT}
#mkdir -p ${RPM_BUILD_ROOT}/usr/bin
echo " `date +'%Y-%m-%d %H:%M:%S'` - Postinst operations completed" 

%changelog
* Tue Oct 21 2015 Chris Ciborowski <krzysztof.ciborowski@telespazio.com> 
This is the initial install 
