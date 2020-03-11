#
#   Instructions to manage the files downloaded (manually) from GDrive and having them ingested on eStation 2.0
#

--------------------------------------------------------
# There are three main actions/topics to deal with:
--------------------------------------------------------

1. Renaming: the incoming files have different naming - according to their generation in GEE. The 'standard' naming is:

    JRC-WBD_YYYYMM01_0000065536-0000131072.tif

2. BigTiff: the files are originally in BigTiff format, which cannot be managed on mesa-proc (limitation of GDAL compiling)

3. Mosaicing and mapset: mosaicing is trivial (gdal_merge.py), while no re-projection can be done (memory error).
   The approach is to use only the GDAL command-line tools, and append at the end 'metadata'

--------------------------------------------------------
# Working approach
--------------------------------------------------------

1. On balthazar (B:) we do 1. and 2. - see directory /data/tmp/JRC-WBD-Convert

2. On mesa-proc (MP:), we do the rest, i.e. mosaicing and mapset management (including metadata assignment).

--------------------------------------------------------
# Working PROCEDURE - CAN START from here - see also ES2-96
--------------------------------------------------------

1. MP: Put the original files in a subdirectory of mesa-proc (e.g. /data/processing/wd-gee/1.0/new_files/1WAF_WB/2016)

2. MP: Copy the files to balthazar, by using the command:

    scp * balthazar:/data/tmp/JRC-WBD-Convert/incoming/

3. B: Modify and run the script  /data/tmp/JRC-WBD-Convert/convert.sh to do renaming and BigTiff -> GTiff

4. MP: Copy back the files from balthazar, by using the command:

    scp  balthazar:/data/tmp/JRC-WBD-Convert/outgoing/* /data/processing/wd-gee/1.0/for_ingest

5. MP: Do the files' ingestion, by dropping the files in /data/ingest/

