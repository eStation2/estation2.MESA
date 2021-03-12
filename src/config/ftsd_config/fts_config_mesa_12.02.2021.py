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
## Répertoire de travail de la eStation
estation_path = "/space/efts/fromTellicast/forEstation"
## Répertoire d'entrée du FTP Push
FTP_PUSH_IN_PATH = "/space/efts/fromTellicast/forFtpPush"


FTS.add_configuration(
    name="Ocean Colour and SST Products - MODIS AQUA",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^UCT_.*_MODIS_.*.nc.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Absolute Dynamic Topography - Multimission / AVISO General",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^.*_j.*_adt_v.*.nc.gz$^.*_global_.*_adt_v.*.nc.gz$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Absolute Sea Level Anomaly - Jason 2 - Mozambique / AVISO General",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^.*_mozambique_j2.*_sla_v.*.nc.gz$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Absolute Sea Level Anomaly - Multimission / AVISO General",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^.*_global_.*_sla_v.*.nc.gz$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Absolute Sea Level Anomaly - SARAL - Mozambique / AVISO General",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^.*_mozambique_al_sla_v.*.nc.gz$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Active Fire Monitoring (CAP) - MSG - 0 degree / Meteorological Products - 15min",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^L-000-MSG.__-MPEF________-FIRC[_].*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="All Sky Radiances - MSG - 0 degree / Meteorological Products - 1 to 3 hourly",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^L-000-MSG.__-MPEF________-ASR[_].*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ASCAT regional ocean surface winds at 12.5 km node grid - Metop / EARS-ASCAT",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^ascat.*_ear_.*125.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ASCAT regional ocean surface winds at 25 km node grid - Metop / EARS-ASCAT",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^ascat.*_ear_.*250.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ASCAT soil moisture at 12.5 km swath grid - Metop / EUMETSAT MetopA ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPA.ASCAT_C_EUM._.*_eps_o_125_ssm_l2.bin$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ASCAT soil moisture at 12.5 km swath grid - Metop / EUMETSAT MetopB ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPB.ASCAT_C_EUM._.*_eps_o_125_ssm_l2.bin$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ASCAT soil moisture at 12.5 km swath grid - Metop / EUMETSAT MetopC ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPC.ASCAT_C_EUM._.*_eps_o_125_ssm_l2.bin$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ASCAT soil moisture at 25 km swath grid - Metop / EUMETSAT MetopA ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPA.ASCAT_C_EUM._.*_eps_o_250_ssm_l2.bin$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ASCAT soil moisture at 25 km swath grid - Metop / EUMETSAT MetopB ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPB.ASCAT_C_EUM._.*_eps_o_250_ssm_l2.bin$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ASCAT soil moisture at 25 km swath grid - Metop / EUMETSAT MetopC ASCAT Surface soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPC.ASCAT_C_EUM._.*_eps_o_250_ssm_l2.bin$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Atlantic High Latitude Downward Longwave Irradiance - Multimission / OSI SAF Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-OSI_-NOR_-MULT-AHLDLI_.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Atlantic High Latitude Sea Surface Temperature - Multimission / OSI SAF Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-OSI_-NOR_-MULT-AHLSST_.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Atlantic High Latitude Surface Shortwave Irradiance - Multimission / OSI SAF Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-OSI_-NOR_-MULT-AHLSSI_.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Atmospheric Motion Vectors - MSG - 0 degree / Meteorological Products - 1 to 3 hourly",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^L-000-MSG.__-MPEF________-AMV[_].*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="ATOVS Sounding Products - Metop / MetopA ATOVS Sounding Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPA.ATOVS_C_EUM._.*_eps_o_l2.bin$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MetopB ATOVS Sounding Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPB.ATOVS_C_EUM._.*_eps_o_l2.bin$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Modified, Composite Ocean Products - Multimission - AMESD Regions / EAMNet/AMESD - NRT, Refined and Composite Marine Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^PML_.*_MODIS_.*_.*_.*.nc.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Corrected Sea Surface Height - Multimission / Included for the AVISO general &apos",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="Delayed Products&apos",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Downwelling Surface LW Fluxes - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_DSLF_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Downwelling Surface SW Fluxes - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_DSSF_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Dry Matter Productivity (DMP) - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_DMP_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Evapotranspiration - MSG - 0 degree / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_ET_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fractional Vegetation Cover - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FVC_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fire Detection and Monitoring - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FDeM.*_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fraction of Absorbed Photosynthetic Active Radiation - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FAPAR_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Land Surface Temperature - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_LST_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Leaf Area Index - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_LAI_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Snow Cover - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_SC2_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Surface Albedo - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_AL.*_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fire Radiative Power Pixel - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FRP-PIXEL.*_.Afr_.*.bz2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Rainfall Estimate for Africa - MSG / TAMSAT Rainfall Estimates",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^rfe[0-9]{4}_[0-9]{2}-dk.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Vegetation Productivity Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_VPI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Vegetation Condition Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_VCI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Normalised Difference Vegetation Index (NDVI) - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_NDVI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Leaf Area Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_LAI_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fraction of green vegetation cover - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_FCOVER_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Fraction of Absorbed Photosynthetically Active Radiation - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_FAPAR_.*_AFRI_PROBAV_V.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Multi-sensor Precipitation Estimate - MSG - 0 degree / Meteorological Products - 15min",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^L-000-MSG.__-MPEF________-MPEG.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Copie des patchs de tellicast vers le serveur de mise à jour",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^mesa2015-.*\.rpm$",
    exclude_filter="^IGNORE.*$"
)

