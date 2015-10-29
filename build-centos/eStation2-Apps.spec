Summary: eStation 2.0 application from JRC
Name: eStation2-Apps
Version: 2.0.1
Release: 1
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

%post
# Create log file
mkdir -p /var/log/eStation2
touch /var/log/eStation2/%{name}-%{version}-postinst.log
# Change code owner/perms
chown adminuser:adminuser -R /var/www/eStation2-%{version}
chmod 755 -R /var/www/eStation2-%{version}

