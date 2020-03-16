# eStation2 Python 3.6 in Docker 
## Introduction

This installation contains the eStation2 code (from the main branch) converted to Python 3.6 or higher
For the database PostgreSQL 12 is used, for which the code had to be adapted to the latest version of SQLAlchemy.
The idea is to refactor the code in such a way that its compatible for both Python 2 as Python 3, using the "future" package.
The code works in Python 3.6 but not yet in Python 2.7, because string handling has been converted to Python 3, 
which is not compatible with Python 2.

Docker compose is used to create/build three images and run the three services (containers).

The three services (containers) are:
* mapserver
* postgres
* web

There are two docker-compose.yml files, one for setting up a Python 3 environment and one for Python2.
For each version a relative Dockerfile exists for the web service, where Python resides.
You can ignore the Python 2 setup, which is used by the developers for testing.

## Installation

1. Clone the python3_docker branch on your local machine.

    You should have [Git](https://git-scm.com/downloads) installed. 
    
    After you installed Git on your computer, open a CMD or Powershell (Windows) or a Terminal (MAC) and run the following command.
    First CD to the directory where you want to create the clone.
    ```bash
    cd /Users/Jurvtk/Develop/
   
    git clone --branch pyhton3_docker https://github.com/eStation2/estation2.MESA.git eStation2_pyhton3_docker
    ```

2. Download and install [Docker desktop](https://www.docker.com/products/docker-desktop)

3. Create the external docker volume for PostgreSQL 12

   Currently, the volume for PostgreSQL has to be created externally by running the following command:
    ```bash
    docker volume create --name docker-postgresql12-volume -d local
    ```
   In the future this volume will be created automatically, probably using swarm mode.
   
4. Setup environment variables for the web service volumes.
   
    The web service uses two external volumes, one for the data and one for the eStation2 static layers and settings.
    In the .env file used by docker-compose, there are two settings which you have to change to the place where you have the data and eStation2 directories.
    For example in Windows:
    
    * DATA_VOLUME=C:\data
    
    * ESTATION2_VOLUME=C:\data\eStation2

    The "data" directory should contain the following directories:
    + processing
    + ingest
    + ingest.wrong
    
    The "eStation2" directory should contain the following, also empty, directories:
    + completeness_bars
    + db_dump
    + docs   
    + get_lists
    + layers
    + log
    + logos
    + requests
    + settings
    
    You can download the docs, layers and logos from the JRC SFTP server [here](ftp://narmauser:JRCkOq7478@srv-ies-ftp.jrc.it/narma/eStation_2.0/static_data).
    - host: srv-ies-ftp.jrc.it
    - username: narma
    - pwd: JRCkOq7478
    - directory: /narma/eStation_2.0/static_data
    
    Unzip the corresponding files in their respective directory.   
   
5. Run docker-compose to build and start the eStation2 application.

   Open a CMD or Powershell (Windows) or a Terminal (MAC) and run the following command. 
   First CD to the directory where you created the clone. You must have an internet connection!
   ```bash
    cd /Users/Jurvtk/Develop/eStation2_pyhton3_docker
   
    docker-compose -f "docker-compose_python3.yml" up -d --build
   ```
   This will take some minutes to build the three images and run the three services (containers). 
   In the end you will see a result like this:
   
   ```bash  
    ...
    Successfully built 52ba36b03b87
    Successfully tagged estation2python3docker/web:1.0
    ...
    Successfully built ca1d8d095631
    Successfully tagged estation2python3docker/mapserver:1.0
    ...
    Successfully built 47f027edf7e9
    Successfully tagged estation2python3docker/postgis:9.6
    Creating mapserver ... done
    Creating web       ... done
    Creating postgres  ... done
   ```

6. Create and fill the database

    Running the postgres service will automatically create the estationdb database and estation user, if they not already exist.
    The structure and the data of the database on the other hand, are not (yet) automatically created.
    
    To do so, you will have to enter the postgres service and run three sql scripts as follows:
    
    ```bash  
    docker exec -it postgres /bin/sh -c "[ -e /bin/bash ] && /bin/bash || /bin/sh"
   
    root@5a1d118827bd:/# psql -h postgres -U estation -d estationdb -w -f /var/tmp/products_dump_structure_only.sql >/var/log/eStation2/products_dump_structure_only.log 2>/var/log/eStation2/products_dump_structure_only.err
    root@5a1d118827bd:/# password: mesadmin
    root@5a1d118827bd:/# psql -h postgres -U estation -d estationdb -w -f /var/tmp/update_db_structure.sql >/var/log/eStation2/update_db_structure.log 2>/var/log/eStation2/update_db_structure.err
    root@5a1d118827bd:/# password: mesadmin
    root@5a1d118827bd:/# psql -h postgres -U estation -d estationdb -w -f /var/tmp/update_insert_jrc_data.sql >/var/log/eStation2/update_insert_jrc_data.log 2>/var/log/eStation2/update_insert_jrc_data.err
    root@5a1d118827bd:/# password: mesadmin
    ```
    
    You have to do this only ones!
    
7. Open a browser and go to [localhost](http://localhost/)

