# coding: utf8
# NE PAS EFFACER
import logging
import logging.handlers

LOG_FILENAME = '/var/log/fts.log'
logger = logging.getLogger('fts')
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, 
    maxBytes=4000000,
    backupCount=5)

formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

from fts import FTS

# Définition des répertoires de travail

## Répertoire de production de tellicast
tellicast_path="/space/tellicast/data/received/default/"
## Répertoire de réception des rpm de tellicast
tellicast_patch_path="/space/tellicast/data/received/default/"
## Répertoire d'entrée du FTP Push
FTP_PUSH_IN_PATH = "/space/efts/fromTellicast/forFtpPush"
## Répertoire de travail de la eStation
estation_path = "/space/efts/fromTellicast/forEstation"
## Répertoire de dépot des patchs
patch_path = "/data/data_patch/temp"


FTS.add_configuration(
    name="Absolute Dynamic Topography - Multimission / AVISO General",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^.*_j.*_adt_v.*.nc.gz$^.*_global_.*_adt_v.*.nc.gz$"
)


FTS.add_configuration(
    name="Absolute Sea Level Anomaly - Jason 2 - Mozambique / AVISO General",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^.*_mozambique_j2.*_sla_v.*.nc.gz$"
)


FTS.add_configuration(
    name="Absolute Sea Level Anomaly - Multimission / AVISO General",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^.*_global_.*_sla_v.*.nc.gz$"
)


FTS.add_configuration(
    name="Absolute Sea Level Anomaly - SARAL - Mozambique / AVISO General",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^.*_mozambique_al_sla_v.*.nc.gz$"
)


FTS.add_configuration(
    name="Active Fire Monitoring (CAP) - MSG - 0 degree / Meteorological Products - 15min",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^L-000-MSG.__-MPEF________-FIRC[_].*$"
)


FTS.add_configuration(
    name="All Sky Radiances - MSG - 0 degree / Meteorological Products - 1 to 3 hourly",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^L-000-MSG.__-MPEF________-ASR[_].*$"
)


FTS.add_configuration(
    name="ASCAT regional ocean surface winds at 12.5 km node grid - Metop / EARS-ASCAT",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^ascat.*_ear_.*125.*$"
)


FTS.add_configuration(
    name="ASCAT regional ocean surface winds at 25 km node grid - Metop / EARS-ASCAT",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^ascat.*_ear_.*250.*$"
)


FTS.add_configuration(
    name="ASCAT soil moisture at 12.5 km swath grid - Metop / EUMETSAT MetopA ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPA.ASCAT_C_EUM._.*_eps_o_125_ssm_l2.bin$"
)


FTS.add_configuration(
    name="ASCAT soil moisture at 12.5 km swath grid - Metop / EUMETSAT MetopB ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPB.ASCAT_C_EUM._.*_eps_o_125_ssm_l2.bin$"
)


FTS.add_configuration(
    name="ASCAT soil moisture at 25 km swath grid - Metop / EUMETSAT MetopA ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPA.ASCAT_C_EUM._.*_eps_o_250_ssm_l2.bin$"
)


FTS.add_configuration(
    name="ASCAT soil moisture at 25 km swath grid - Metop / EUMETSAT MetopB ASCAT Surface Soil Moisture",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPB.ASCAT_C_EUM._.*_eps_o_250_ssm_l2.bin$"
)


FTS.add_configuration(
    name="Atlantic High Latitude Downward Longwave Irradiance - Multimission / OSI SAF Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-OSI_-NOR_-MULT-AHLDLI_.*$"
)


FTS.add_configuration(
    name="Atlantic High Latitude Sea Surface Temperature - Multimission / OSI SAF Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-OSI_-NOR_-MULT-AHLSST_.*$"
)


FTS.add_configuration(
    name="Atlantic High Latitude Surface Shortwave Irradiance - Multimission / OSI SAF Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-OSI_-NOR_-MULT-AHLSSI_.*$"
)


FTS.add_configuration(
    name="Atmospheric Motion Vectors - MSG - 0 degree / Meteorological Products - 1 to 3 hourly",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^L-000-MSG.__-MPEF________-AMV[_].*$"
)


FTS.add_configuration(
    name="ATOVS Sounding Products - Metop / MetopA ATOVS Sounding Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPA.ATOVS_C_EUM._.*_eps_o_l2.bin$"
)


FTS.add_configuration(
    name="MetopB ATOVS Sounding Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*METOPB.ATOVS_C_EUM._.*_eps_o_l2.bin$"
)


FTS.add_configuration(
    name="Clear Sky Radiances - MFG - Indian Ocean / Meteosat Meteorological Products - IODC",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*MET07.CSR_C_EUMS_.*.bin$"
)


FTS.add_configuration(
    name="Clear Sky Water Vapour Winds - MFG - Indian Ocean / Meteosat Meteorological Products - IODC",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*MET07.WVW_C_EUMS_.*.bin$"
)


FTS.add_configuration(
    name="Cloud Analysis (BUFR) - MFG - Indian Ocean / Meteosat Meteorological Products - IODC",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*MET07.CLA_C_EUMS_.*.bin$"
)


