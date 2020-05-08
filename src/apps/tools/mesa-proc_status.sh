#!/bin/bash

SEND_EMAIL=False
MESA_STATUS_ALERT_FILE=/home/adminuser/scripts/mesa_status.txt
THRESHOLD=95
MESA_PSWD=
SUBJECT='MESA-PROC_STATUS_ALERT'
MESA_STATUS_ALERT_FILE=/home/adminuser/scripts/mesa_status.txt
EMAIL_IDS=vijaycharan.irs@gmail.com,Vijay.VENKATACHALAM@ext.ec.europa.eu,clerici.marco@gmail.com,jurvtk@gmail.com
#EMAIL_IDS=vijaycharan.irs@gmail.com,Vijay.VENKATACHALAM@ext.ec.europa.eu.


echo 'Dear all, ' > $MESA_STATUS_ALERT_FILE

STATUS_EUM=$(python /var/www/eStation2/apps/acquisition/service_get_eumetcast.py status | awk '{print $6}')
if [ "$STATUS_EUM" == "False" ]; then
  echo 'Mesa-Proc service status --> get_eumetcast stopped' >> $MESA_STATUS_ALERT_FILE
  SEND_EMAIL=True
fi

STATUS_INTERNET=$(python /var/www/eStation2/apps/acquisition/service_get_internet.py status | awk '{print $6}')
if [ "$STATUS_INTERNET" == "False" ]; then
  echo 'Mesa-Proc service status --> get_internet stopped' >> $MESA_STATUS_ALERT_FILE
  SEND_EMAIL=True
fi

STATUS_INGESTION=$(python /var/www/eStation2/apps/acquisition/service_ingestion.py status | awk '{print $6}')
if [ "$STATUS_INGESTION" == "False" ]; then
  echo 'Mesa-Proc service status --> Ingestion stopped' >> $MESA_STATUS_ALERT_FILE
  SEND_EMAIL=True
fi

STATUS_PROCESSING=$(python /var/www/eStation2/apps/processing/service_processing.py status | awk '{print $6}')
if [ "$STATUS_PROCESSING" == "False" ]; then
  echo 'Mesa-Proc service status --> Processing stopped' >> $MESA_STATUS_ALERT_FILE
  SEND_EMAIL=True
fi

STATUS_DATA_SPACE=$(df /data-space | grep / | awk '{ print $5}' | sed 's/%//g')
if [ "${STATUS_DATA_SPACE}" -gt "${THRESHOLD}" ]; then
  echo "Mesa-Proc Disk status --> data-space disk is ${STATUS_DATA_SPACE} % full" >> $MESA_STATUS_ALERT_FILE
  SEND_EMAIL=True
fi

STATUS_SPATIAL_DATA=$(df /spatial_data | grep / | awk '{ print $4}' | sed 's/%//g')
if [ "${STATUS_SPATIAL_DATA}" -gt "${THRESHOLD}" ]; then
  echo "Mesa-Proc Disk status --> spatial_data disk is ${STATUS_SPATIAL_DATA} % full" >> $MESA_STATUS_ALERT_FILE
  SEND_EMAIL=True
fi

if [ "${SEND_EMAIL}" == "True" ]; then
  echo "$MESA_PSWD" | sudo -S mail -v -s 'MESA-PROC STATUS ALERT' ${EMAIL_IDS} < '/home/adminuser/scripts/mesa_status.txt'
  #echo "rootroot" | sudo -S mail -v -s 'MESA-PROC STATUS ALERT' vijaycharan.irs@gmail.com,Vijay.VENKATACHALAM@ext.ec.europa.eu < '/home/adminuser/scripts/mesa_status.txt'
  #echo "mesadmin" | sudo -S mail -v -s "Disk spatial_data is almost full" vijaycharan.irs@gmail.com < '/home/adminuser/scripts/mesa_proc_alert.txt'
fi