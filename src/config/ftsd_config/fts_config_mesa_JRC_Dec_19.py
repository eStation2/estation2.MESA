# coding: utf8
#NE PAS EFFACER
import logging
import logging.handlers

LOG_FILENAME = '/var/log/fts.log'
logger = logging.getLogger('fts')

handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
    maxBytes=4000000, 
	backupCount=5)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


from fts import FTS

## Répertoire de production de tellicast
tellicast_path="/space/tellicast/data/received/default"
## Répertoire de dépot des patchs
patch_path = "/data/data_patch/temp"
## Répertoire d'entrée du FTP Push
FTP_PUSH_IN_PATH = "/space/efts/fromTellicast/forFtpPush"


FTS.add_configuration(
    name="Absolute Dynamic Topography - Multimission / AVISO General",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^.*_j.*_adt_v.*.nc.gz$^.*_global_.*_adt_v.*.nc.gz$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Absolute Sea Level Anomaly - Jason 2 - Mozambique / AVISO General",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^.*_mozambique_j2.*_sla_v.*.nc.gz$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Absolute Sea Level Anomaly - Multimission / AVISO General",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^.*_global_.*_sla_v.*.nc.gz$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Absolute Sea Level Anomaly - SARAL - Mozambique / AVISO General",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^.*_mozambique_al_sla_v.*.nc.gz$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Active Fire Monitoring (CAP) - MSG - 0 degree / Meteorological Products - 15min",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^L-000-MSG.__-MPEF________-FIRC[_].*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Atmospheric Motion Vectors - MSG - 0 degree / Meteorological Products - 1 to 3 hourly",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^L-000-MSG.__-MPEF________-AMV[_].*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Composite Ocean Products - Multimission - AMESD Regions / EAMNet/AMESD - Refined and Composite Marine Products",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^PML_.*_MODIS_.*_.daycomp_.*.nc.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Corrected Sea Surface Height - Multimission / Included for the AVISO general &apos",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="Delayed Products&apos",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Dry Matter Productivity (DMP) - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^g2_BIOPAR_DMP_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Evapotranspiration - MSG - 0 degree / Land SAF Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_ET_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Land Surface Temperature - MSG / Land SAF Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_LST_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fire Radiative Power Pixel - MSG / Land SAF Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FRP-PIXEL.*_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Rainfall Estimate for Africa - MSG / TAMSAT Rainfall Estimates",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^rfe[0-9]{4}_[0-9]{2}-dk.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Vegetation Productivity Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^g2_BIOPAR_VPI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Vegetation Condition Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^g2_BIOPAR_VCI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Normalised Difference Vegetation Index (NDVI) - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^g2_BIOPAR_NDVI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Leaf Area Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^g2_BIOPAR_LAI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fraction of green vegetation cover - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^g2_BIOPAR_FCOVER_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fraction of Absorbed Photosynthetically Active Radiation - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^g2_BIOPAR_FAPAR_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Multi-sensor Precipitation Estimate - MSG - 0 degree / Meteorological Products - 15min",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^L-000-MSG.__-MPEF________-MPEG.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Copie des patchs de tellicast vers le serveur de mise à jour",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/data/data_patch/temp'],
    include_filter="^mesa2015-.*\.rpm$",
    exclude_filter="^IGNORE.*$"
)

FTS.add_configuration(
    name="Export du sentinel 3",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^S3(A|B)_(OL|SL|SR)_2_.*.SEN3.tar$",
    exclude_filter="^IGNORE.*$"
)

FTS.add_configuration(
    name="Near real time NDVI 2.2 from VITO",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^c_gls_NDVI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Near real time FAPAR 2.2 from VITO",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^c_gls_FAPAR.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Near real time LAI 2.2 from VITO",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^c_gls_LAI.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Near real time FCOVER 2.2 from VITO",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^c_gls_FCOVER.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global Chla 4km",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^A.*.L3m_DAY_CHL_chlor_a_4km.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global SST 4km",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^AQUA_MODIS.*.L3m.DAY.SST.sst.4km.*.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global PAR 4km",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^A.*.L3m_DAY_PAR_par_4km.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global Kd490 4km",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^A.*.L3m_DAY_KD490_Kd_490_4km.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Products generated by BDMS/CSC  in the framework of AMESD/MESA projects - Southern Africa ",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^(AMESD|MESA)_SADC.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Products generated by JRC in the framework of MESA projects ",
    input_directory="/space/tellicast/data/received/default",
    output_directories=['/space/efts/fromTellicast/forEstation'],
    include_filter="^MESA_JRC_.*$",
    exclude_filter="^$"
)
