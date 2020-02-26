#
# Note: this script can generate several 'additional' Layers package, by changing the 'Name' below (a1,a2,a3 ..)
#
Summary: eStation 2.0 reference Layers - Additional package
Name: eStation2-Layers-a0
Version: 2.0.4
Release: 1
Group: eStation
License: GPL
Source: /home/adminuser/rpms/%{name}/%{name}.tgz
BuildRoot: %{_topdir}/BUILD/%{name}


# Procedure: the files are downloaded from JRC site, packed in a .tgz (in %{Source}), 
#	     and subsequently unpacked in the BUILD_ROOT dir


%description
%summary

%prep
# Get the sources from the JRC ftp and create .tgz
echo "WARNING: all new files have to be copied manually into /home/adminuser/rpms/%{name}/"
###lftp -e "mirror -Le /ftp/private/narma/eStation_2.0/Packages/%{name}/ /home/adminuser/rpms/%{name}/; exit" -u narmauser:2016mesa! h05-ftp.jrc.it"" 

cd /home/adminuser/rpms/%{name}/
rm -f %{name}.rpm
tar -cvzf %{name}.tgz *

# Prepare the Layers in BUILD_ROOT
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/eStation2/layers
cd $RPM_BUILD_ROOT 
cp %{SOURCEURL0} ./eStation2/layers
cd ./eStation2/layers
tar -xvzf %{name}.tgz
rm %{name}.tgz
%clean
rm -r -f $RPM_BUILD_ROOT

%files
/eStation2/layers/*

%post
# Change ownership and permissions of the layers
chown -R analyst:estation /eStation2/layers
chmod -R 775 /eStation2/layers

# Insert the relevant records in analysis.layers 
echo "`date +'%Y-%m-%d %H:%M '` Populate analysis.layers table" 
psql -h localhost -U estation -d estationdb -f /eStation2/layers/insert_%{name}.sql >/dev/null 2>&1

