#!/bin/sh
# Modified for 2.0
# date 29/6/2015
# Usage: network_config_1.0.sh IP_ACQ IP_PC2 IP_PC3 IP_DNS IP_GAT IP_LAN 
# Changes IPs in /etc/hosts ; /etc/interfaces and other config files
#
# It expects the following network hostnames to be defined on the PCs:
# PC1 -> Acquisition
# PC2 -> mesa-1
# PC3 -> mesa-2
#
# Important NOTE: hostnames STILL to be DEFINED on MESA Stations
hostname_pc1='Acquisition'
hostname_pc2='mesa-1'
hostname_pc3='mesa-2'

# Check number of parameters

if [ $# -ne 6 ]; then
	echo " The script requires exactly 6 parameters. Exit"
	exit
fi

IP_PC1=$1
IP_PC2=$2
IP_PC3=$3
IP_DNS=$4
IP_GAT=$5
IP_LAN=$6
for ip in $IP_PC1 $IP_GAT $IP_DNS $IP_VIP $IP_EMMA $IP_PS;do
	IP_ADDR_VAL=$(echo "$ip" | grep -Ec '^(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])$')
	if [ $IP_ADDR_VAL -eq 0 ]; then
		zenity --error --title="LAN Configuration" --text "Bad IP : ${ip}."
		exit 2
	fi
done
if [ $? -eq 0 ];then
	# Manage /etc/hosts
	sed -i "s|.*${hostname_pc1}|${IP_PC1} ${hostname_pc1}|g" /etc/hosts
	sed -i "s|.*${hostname_pc2}|${IP_PC2} ${hostname_pc2}|g" /etc/hosts
	sed -i "s|.*${hostname_pc3}|${IP_PC3} ${hostname_pc3}|g" /etc/hosts
	if [ "$(uname -n)" = "${hostname_pc2}" ];then
		echo "Changing address in /etc/network/interfaces"
		sed -i "s|address.*|address ${IP_PC2}|g" /etc/network/interfaces
	fi
	if [ "$(uname -n)" = "${hostname_pc3}" ];then
		sed -i "s|address.*|address ${IP_PC3}|g" /etc/network/interfaces
		echo "Changing address in /etc/network/interfaces"
	fi
	IP_NET=$(echo ${IP_PC2}|awk -F. '{print $1"."$2"."$3".0"}')
	sed -i "s|network.*|network ${IP_NET}|g" /etc/network/interfaces
	IP_BROADCAST=$(echo ${IP_PC2}|awk -F. '{print $1"."$2"."$3".255"}')
	sed -i "s|broadcast.*|broadcast ${IP_BROADCAST}|g" /etc/network/interfaces
	sed -i "s|dns-nameservers.*|dns-nameservers ${IP_DNS}|g" /etc/network/interfaces
	sed -i "s|gateway.*|gateway ${IP_GAT}|g" /etc/network/interfaces
	sed -i "s|nameserver.*|nameserver ${IP_DNS}|g" /etc/resolv.conf
	# Just add a newline (if the IP_LAN is not present)
	new_line="host    all         all         ${IP_LAN}           trust"
	if [ $(grep -c "${new_line}" /etc/postgresql/9.3/main/pg_hba.conf) -le 0 ]; then 
		sed -i "s|# IPv4 local connections.*|# IPv4 local connections \nhost    all         all         ${IP_LAN}           trust|g" /etc/postgresql/9.3/main/pg_hba.conf
	fi
	# Update rsync config on local machine
	sed -i "s|.*hosts allow.*=.*|        hosts allow=${IP_LAN}|g" /etc/rsyncd.conf

fi
exit 0
