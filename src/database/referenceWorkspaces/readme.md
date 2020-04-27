
# To update the jrc_ref_workspaces follow the steps below:

- On mesa-proc login the GUI as jrc_ref (pwd: mesadmin) and create new workspaces.

- Select the workspaces you want to export under MY WORKSPACES and export them.

- Rename the exported json file to jrc_ref_workspaces.json and copy this file to /src/database/referenceWorkspaces/ 
You can first rename the existing jrc_ref_workspaces.json to jrc_ref_workspaces<version>.json 
where <version> is the version you find in the file jrc_ref_settings.ini in the same directory.
    
- Set the value of 'update' to true in the file jrc_ref_settings.ini (e.g. update = true)

- In /build-centos/eStation2-Apps-upgrade.spec increment the version value in the line:

    (look at the value to increment to in the file jrc_ref_settings.ini)
    ````
    su adminuser -c "/usr/local/src/tas/anaconda/bin/python -c 'import webpy_esapp_helpers; webpy_esapp_helpers.importJRCRefWorkspaces(version=1)'"
    ```` 
    
- In the docker environment open the file /build-docker/web/docker-entrypoint.sh and increment the version value in the line:
    ````
    python -c 'import webpy_esapp_helpers; webpy_esapp_helpers.importJRCRefWorkspaces(version=1)'
    ````