FTS.add_configuration(
    name="Cloud Mask - MFG - Indian Ocean / Meteosat Meteorological Products - IODC",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^W_XX-EUM.*MET07.CLM_C_EUMS_.*.bin$"
)


FTS.add_configuration(
    name="Colour Composite CCD-HRC - CBERS - Africa, South America / INPE Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^INPE_CBERS_2B_CHC_.*_.*_.*_.*_.*_.*.tif.gz$"
)


FTS.add_configuration(
    name="Composites - GOES-MSG - Africa, South America / INPE Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^INPE_GMC_.*.jpg$"
)


FTS.add_configuration(
    name="Composite Ocean Products - Multimission - AMESD Regions / EAMNet/AMESD - Refined and Composite Marine Products",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^PML_.*_MODIS_.*_.daycomp_.*.nc.bz2$"
)


FTS.add_configuration(
    name="Corrected Sea Surface Height - Multimission / Included for the AVISO general &apos",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="Delayed Products&apos"
)


FTS.add_configuration(
    name="Downwelling Surface LW Fluxes - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_DSLF_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Downwelling Surface SW Fluxes - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_DSSF_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Dry Matter Productivity (DMP) - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_DMP_.*_AFRI_PROBAV_V.*.zip$"
)


FTS.add_configuration(
    name="Evapotranspiration - MSG - 0 degree / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_ET_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Fractional Vegetation Cover - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FVC_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Fire Detection and Monitoring - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FDeM.*_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Fraction of Absorbed Photosynthetic Active Radiation - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FAPAR_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Land Surface Temperature - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_LST_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Leaf Area Index - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_LAI_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Snow Cover - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_SC2_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Surface Albedo - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_AL.*_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Fire Radiative Power Pixel - MSG / Land SAF Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S-LSA_-HDF5_LSASAF_MSG_FRP-PIXEL.*_.Afr_.*.bz2$"
)


FTS.add_configuration(
    name="Rainfall Estimate for Africa - MSG / TAMSAT Rainfall Estimates",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^rfe[0-9]{4}_[0-9]{2}-dk.*$"
)


FTS.add_configuration(
    name="Vegetation Productivity Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_VPI_.*_AFRI_PROBAV_V.*.zip$"
)


FTS.add_configuration(
    name="Vegetation Condition Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_VCI_.*_AFRI_PROBAV_V.*.zip$"
)


FTS.add_configuration(
    name="Normalised Difference Vegetation Index (NDVI) - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_NDVI_.*_AFRI_PROBAV_V.*.zip$"
)


FTS.add_configuration(
    name="Leaf Area Index - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_LAI_.*_AFRI_PROBAV_V.*.zip$"
)


FTS.add_configuration(
    name="Fraction of green vegetation cover - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_FCOVER_.*_AFRI_PROBAV_V.*.zip$"
)


FTS.add_configuration(
    name="Fraction of Absorbed Photosynthetically Active Radiation - PROBA-V - Africa / VITO - Copernicus Global Land - Africa",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^g2_BIOPAR_FAPAR_.*_AFRI_PROBAV_V.*.zip$"
)


FTS.add_configuration(
    name="Multi-sensor Precipitation Estimate - MSG - 0 degree / Meteorological Products - 15min",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^L-000-MSG.__-MPEF________-MPEG.*$"
)

FTS.add_configuration(
    name="Copie des patchs de tellicast vers le serveur de mise à jour",
    input_directory=tellicast_patch_path,
    output_directories=[patch_path],
    include_filter="^mesa2015-.*\.rpm$",
    exclude_filter="^IGNORE.*$"
)

# export vers le FTP du sentinel 3
FTS.add_configuration(
    name="Export du sentinel 3",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^S3A_(OL|SL|SR)_2_.*.SEN3.tar$",
    exclude_filter="^IGNORE.*$"
)

# ajout demandé par le JRC pour MESA 1.2
FTS.add_configuration(
    name="Near real time NDVI 2.2 from VITO",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^c_gls_NDVI_.*_AFRI_PROBAV_V.*.zip$"    
)


# ajout demandé par le JRC pour MESA 1.3
FTS.add_configuration(
    name="MODIS Global Chla 4km",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^A.*.L3m_DAY_CHL_chlor_a_4km.nc$"    
)
# ajout demandé par le JRC pour MESA 1.3
FTS.add_configuration(
    name="MODIS Global SST 4km",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^A.*.L3m_DAY_SST_sst_4km.nc$"    
)
# ajout demandé par le JRC pour MESA 1.3
FTS.add_configuration(
    name="MODIS Global PAR 4km",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^A.*.L3m_DAY_PAR_par_4km.nc$"    
)
# ajout demandé par le JRC pour MESA 1.3
FTS.add_configuration(
    name="MODIS Global Kd490 4km",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^A.*.L3m_DAY_KD490_Kd_490_4km.nc$"    
)

FTS.add_configuration(
    name="Products generated by BDMS/CSC  in the framework of AMESD/MESA projects - Southern Africa ",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^(AMESD|MESA)_SADC.*$"
)
 
FTS.add_configuration(
    name="Products generated by JRC in the framework of MESA projects ",
    input_directory=tellicast_path,
    output_directories=[estation_path],
    include_filter="^MESA_JRC_.*$"
)

#ajout pour produit ECOWAS
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
