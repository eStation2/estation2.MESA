Summary: eStation 2.0 application from JRC
Name: eStation2-Apps
Version: 2.1.0
Release: 15
Group: eStation
License: GPL
Source: /home/adminuser/rpms/eStation-Apps/%{name}-%{version}-%{release}.tgz
BuildRoot: %{_topdir}/BUILD/%{name}-%{version}-%{release}

# Procedure: the whole eStation2.git repo is synchronized on the local machine (in /home/adminuser/eStation2.git) 
#	     A Package with all /src contents is packed in a .tgz (in %{Source}), 
#	     and subsequently unpacked in the BUILD_ROOT dir

%description
%summary

%prep
# Sync the git repository from github
cd /home/adminuser/eStation2.git			# -> TEMP: locally unzippped manually
git pull origin main		  			# -> TEMP: locally unzippped manually
# Create the .tgz
# cd /home/adminuser/estation2.MESA-main/src
cd src
tar -cvzf /home/adminuser/rpms/eStation-Apps/%{name}-%{version}-%{release}.tgz *

# Prepare the files in BUILD_ROOT
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/var/www/eStation2-%{version}
cd $RPM_BUILD_ROOT
cp /home/adminuser/rpms/eStation-Apps/%{name}-%{version}-%{release}.tgz ./var/www/eStation2-%{version}
cd ./var/www/eStation2-%{version}
tar -xvzf eStation2-Apps-%{version}-%{release}.tgz
rm eStation2-Apps-%{version}-%{release}.tgz

%clean
rm -r -f $RPM_BUILD_ROOT

