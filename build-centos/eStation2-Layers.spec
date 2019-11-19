Summary: eStation 2.0 reference Layers for visualization
Name: eStation2-Layers
Version: 2.2.0
Release: 1
Group: eStation
License: GPL
Source: /home/adminuser/rpms/eStation-Layers-%{version}/%{name}-%{version}-%{release}.tgz
BuildRoot: %{_topdir}/BUILD/%{name}-%{version}-%{release}


# Procedure: the files are/were downloaded from JRC site, packed in a .tgz (in %{Source}), 
#	     and subsequently unpacked in the BUILD_ROOT dir


%description
%summary

%prep
# Get the sources from the JRC ftp and create .tgz

echo ""
echo "WARNING: files have to be manually copied into /home/adminuser/rpms/eStation-Layers-%{version}/"
echo ""

lftp -e "mirror -Le /ftp/private/narma/eStation_2.0/Packages/eStation-Layers-%{version}/ /home/adminuser/ISOs-RPMs/eStation-Layers-%{version}/; exit" -u narma:JRCVRw2960 srv-ies-ftp.jrc.it"" 
cd /home/adminuser/ISOs-RPMs/eStation-Layers-%{version}/
rm -f %{name}-%{version}-%{release}.rpm
rm -f %{name}-%{version}-%{release}.tgz

tar -cvzf %{name}-%{version}-%{release}.tgz *

# Prepare the Layers in BUILD_ROOT
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/eStation2/layers
cd $RPM_BUILD_ROOT 
cp %{SOURCEURL0} ./eStation2/layers
cd ./eStation2/layers
#tar -xvzf %{name}-%{version}-%{release}.tgz
#rm %{name}-%{version}-%{release}.tgz
%clean
rm -r -f $RPM_BUILD_ROOT

%files
/eStation2/layers/*.tgz

%post
# Extract the layers
echo "`date +'%Y-%m-%d %H:%M '` Extract the layers." 
tar -xvzf /eStation2/layers/eStation2-Layers-%{version}-%{release}.tgz -C /eStation2/layers/

# Change ownership and permissions of the layers
chown -R analyst:estation /eStation2/layers
chmod -R 775 /eStation2/layers

# Before uninstall: remove the link and copy all code into a bck dir
echo "`date +'%Y-%m-%d %H:%M '` Populate analysis.layers table" 
psql -h localhost -U estation -d estationdb -f /eStation2/layers/insert_%{name}_%{version}.sql >/dev/null 2>&1

