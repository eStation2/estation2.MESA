#
#   Assign network configuration
#   Usage: <name> PC2/PC3
#

#   Source the environment definition (cdrom ??)
. /cdrom/setup/iniEnv

#   Check the number of arguments
if [ "$#" -ne 1 ]; then
    echo " $0 - Error: no arguments passed. Exit" >> $ESTATION2_INST_LOG_FILE
    exit -1
fi

#   Set the 'fixed' static IP method in /etc/NetworkManager
cp /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.bak
perl -p -i -e "s#managed=false#managed=false#" /etc/NetworkManager/NetworkManager.conf

#   Modify the interfaces file
cp /etc/network/interfaces /etc/network/interfaces.bak
echo " "                                                >> /etc/network/interfaces
echo "auto eth0 "                                       >> /etc/network/interfaces
echo "iface eth0 inet static "                          >> /etc/network/interfaces
if [ $1 == 'PC2' ]; then
    echo "      address     $PC2_IPV4_ADDRESS"          >> /etc/network/interfaces
elif [ $1 == 'PC3' ]; then
    echo "      address     $PC2_IPV4_ADDRESS"          >> /etc/network/interfaces
elif
    echo " $0 - Error: argument must be PC2 or PC3. Exit" >> $ESTATION2_INST_LOG_FILE
fi

echo "      address     $NETWORK_ADDRESS"          >> /etc/network/interfaces
echo "      netmask     $NETWORK_SUBMASK"          >> /etc/network/interfaces
echo "      broadcast   $NETWORK_BROADCAST"        >> /etc/network/interfaces
echo "      gateway     $NETWORK_GATEWAY"          >> /etc/network/interfaces


