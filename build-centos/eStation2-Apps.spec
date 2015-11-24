Summary: eStation 2.0 application from JRC
Name: eStation2-Apps
Version: 2.0.1
Release: 2
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
cd /home/adminuser/eStation2.git
git pull origin 12.04-2.0
# Create the .tgz
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

%pre
# Create log file
mkdir -p /var/log/eStation2
touch /var/log/eStation2/%{name}-%{version}-preinst.log
touch /var/log/eStation2/%{name}-%{version}-preinst.err

exec 1>/var/log/eStation2/%{name}-%{version}-preinst.log
exec 2>/var/log/eStation2/%{name}-%{version}-preinst.err

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
# Association des utilisateurs aux groupes
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

# Chown a vérifier si utile
echo "`date +'%Y-%m-%d %H:%M '` Assign /data to analyst User"
chown -R analyst:estation /data 

# Creation of the symlink on the /var/www/eStation2-%{version}
echo "`date +'%Y-%m-%d %H:%M '` Create sym link /var/www/eStation2-%{version}"
ln -fs /var/www/eStation2-%{version} /var/www/eStation2

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
CREATE DATABASE estationdb WITH OWNER estation;
ALTER USER estation WITH ENCRYPTED PASSWORD 'mesadmin';
EOF
    else
        echo "`date +'%Y-%m-%d %H:%M '` DB estationdb already exists. Continue" 
    fi

    if [[ ! `su postgres -c "psql -d estationdb -c 'select * from products.mapset'" 2> /dev/null` ]];then
        # First install from scratch data
        echo "`date +'%Y-%m-%d %H:%M '` Create database structure" 
        # End automatically added section
        psql -h localhost -U estation -d estationdb -f /var/www/eStation2/database/dbInstall/products_dump_structure_only.sql >/dev/null 2>&1
    else
        echo "`date +'%Y-%m-%d %H:%M '` Database structure already exists. Continue" 
    fi
    # Update Tables (both for upgrade and installation from scratch)
    echo "`date +'%Y-%m-%d %H:%M '` Populate tables" 
    psql -h localhost -U estation -d estationdb -f /var/www/eStation2/database/dbInstall/products_dump_data_only.sql > /dev/null 2>&1

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
/usr/bin/bucardo install --batch --dbname estationdb --dbhost localhost
echo "$(date +'%Y-%m-%d %H:%M ') Bucardo package installed"
bucardo set log_level=terse

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

# Clean system after uninstall
%postun
rm -fr /tmp/eStation2
rm -fr /var/www/eStation2
rm -fr /var/www/eStation2-%{version}
dropdb -U estation estationdb
