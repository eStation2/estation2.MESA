#
#   Notes on Geoserver implementation for eStation 2.0 products
#

NOTE: you should be able to access the remote machine (hosting geoserver) w/o psw request. Generate an ssh-key as described in
      https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2

-------------------
 Implementation
-------------------

The following python modules are used for the implementation:

1. geoserverREST.py:    defines the API functions (mainly based on curl)
2. test_geoserver.py:   defined the test cases for APIs and esTools (unittest)
3. eStationTools.py:    translation dictionaries and other methods
4. system_geoserver.py: 'service' loop for a. Sync the datasets, b. Updating Geoserver.

NOTE: in my implementation all files are in /var/www/eStation2/apps/es2system/GeoPortal/

-------------------
 Workspaces
-------------------

1. A WS is created, with a naming convention defined in esTools.setWorkspaceName()

2. By default, we use the option nametype=serviceproductsubproduct and the workspace name is like:

    rainfall_fewsnet-rfe_10davg

    NOTE: version like 2.0 is not accepted in workspace naming. The version name is converted (e.g. 2.0 -> 2_0)
          We use, FTTB, the 'Category' of eStation2.0 (vegetation, rainfall, fire, ...) as 'Service'

-------------------
 Coverage Store
-------------------

1. The coverage (store) is named like the product, and contains the date, like:

    '20150201_fewsnet-rfe_1moncum_FEWSNET-Africa-8km_2_0'

-------------------
 Raster
-------------------

1. A raster correspond to a specific 'date'
2. Name of the Raster contains the following elements:

    'category'_'product'_'date'_'region'_'version'.tif , e.g. (for SADC)

    AMESD_SADC_LtavgRFE___20151021_SAfri_v2.tif



-------------------
 SLD (color palette)
-------------------

1. An .sld file is created from the legend_steps table, having:

    filename = <product>_<version>_<subproduct>.sld
    <NamedLayer Name="vgt-ndvi">    -> i.e. <product>
    <UserStyle Title="NDVI">        -> i.e. Legend Name

  It is then uploaded to geoserver as Style, and assigned as default Style for the Layer


--------------------------------------
  syncGeoserver() flow
--------------------------------------

FOREACH product

    IF NOT isWorkspace() -> createWorkspace()

    FOREACH file

        uploadAndRegisterRaster():  IF NOT isStyle() ->  createStyle()
                                    IF NOT isRaster() ->
                                        IF NOT existsRemote() -> uploadRemote()
                                        registerRaster()

Methods used by each routine:

isWorkspace()       -> requests.get()
createWorkspace()   -> curl -s -u ...
isStyle()           -> requests.get()
createStyle()       -> requests.put()
isRaster()          -> requests.get()
registerRaster()    -> requests.put()
setDefaultStyle()   -> requests.put()      NOT USED ??

existRemote()       -> ssh test -f
uploadRemote()      -> scp