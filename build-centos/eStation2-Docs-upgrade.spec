Summary: eStation 2.0 Documentation
Name: eStation2-Docs
Version: 2.1.2
Release: 4
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
# lftp -e "mirror -Le /ftp/private/narma/eStation_2.0/Packages/eStation-Docs /home/adminuser/rpms/; exit" -u narmauser:JRCkOq7478 srv-ies-ftp.jrc.it"" 
# lftp -c "open -u narmauser,JRCkOq7478 sftp://srv-ies-ftp.jrc.it; mirror -c -L -e  /FTP/pvt/narma/narma/eStation_2.0/Packages/eStation-Docs /home/adminuser/rpms/"

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
echo "Renaming/copying the package under /home/adminuser/rpms"
cp /rpm/rpmbuild/RPMS/x86_64/%{name}-%{version}-%{release}.x86_64.rpm /home/adminuser/rpms/eStation-Docs/mesa2015-%{name}-%{version}-%{release}.x86_64.rpm

%files
/eStation2/docs/*

%pre
# Create log file
mkdir -p /var/log/eStation2
touch /var/log/eStation2/%{name}-%{version}-preinst.log
touch /var/log/eStation2/%{name}-%{version}-preinst.err

exec 1>/var/log/eStation2/%{name}-%{version}-preinst.log
exec 2>/var/log/eStation2/%{name}-%{version}-preinst.err

# Change permissions for writing in /eStation2/docs
echo "`date +'%Y-%m-%d %H:%M '` Change permissions for writing in /eStation2/docs"
mkdir -p /eStation2/docs
chown -R adminuser:estation /eStation2/docs
chmod -R 755 /eStation2/docs


%post
# Create log file
echo "`date +'%Y-%m-%d %H:%M '` Create log files"
mkdir -p /var/log/eStation2
touch /var/log/eStation2/%{name}-%{version}-postinst.log
touch /var/log/eStation2/%{name}-%{version}-postinst.err
exec 1>/var/log/eStation2/%{name}-%{version}-postinst.log
exec 2>/var/log/eStation2/%{name}-%{version}-postinst.err

# Change permissions for writing in /eStation2/docs
echo "`date +'%Y-%m-%d %H:%M '` Change permissions for writing in /eStation2/docs"
mkdir -p /eStation2/docs
chown -R adminuser:estation /eStation2/docs
chmod -R 755 /eStation2/docs


# Before uninstall: copy all docs into a bck dir to keep all the docs
%preun
mkdir -p /eStation2/docs-%{version}.bck
cp -r /eStation2/docs/* /eStation2/docs-%{version}.bck/


# After uninstall: move the .bck dir to /eStation2/docs to keep all the docs
%postun
rm -fr /eStation2/docs/
mv /eStation2/docs-%{version}.bck /eStation2/docs
chown adminuser:estation -R /eStation2/docs
chmod 755 -R /eStation2/docs
