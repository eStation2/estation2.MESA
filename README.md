# eStation2 Python 2.7 in Docker

This installation contains the eStation2 code of the main branch (in Python 2.7 with PostgreSQL 9.6) and is "dockerized".
Docker compose is used to create/build three images and run the three services (containers).

The three services (containers) are:
* mapserver
* postgres
* web

## Installation

1. Clone the main_docker branch on your local machine.

    You should have [Git](https://git-scm.com/downloads) installed. 
    
    After you installed Git on your computer, 
    open a CMD or Powershell (Windows) or a Terminal (MAC) and run the following command.
    First CD to the directory where you want to create the clone.
    ```bash
    cd /Users/Jurvtk/Develop/
   
    git clone --branch main_docker https://github.com/eStation2/estation2.MESA.git eStation2_main_docker
    ```

2. Download and install [Docker desktop](https://www.docker.com/products/docker-desktop)

3. Create the external docker volume for PostgreSQL 9.6

   Currently, the volume for PostgreSQL has to be created externally by running the following command:
    ```bash
    docker volume create --name docker-postgresql96-volume -d local
    ```
   In the future this volume will be created automatically, probably using swarm mode.
   
4. Run docker-compose to build and start the eStation2 application.

   Open a CMD or Powershell (Windows) or a Terminal (MAC) and run the following command. 
   First CD to the directory where you created the clone. You must have an internet connection!
   ```bash
    cd /Users/Jurvtk/Develop/eStation2_main_docker
   
    docker-compose -f "docker-compose.yml" up -d --build
   ```
   This will take some minutes to build the three images and run the three services (containers). In the end you will see a result like this:
   ```bash  
    ...
    Successfully built 52ba36b03b87
    Successfully tagged estation2_main_docker/web:1.0
    ...
    Successfully built ca1d8d095631
    Successfully tagged estation2_main_docker/mapserver:1.0
    ...
    Successfully built 47f027edf7e9
    Successfully tagged estation2_main_docker/postgis:9.6
    Creating mapserver ... done
    Creating web       ... done
    Creating postgres  ... done
   ```

5. Create and fill the database

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
    
6. Open a browser and go to [localhost](http://localhost/)