FTS.add_configuration(
    name="Export du Sentinel 3 MARINE Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S3(A|B)_(OL|SL|SR)_2_(WRR|WST|WAT)_.*.SEN3.tar$",
    exclude_filter="^IGNORE.*$"
)

FTS.add_configuration(
    name="Export du Sentinel 3 Land Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S3(A|B)_(OL|SL|SR|SY)_2_(LFR|LST|LAN|SYN|V10)_.*.SEN3.tar$",
    exclude_filter="^IGNORE.*$"
)

FTS.add_configuration(
    name="Near real time Copernicus Global Land Products from VITO",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^c_gls_.*_AFRI_.*.zip$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global Chla 4km",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^A.*.L3m_DAY_CHL_chlor_a_4km.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global SST 4km",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^A.*.L3m_DAY_SST_sst_4km.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global PAR 4km",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^A.*.L3m_DAY_PAR_par_4km.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global Kd490 4km",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^A.*.L3m_DAY_KD490_Kd_490_4km.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="MODIS Global Chla, SST, PAR, Kd490 4km - Products ",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^AQUA_MODIS.*.L3m.*.nc$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Products generated by JRC in the framework of MESA projects ",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^MESA_JRC_.*$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Significant Wave Height - ECOWAS Marine Thema/ MESA-UG",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^MESA-UG_SWH.*_.*.tif$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Sea Surface Temperature - ECOWAS Marine Thema/ MESA-UG",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^MESA-UG_SST.*_.*.tif$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Sea Surface Currents - ECOWAS Marine Thema/ MESA-UG",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^MESA-UG_SSC.*_.*.tif$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Sea Surface Salinity - ECOWAS Marine Thema/ MESA-UG",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^MESA-UG_SAL.*_.*.tif$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Sea Surface Height - ECOWAS Marine Thema/ MESA-UG",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^MESA-UG_SSH.*_.*.tif$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Potential Fishing Zones- ECOWAS Marine Thema/ MESA-UG",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^MESA-UG_PFZ.*_.*.tif$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Generic 1 FTP Push",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^file1$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Generic 2 FTP Push",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^file2$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Generic 3 FTP Push",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^file3$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Generic 4 FTP Push",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^file4$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Generic 5 FTP Push",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^file5$",
    exclude_filter="^$"
)

FTS.add_configuration(
    name="Precipitation Products - H-SAF",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-HSAF-h0(3|5).*$",
    exclude_filter="^$"
)
