#!/bin/bash
status=0
my_filename='message.txt'
MOUNTPOINTS="/spatial_data /data-space"
THRESHOLD=80
subject='Anomaly detect '

STATUS_EUM=$(python /var/www/eStation2/apps/acquisition/service_get_eumetcast.py status | awk '{print $6}')
if [ "$STATUS_EUM" == "False" ]; then
  #echo  "Current status of the get_eumetcast Service: False" | mail -s 'Current status of the get_eumetcast Service: False' JRC-ESTATION@ec.europa.eu
  echo 'Current status of the get_eumetcast Service: False'
fi

STATUS_INTERNET=$(python /var/www/eStation2/apps/acquisition/service_get_internet.py status | awk '{print $6}')
if [ "$STATUS_INTERNET" == "False" ]; then
  #echo  "Current status of the get_internet Service: False" | mail -s 'Current status of the get_internet Service: False' JRC-ESTATION@ec.europa.eu
  echo 'Current status of the get_internet Service: False'
fi

STATUS_INGESTION=$(python /var/www/eStation2/apps/acquisition/service_ingestion.py status | awk '{print $6}')
if [ "$STATUS_INGESTION" == "False" ]; then
  #echo  "Current status of the Ingestion Service: False" | mail -s 'Current status of the Ingestion Service: False' JRC-ESTATION@ec.europa.eu
  echo 'Current status of the Ingestion Service: False'
fi

STATUS_PROCESSING=$(python /var/www/eStation2/apps/processing/service_processing.py status | awk '{print $6}')
if [ "$STATUS_PROCESSING" == "False" ]; then
  #echo  "Current status of the Processing Service: False" | mail -s 'Current status of the Processing Service: False' JRC-ESTATION@ec.europa.eu
  echo 'Current status of the Processing Service: False'
fi

STATUS_DATA_SPACE=$(df /data-space | grep / | awk '{ print $5}' | sed 's/%//g')
if [ "${STATUS_DATA_SPACE}" -gt "${THRESHOLD}" ]; then
  #echo  "Disk full" | mail -s 'Disk /data-space/ is almost full' JRC-ESTATION@ec.europa.eu
  echo 'Disk full'
fi

STATUS_SPATIAL_DATA=$(df /spatial_data | grep / | awk '{ print $4}' | sed 's/%//g')
if [ "${STATUS_SPATIAL_DATA}" -gt "${THRESHOLD}" ]; then
  echo "Disk full" | mail -s 'Disk /spatial_data is almost full' vijaycharan.irs@gmail.com
  echo 'Disk full'
fi