%files
/var/www/eStation2-%{version}/*
%config /var/www/eStation2-%{version}/apps/es2system/GeoPortal/geoportal.conf

####%config(noreplace) /var/www/eStation2-%{version}/*

%pre
# Create log file
mkdir -p /var/log/eStation2
touch /var/log/eStation2/%{name}-%{version}-preinst.log
touch /var/log/eStation2/%{name}-%{version}-preinst.err

exec 1>/var/log/eStation2/%{name}-%{version}-preinst.log
exec 2>/var/log/eStation2/%{name}-%{version}-preinst.err

# Stop the eStation Services (for upgrade)
echo "`date +'%Y-%m-%d %H:%M '` Stopping all services"
if [[ -d /var/www/eStation2 ]]; then 
/etc/init.d/tas_all_servicesd stop
fi
# En preinst pas de script externe inclus dans le RPM car pas encore decompressé
# Ajout du compte analyst
echo "`date +'%Y-%m-%d %H:%M '` Checking/creating analyst User"
getent passwd analyst >/dev/null || useradd -c "eStation Thematic User" -s /bin/bash -m -p '$1$QzIcDpOX$MTmh852fnqwQm3MSFyRq10' analyst
# Ajout du compte adminuser
echo "`date +'%Y-%m-%d %H:%M '` Checking/creating Admin"
getent passwd adminuser >/dev/null || useradd -c "eStation Administrator" -s /bin/bash -m -p '$1$QzIcDpOX$MTmh852fnqwQm3MSFyRq10' adminuser
# Ajout du groupe estation
echo "`date +'%Y-%m-%d %H:%M '` Checking/creating estation Group"
getent group estation >/dev/null || groupadd estation
# Association des utilisateurs aux groupes
echo "`date +'%Y-%m-%d %H:%M '` Checking/adding Users to Groups"
awk -F':' '/estation/{print $4}' /etc/group | grep adminuser >/dev/null || usermod -a -G estation adminuser
awk -F':' '/apache/{print $4}' /etc/group | grep analyst >/dev/null || usermod -a -G apache analyst
awk -F':' '/estation/{print $4}' /etc/group | grep analyst >/dev/null || usermod -a -G estation analyst

echo "`date +'%Y-%m-%d %H:%M '` Adding adminuser to sudoers"
echo "adminuser	All=(ALL) ALL" >> /etc/sudoers

%post
# Create log file
echo "`date +'%Y-%m-%d %H:%M '` Create log files"
mkdir -p /var/log/eStation2
touch /var/log/eStation2/%{name}-%{version}-postinst.log
touch /var/log/eStation2/%{name}-%{version}-postinst.err
exec 1>/var/log/eStation2/%{name}-%{version}-postinst.log
exec 2>/var/log/eStation2/%{name}-%{version}-postinst.err

# Change code owner/perms
echo "`date +'%Y-%m-%d %H:%M '` Assign /var/www/eStation to adminuser"
chown adminuser:adminuser -R /var/www/eStation2-%{version}
echo "`date +'%Y-%m-%d %H:%M '` Change permissions of /var/www/eStation"
chmod 755 -R /var/www/eStation2-%{version}

# Create temporary path 
echo "`date +'%Y-%m-%d %H:%M '` Create temporary paths"
mkdir -p -m 775 /tmp/eStation2/
mkdir -p -m 775 /tmp/eStation2/services/
mkdir -p -m 775 /tmp/eStation2/processing/
mkdir -p -m 775 /tmp/eStation2/ingested_files/
chown -R analyst:estation /tmp/eStation2/

# Creating temporary path in tmp after boot (in case of). Configuration of rc.local
echo "`date +'%Y-%m-%d %H:%M '` Create temporary paths in rc.local"
grep "rm -fr /tmp/eStation2/app" /etc/rc.local >/dev/null ||echo "rm -fr /tmp/eStation2/apps.*" >> /etc/rc.local
grep "mkdir -p -m 775 /tmp/eStation2/" /etc/rc.local >/dev/null ||echo "mkdir -p -m 775 /tmp/eStation2/" >> /etc/rc.local
grep "mkdir -p -m 775 /tmp/eStation2/services/" /etc/rc.local >/dev/null ||echo "mkdir -p -m 775 /tmp/eStation2/services/" >> /etc/rc.local
grep "mkdir -p -m 775 /tmp/eStation2/processing/" /etc/rc.local >/dev/null ||echo "mkdir -p -m 775 /tmp/eStation2/processing/" >> /etc/rc.local
grep "mkdir -p -m 775 /tmp/eStation2/ingested_files/" /etc/rc.local >/dev/null ||echo "mkdir -p -m 775 /tmp/eStation2/ingested_files/" >> /etc/rc.local
grep "chown -R analyst:estation /tmp/eStation2/" /etc/rc.local >/dev/null ||echo "chown -R analyst:estation /tmp/eStation2/" >> /etc/rc.local

# Creation of /estation2 path
echo "`date +'%Y-%m-%d %H:%M '` Create eStation2 paths"
mkdir -p -m 775 /eStation2
mkdir -p -m 775 /eStation2/settings
mkdir -p -m 775 /eStation2/get_lists
mkdir -p -m 775 /eStation2/get_lists/get_internet
mkdir -p -m 775 /eStation2/get_lists/get_eumetcast
mkdir -p -m 777 /eStation2/log
mkdir -p -m 775 /eStation2/db_dump
mkdir -p -m 775 /eStation2/requests
mkdir -p -m 775 /eStation2/system
chown -R analyst:estation /eStation2/

# Creation of /data path
echo "`date +'%Y-%m-%d %H:%M '` Create /data paths"
mkdir -p -m 775 /data/ingest
mkdir -p -m 775 /data/ingest.wrong
mkdir -p -m 775 /data/processing
mkdir -p -m 775 /data/spirits

# Change owner of /data/
echo "`date +'%Y-%m-%d %H:%M '` Assign /data to analyst User"
chown -R analyst:estation /data/ 

# Change permissions /var/www (for allowing analyst to change version)
chmod 777 /var/www

# Change permissions for writing in Desktop
chown -R adminuser:adminuser /home/adminuser/*
chmod -R 755 /home/adminuser/Desktop
chown -R analyst:analyst /home/analyst/*
chmod -R 755 /home/analyst/Desktop

# Change permissions of the Layers dir (2.0.4) -> it is done in layers-2.0.4
#echo "`date +'%Y-%m-%d %H:%M '` Change permissions of /eStation2/layers to 775"
#chmod 775 -R /eStation2/layers

# Creation of the symlink on the /var/www/eStation2-%{version}
echo "`date +'%Y-%m-%d %H:%M '` Create sym link /var/www/eStation2-%{version}"
is_an_upgrade=0
if [[ -d /var/www/eStation2 ]]; then 
rm /var/www/eStation2
is_an_upgrade=1
fi
ln -fs /var/www/eStation2-%{version} /var/www/eStation2

# Change settings of apache for layer size (2.0.4)
if [[ ${is_an_upgrade} == 1 ]]; then
echo "`date +'%Y-%m-%d %H:%M '` Change apache config LimitRequestBody to 300Mb"
apache_config='/usr/local/src/tas/eStation_wsgi_srv/httpd.conf'
sed -i "s|.*LimitRequestBody.*|LimitRequestBody 314572800|" ${apache_config}
fi

# Restart postgresql 
echo "`date +'%Y-%m-%d %H:%M '` Restart postgresql-9.3"
/etc/init.d/postgresql-9.3 restart
if [ $? -eq 0 ]; then
    echo "`date +'%Y-%m-%d %H:%M '` Postgresql restarted"				 	
else
    echo "`date +'%Y-%m-%d %H:%M '` ERROR in restarting Postgresql"
fi
echo "`date +'%Y-%m-%d %H:%M '` Wait for postgresql-9.3 restart ..."
sleep 3
# localhost reachable
echo "`date +'%Y-%m-%d %H:%M '` Check localhost is reachable"
if [[ `nc -v -z localhost 5432 1>/dev/null 2>&1;echo $?` -eq 0 ]]; then
    echo "`date +'%Y-%m-%d %H:%M '` Postgresql is running" 
    # estation User exists ?
    if [[ `su postgres -c "psql -c 'select usename from pg_user'"  2>/dev/null|grep estation` == '' ]];then
        echo "`date +'%Y-%m-%d %H:%M '` Create estation User" 
        su postgres -c psql << EOF
CREATE USER estation;
EOF
    else
        echo "`date +'%Y-%m-%d %H:%M '` User estation already exists. Continue" 
    fi
    # estationdb exists ?
    if [[ `su postgres -c "psql -c 'select datname from pg_database'"  2>/dev/null|grep estationdb` == '' ]];then
        echo "`date +'%Y-%m-%d %H:%M '` Create estationdb Database" 
        su postgres -c psql << EOF
ALTER ROLE estation WITH CREATEDB;
CREATE DATABASE estationdb WITH OWNER estation TEMPLATE template0 ENCODING 'UTF8';
ALTER USER estation WITH ENCRYPTED PASSWORD 'mesadmin';
EOF
    else
        echo "`date +'%Y-%m-%d %H:%M '` DB estationdb already exists. Continue" 
    fi

    if [[ ! `su postgres -c "psql -d estationdb -c 'select * from products.mapset'" 2> /dev/null` ]];then
        # First install from scratch data
        echo "`date +'%Y-%m-%d %H:%M '` Create database structure" 
        # Create database initial version (2.0.2)
        psql -h localhost -U estation -d estationdb -f /var/www/eStation2/database/dbInstall/products_dump_structure_only.sql >/dev/null 2>&1
    else
        echo "`date +'%Y-%m-%d %H:%M '` Database structure already exists. Continue" 
    fi
    # Update database structure to current release
    echo "`date +'%Y-%m-%d %H:%M '` Update database structure" 
    psql -h localhost -U estation -d estationdb -f /var/www/eStation2/database/dbInstall/update_db_structure.sql >/var/log/eStation2/%{name}-%{version}-update_db_structure.log 2>/var/log/eStation2/%{name}-%{version}-update_db_structure.err

    # Activate the User THEMA in the thema table (since 2.1.0)
    thema=`grep -i thema /eStation2/settings/system_settings.ini | sed 's/thema =//'| sed 's/ //g'`
    psql -U estation -d estationdb -c "update products.thema SET activated=TRUE WHERE thema_id='$thema'"
    echo "`date +'%Y-%m-%d %H:%M '` Thema acivated in the products.thema table"


    # Update Tables (both for upgrade and installation from scratch)
    echo "`date +'%Y-%m-%d %H:%M '` Populate/update tables" 
    psql -h localhost -U estation -d estationdb -f /var/www/eStation2/database/dbInstall/update_insert_jrc_data.sql >/var/log/eStation2/%{name}-%{version}-update_insert_jrc_data.log 2>/var/log/eStation2/%{name}-%{version}-update_insert_jrc_data.err

else
    echo "`date +'%Y-%m-%d %H:%M '` Postgresql is NOT running: DB not created !" 
fi # localhost reachable

# Copy the User Settings file (if does not exist)
src_file='/var/www/eStation2/config/install/user_settings.ini'
trg_file='/eStation2/settings/user_settings.ini'

if [ -f  ${trg_file} ]; then
    echo "`date +'%Y-%m-%d %H:%M '` User Setting file already exist $trg_file" 
else
    cp $src_file $trg_file
    if [ $? -eq 0 ]; then 
        echo "`date +'%Y-%m-%d %H:%M '` User Setting file $trg_file created" 
        chown analyst:estation ${trg_file}
        chmod 775 ${trg_file}
    else
        echo "`date +'%Y-%m-%d %H:%M '` ERROR in creating User Setting file $trg_file" 
    fi
fi

# Copy the System Settings file (if does not exist)
src_file='/var/www/eStation2/config/install/system_settings.ini'
trg_file='/eStation2/settings/system_settings.ini'

if [[ -f  ${trg_file} ]]; then
    echo "`date +'%Y-%m-%d %H:%M '` System Setting file already exist $trg_file" 
else
    cp $src_file $trg_file
    if [[ $? -eq 0 ]]; then 
        echo "`date +'%Y-%m-%d %H:%M '` System Setting file $trg_file created" 
        chown analyst:estation ${trg_file}
        chmod 775 ${trg_file}
    else
        echo "`date +'%Y-%m-%d %H:%M '` ERROR in creating System Setting file $trg_file" 
    fi
fi

# Initialize the bucardo installation
log_dir="/var/log/bucardo"
run_dir="/var/run/bucardo"

# Check if the bucardo db already exists
if [[ `su postgres -c "psql -c 'select datname from pg_database'"  2>/dev/null|grep bucardo` == '' ]];then
	/usr/bin/bucardo install --batch --dbname estationdb --dbhost localhost
	echo "$(date +'%Y-%m-%d %H:%M ') Bucardo package installed"
else
	echo "$(date +'%Y-%m-%d %H:%M ') Bucardo package already installed. Continue"
fi
bucardo set log_level=terse
bucardo set reason_file='/var/log/bucardo/bucardo.restart.reason'

# Create log and run dir for Bucardo
mkdir -p ${log_dir}
chown adminuser:estation ${log_dir}
chmod 777 ${log_dir}
mkdir -p ${run_dir}
chown adminuser:estation ${run_dir}
chmod 777 ${run_dir}
#chmod 666 /home/adminuser/.pgpass

# Set the 'role' in system_settings
my_role=$(hostname | cut -d '-' -f2)
sed -i "s|.*role.=.*|role = ${my_role}|" /eStation2/settings/system_settings.ini

# Set the 'version' in system_settings
sed -i "s|.*active_version.=.*|active_version = %{version}|" /eStation2/settings/system_settings.ini

# Check the link of libmapserver exist
#if [[ ! -h /usr/lib64/libmapserver.so ]]; then ln -fs /usr/local/lib64/libmapserver.so /usr/lib64/; fi
#if [[ ! -h /usr/lib64/libmapserver.so.1 ]]; then ln -fs /usr/local/lib64/libmapserver.so.1 /usr/lib64/; fi
#if [[ ! -h /usr/lib64/libmapserver.so.6.4.1 ]]; then ln -fs /usr/local/lib64/libmapserver.so.6.4.1 /usr/lib64/; fi

# Specific to upgrade from 2.0.2 -> re-set the THEMA (for pads settings table)
# thema=`grep -i thema /eStation2/settings/system_settings.ini | sed 's/thema =//'| sed 's/ //g'`
# psql -U estation -d estationdb -c "select products.set_thema('$thema')"
# echo "`date +'%Y-%m-%d %H:%M '` Set again the Thema to $thema"

# Start the eStation Services 
echo "`date +'%Y-%m-%d %H:%M '` Starting all services"
if [[ ${is_an_upgrade} == 1 ]]; then
/etc/init.d/tas_all_servicesd start
fi

# Before uninstall: remove the link and copy all code into a bck dir
%preun
mkdir -p /var/www/eStation2-%{version}.bck
cp -r /var/www/eStation2-%{version}/* /var/www/eStation2-%{version}.bck/

# After uninstall: remove /tmp files, and move the .bck dir to 'old-version' place
%postun
rm -fr /var/www/eStation2-%{version}
mv /var/www/eStation2-%{version}.bck /var/www/eStation2-%{version}
chown adminuser:estation -R /var/www/eStation2-%{version}
chmod 755 -R /var/www/eStation2-%{version}

