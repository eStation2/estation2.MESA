Summary: eStation 2.0 application from JRC
Name: eStation2-Apps
Version: 2.2.0
Release: 9
Group: eStation
License: GPL
Source: /home/adminuser/ISOs-RPMs/eStation-Apps/%{name}-%{version}-%{release}.tgz
BuildRoot: %{_topdir}/BUILD/%{name}-%{version}-%{release}

# Procedure: the whole eStation2.git repo is synchronized on the local machine (in /home/adminuser/eStation2.git) 
#	     A Package with all /src contents is packed in a .tgz (in %{Source}), 
#	     and subsequently unpacked in the BUILD_ROOT dir

%description
%summary

%prep
# Sync the git repository from github
cd /home/adminuser/eStation2.git			# -> TEMP: locally unzippped manually
# git pull origin main		  			# -> TEMP: locally unzippped manually
git pull origin dev_2.2.0

# Create the .tgz
cd src
tar -cvzf /home/adminuser/ISOs-RPMs/eStation-Apps/%{name}-%{version}-%{release}.tgz *

# Prepare the files in BUILD_ROOT
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/var/www/eStation2-%{version}
cd $RPM_BUILD_ROOT
cp /home/adminuser/ISOs-RPMs/eStation-Apps/%{name}-%{version}-%{release}.tgz ./var/www/eStation2-%{version}
cd ./var/www/eStation2-%{version}
tar -xvzf eStation2-Apps-%{version}-%{release}.tgz
rm eStation2-Apps-%{version}-%{release}.tgz

%clean
rm -r -f $RPM_BUILD_ROOT
echo "Renaming/copying the package under /home/adminuser/rpms"
cp /rpm/rpmbuild/RPMS/x86_64/%{name}-%{version}-%{release}.x86_64.rpm /home/adminuser/ISOs-RPMs/eStation-Apps/mesa2015-%{name}-%{version}-%{release}.x86_64.rpm

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
/etc/init.d/tas_estation_apached stop
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
mkdir -p -m 775 /eStation2/logos
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

# Change permissions for writing in home and Desktop
if [[ ! -d /home/adminuser/Desktop ]]; then
mkdir -p /home/adminuser/Desktop
fi
if [[ ! -d /home/analyst/Desktop ]]; then
mkdir -p /home/analyst/Desktop
fi
chown -R adminuser:adminuser /home/adminuser
chmod -R 755 /home/adminuser
chown -R analyst:analyst /home/analyst
chmod -R 755 /home/analyst

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
# if [[ ${is_an_upgrade} == 1 ]]; then
# echo "`date +'%Y-%m-%d %H:%M '` Change apache config LimitRequestBody to 300Mb"
# apache_config='/usr/local/src/tas/eStation_wsgi_srv/httpd.conf'
# sed -i "s|.*LimitRequestBody.*|LimitRequestBody 314572800|" ${apache_config}
# fi

# Change settings of apache for pointing to apps/gui/esapp/build/production (2.2.0)
echo "`date +'%Y-%m-%d %H:%M '` Change apache config file"
if [[ -f /usr/local/src/tas/eStation_wsgi_srv/httpd.conf ]]; then
mv /usr/local/src/tas/eStation_wsgi_srv/httpd.conf /usr/local/src/tas/eStation_wsgi_srv/httpd_pre_2.2.0.conf
cp /var/www/eStation2/config/install/httpd.conf /usr/local/src/tas/eStation_wsgi_srv/
fi

# Copy the System Settings file (if does not exist)
src_file='/var/www/eStation2/config/install/system_settings.ini'
trg_file='/eStation2/settings/system_settings.ini'

if [[ -f  ${trg_file} ]]; then
    echo "`date +'%Y-%m-%d %H:%M '` System Setting file already exists $trg_file" 
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

