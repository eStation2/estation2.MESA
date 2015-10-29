Summary: eStation 2.0 Documentation
Name: eStation2-Docs
Version: 2.0.1
Release: 1
Group: eStation
License: GPL
Source: /home/adminuser/rpms/Docs/%{name}-%{version}-%{release}.tgz
BuildRoot: %{_topdir}/BUILD/%{name}-%{version}-%{release}


# Procedure: the files are downloaded from JRC site, packed in a .tgz (in %{Source}), 
#	     and subsequently unpacked in the BUILD_ROOT dir

%description
%summary

%prep
# Get the sources from the JRC ftp and create .tgz
lftp -e "mirror -Le /ftp/private/narma/eStation_2.0/Packages/eStation-Docs/ /home/adminuser/rpms/Docs/; exit" -u narmauser:narma11 h05-ftp.jrc.it"" 
cd /home/adminuser/rpms/Docs/
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

