Summary: eStation 2.0 Documentation
Name: eStation2-Docs
Version: 2.1.2
Release: 1
Group: eStation
License: GPL
Source: /home/adminuser/rpms/eStation-Docs/%{name}-%{version}-%{release}.tgz
BuildRoot: %{_topdir}/BUILD/%{name}-%{version}-%{release}


# Procedure: the files are downloaded from JRC site, packed in a .tgz (in %{Source}), 
#	     and subsequently unpacked in the BUILD_ROOT dir

%description
%summary

%prep
# Get the sources from the JRC ftp and create .tgz
lftp -e "mirror -Le /ftp/private/narma/eStation_2.0/Packages/eStation-Docs /home/adminuser/rpms/; exit" -u narma:JRCVRw2960 srv-ies-ftp.jrc.it"" 
cd /home/adminuser/rpms/eStation-Docs/
rm -f %{name}-%{version}-%{release}.rpm
tar -cvzf %{name}-%{version}-%{release}.tgz --exclude=*.tgz *

# Prepare the Layers in BUILD_ROOT
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/eStation2/docs
cd $RPM_BUILD_ROOT 
cp %{SOURCEURL0} ./eStation2/docs
cd ./eStation2/docs
tar -xvzf %{name}-%{version}-%{release}.tgz
rm %{name}-%{version}-%{release}.tgz

%clean
rm -r -f $RPM_BUILD_ROOT

%files
/eStation2/docs/*

