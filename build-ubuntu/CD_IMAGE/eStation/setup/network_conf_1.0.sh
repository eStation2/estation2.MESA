#!/bin/sh
# Modified for 2.0
# date 29/6/2015
# Change_IP.sh IP_ACQ IP_PC2 IP_PC3 IP_DNS IP_GAT IP_LAN in /etc/hosts ; /etc/interfaces and other config files
#	
#	It expects the following network hostnames to be defined on the PCs: 
#		PC1 -> Acquisition.eStation
#		PC2 -> eStation-PS.eStation
#		PC3 -> eStation-EMMA.eStation
#
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
	sed -i "s|.*Acquisition.eStation|${IP_PC1} Acquisition.eStation|g" /etc/hosts
	sed -i "s|.*eStation-PS.eStation|${IP_PC2} eStation-PS.eStation|g" /etc/hosts
	sed -i "s|.*eStation-EMMA.eStation|${IP_PC3} eStation-EMMA.eStation|g" /etc/hosts

	if [ "$(uname -n)" = "eStation-PS" ];then
		sed -i "s|address.*|address ${IP_PC2}|g" /etc/network/interfaces
	fi

	if [ "$(uname -n)" = "eStation-EMMA" ];then
		sed -i "s|address.*|address ${IP_PC3}|g" /etc/network/interfaces
	fi
	IP_NET=$(echo ${IP_PC2}|awk -F. '{print $1"."$2"."$3".0"}')
	sed -i "s|network.*|network ${IP_NET}|g" /etc/network/interfaces
	IP_BROADCAST=$(echo ${IP_PC2}|awk -F. '{print $1"."$2"."$3".255"}')
	sed -i "s|broadcast.*|broadcast ${IP_BROADCAST}|g" /etc/network/interfaces
	sed -i "s|dns-nameservers.*|dns-nameservers ${IP_DNS}|g" /etc/network/interfaces
	sed -i "s|gateway.*|gateway ${IP_GAT}|g" /etc/network/interfaces

	sed -i "s|nameserver.*|nameserver ${IP_DNS}|g" /etc/resolv.conf
	# To be changed (original 192.168.0.0 used)
	sed -i "s|192.168.0.0/24|0.0.0.0/0|g" /etc/postgresql/8.3/main/pg_hba.conf
	# To be kept ?
	sed -i "s|hosts allow=.*|hosts allow=${IP_LAN}|g" /etc/rsyncd.conf
fi

exit 0