# Copy logos to /eStation2/logos - directory created above. (2.2.0)
echo "`date +'%Y-%m-%d %H:%M '` Copy logos to eStation2 - logos directory"
cp -rf /var/www/eStation2/config/install/logos/* /eStation2/logos


# Remove/reset the existing bucardo setup, so that system_bucardo_config() - driven by System service - will recreate the sync adding all tables
# This is especially important when there are new tables - in either analysis or products - to be added to bucardo-sync
if [[ ${is_an_upgrade} == 1 ]]; then
echo "`date +'%Y-%m-%d %H:%M '` Resetting bucardo"
/var/www/eStation2-%{version}/config/install/bucardo_reset.sh
echo "`date +'%Y-%m-%d %H:%M '` Bucardo Resetted"
# Stop Bucardo to prevent sync during DB update - see also ES2-112
bucardo stop
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
    echo "`date +'%Y-%m-%d %H:%M '` Thema activated in the products.thema table"


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
    echo "" >> $trg_file
    echo "proxy_host =" >> $trg_file
    echo "proxy_port =" >> $trg_file
    echo "proxy_user =" >> $trg_file
    echo "proxy_userpwd =" >> $trg_file
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
# Bucardo logfile and options - see also ES2-112
if [[ -f /var/log/bucardo/log.bucardo ]]; then
mv -f /var/log/bucardo/log.bucardo /var/log/bucardo/log.bucardo.bck
fi
bucardo set log_level=terse
bucardo set reason_file='/var/log/bucardo/bucardo.restart.reason'
# bucardo start # wait eStation2:system service to start it

# Create log and run dir for Bucardo
mkdir -p ${log_dir}
chown adminuser:estation -R ${log_dir}
chmod 777 -R ${log_dir}
mkdir -p ${run_dir}
chown adminuser:estation -R ${run_dir}
chmod 777 -R ${run_dir}

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

# Specific to upgrade from 2.1.2 -> set the activated THEMA in the table products.thema
if [[ ${is_an_upgrade} == 1 ]]; then
thema=`grep -i thema /eStation2/settings/system_settings.ini | sed 's/thema =//'| sed 's/ //g'`
psql -U estation -d estationdb -c "UPDATE products.thema SET activated = TRUE WHERE thema_id = '$thema'"
echo "`date +'%Y-%m-%d %H:%M '` Set the activated Thema to $thema in the table products.thema"
fi

# SNAP Install
# Check if snap is already installed -> not needed because it will be overwritten **** ->> To be changed !!!
if [[ -d /usr/local/snap/bin ]]; then 
	echo "`date +'%Y-%m-%d %H:%M '` SNAP already installed - remove and reinstall full version"
	rm -Rf /usr/local/snap
fi
#sudo chmod 777 /var/www/eStation2-%{version}/lib/snap/esa-snap_sentinel_unix_6_0.sh
mkdir -p /usr/local/snap
echo "`date +'%Y-%m-%d %H:%M '` Installing SNAP"
/var/www/eStation2-%{version}/lib/snap/esa-snap_all_unix_6_0.sh -q -dir "/usr/local/snap/"
echo "`date +'%Y-%m-%d %H:%M '` SNAP Installed!"

# Create a link for SNAP in the Desktop of adminuser and analyst 
cp /usr/local/snap/SNAP\ Desktop.desktop /home/adminuser/Desktop
cp /usr/local/snap/SNAP\ Desktop.desktop /home/analyst/Desktop


# Change location of pip in file /usr/local/src/tas/anaconda/bin/pip [ 16.08.19 - remove is_an_upgrade clause] 
#if [[ ${is_an_upgrade} == 1 ]]; then
echo "`date +'%Y-%m-%d %H:%M '` Change location of pip in file /usr/local/src/tas/anaconda/bin/pip"
pip_file='/usr/local/src/tas/anaconda/bin/pip'
newline='#!/usr/local/src/tas/anaconda/bin/python'
sed -i "s|#!.*|$newline|" ${pip_file}
#fi

# Install sentinelsat 
# Check if sentinelsat is already installed
if [[ -f /usr/local/src/tas/anaconda/bin/sentinelsat ]]; then 
	echo "`date +'%Y-%m-%d %H:%M '` sentinelsat already installed"
else
	echo "`date +'%Y-%m-%d %H:%M '`Installing sentinelsat"
	/usr/local/src/tas/anaconda/bin/pip install /var/www/eStation2-%{version}/lib/packages/sentinelsat/sentinelsat-0.13-py2.py3-none-any.whl -f /var/www/eStation2-%{version}/lib/packages/sentinelsat/ --no-index
fi

# Install motuclient
# Check if motuclient is already installed
if [[ -f /usr/local/src/tas/anaconda/bin/motuclient ]]; then 
	echo "`date +'%Y-%m-%d %H:%M '` motuclient already installed"
else
	echo "`date +'%Y-%m-%d %H:%M '`Installing motuclient"
	/usr/local/src/tas/anaconda/bin/pip install /var/www/eStation2-%{version}/lib/packages/motuclient/motuclient-1.8.2.tar.gz -f ./ --no-index
fi

# Run the patch to install Firefox 52.4.0 (if not already installed) **** ->> To be changed !!!
# echo "`date +'%Y-%m-%d %H:%M '` Run Firefox Upgrader"
# /var/www/eStation2/patches/updater_firefox_52.4.0.dbx
# echo "`date +'%Y-%m-%d %H:%M '` Firefox version now: `firefox -v | awk '{ print $3 }' 2>> /dev/null`"

# Start the eStation Services (16.08.19 - comment if clause) ->> ??????
echo "`date +'%Y-%m-%d %H:%M '` Starting all services"
#if [[ ${is_an_upgrade} == 1 ]]; then
/etc/init.d/tas_all_servicesd start
/etc/init.d/tas_estation_apached start
#fi
# Remove all the .json files so that the GUI will trigger regeneration automatically
if [[ ${is_an_upgrade} == 1 ]]; then
rm /tmp/eStation2/*.json
fi

# Import JRC Reference workspaces
echo "`date +'%Y-%m-%d %H:%M '` Importing JRC Reference workspaces"
su adminuser -c "/usr/local/src/tas/anaconda/bin/python -c 'import webpy_esapp_helpers; webpy_esapp_helpers.importJRCRefWorkspaces()'"

# Install Anydesk (see ES2-453)
if [[ ! `yum list installed | grep -i anydesk` ]]; then 
echo "`date +'%Y-%m-%d %H:%M '` Installing Anydesk 2.9.5"
sudo yum localinstall -y /var/www/eStation2/lib/anydesk/anydesk-2.9.5-1.el7.x86_64.rpm
else
echo "`date +'%Y-%m-%d %H:%M '` Anydesk 2.9.5 already installed"
fi

# Add an entry in crontab for running correct_normalize permissions (ES2-262)
if [[ ! `crontab -l | grep correct_normalize` ]]; then
echo "`date +'%Y-%m-%d %H:%M '` Add an entry in crontab for correcting/normalizing permissions"
crontab -l > /root/my_crontab.txt
echo '0 */3 * * * /var/www/eStation2/apps/es2system/correct_normalize_permissions.sh >> dev/null' >> /root/my_crontab.txt
crontab /root/my_crontab.txt
else
echo "`date +'%Y-%m-%d %H:%M '` The entry in crontab for correcting/normalizing permissions already exists."
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

