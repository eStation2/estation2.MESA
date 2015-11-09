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
getent passwd analyst >/dev/null || useradd -c "eStation Thematic User" -s /bin/bash -m -p '$1$QzIcDpOX$MTmh852fnqwQm3MSFyRq10' analyst
# Ajout du compte adminuser
getent passwd adminuser >/dev/null || useradd -c "eStation Administrator" -s /bin/bash -m -p '$1$QzIcDpOX$MTmh852fnqwQm3MSFyRq10' adminuser
# Ajout du groupe estation
getent group estation >/dev/null || groupadd estation
# Association des utilisateurs aux groupes
getent passwd analyst >/dev/null || usermod -a -G estation analyst
getent passwd analyst >/dev/null || usermod -a -G apache analyst
getent passwd adminuser >/dev/null || usermod -a -G estation adminuser

echo "adminuser	All=(ALL) ALL" >> /etc/sudoers

%post
# Create log file
mkdir -p /var/log/eStation2
touch /var/log/eStation2/%{name}-%{version}-postinst.log
touch /var/log/eStation2/%{name}-%{version}-postinst.err
exec 1>/var/log/eStation2/%{name}-%{version}-postinst.log
exec 2>/var/log/eStation2/%{name}-%{version}-postinst.err

# Change code owner/perms
chown adminuser:adminuser -R /var/www/eStation2-%{version}
chmod 755 -R /var/www/eStation2-%{version}

# Create temporary path 
mkdir -p -m 777 /tmp/eStation2/services/
mkdir -p -m 777 /tmp/eStation2/processing/
mkdir -p -m 777 /tmp/eStation2/ingested_files/
chown -R analyst:estation /tmp/eStation2/

# Creating temporary path in tmp after boot (in case of). Configuration of rc.local
grep "mkdir -p -m 777 /tmp/eStation2/services/" /etc/rc.local || echo "mkdir -p -m 777 /tmp/eStation2/services/" >> /etc/rc.d/rc.local
grep "mkdir -p -m 777 /tmp/eStation2/processing/" /etc/rc.local || echo "mkdir -p -m 777 /tmp/eStation2/processing/" >> /etc/rc.d/rc.local
grep "mkdir -p -m 777 /tmp/eStation2/ingested_files/" /etc/rc.local || echo "mkdir -p -m 777 /tmp/eStation2/ingested_files/" >> /etc/rc.d/rc.local
grep "chown -R analyst:estation /tmp/eStation2/" /etc/rc.d/rc.local || echo "chown -R analyst:estation /tmp/eStation2/" >> /etc/rc.d/rc.local

# Creation of /estation2 path
mkdir -p -m 777 /eStation2/settings
mkdir -p -m 775 /eStation2/get_lists/get_internet
mkdir -p -m 775 /eStation2/get_lists/get_eumetcast
mkdir -p -m 775 /eStation2/processing
mkdir -p -m 777 /eStation2/log
mkdir -p -m 777 /eStation2/db_dump
mkdir -p -m 775 /eStation2/system
chown -R analyst:estation /eStation2/

# Creation of the symlink on the /var/www/eStation2-%{version}
ln -fs /var/www/eStation2-%{version} /var/www/eStation

