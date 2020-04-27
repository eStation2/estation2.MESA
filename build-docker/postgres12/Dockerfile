FROM kartoza/postgis:12.0
# FROM d-registry.jrc.it:5000/public/postgis:12.0
ADD ./build-docker/postgres12/pg_hba.conf /etc/postgresql/12/main/
RUN chown postgres:postgres /etc/postgresql/12/main/pg_hba.conf
RUN chown postgres.postgres /var/log/postgresql

#RUN apt-get update && apt-get install -y nano

RUN mkdir /home/postgres/
RUN mkdir /var/log/eStation2/
RUN mkdir -p /var/www/eStation2/

#USER postgres
# RUN export PGPASSWORD='mesadmin'; -> Done in docker-compose file.
ADD ./build-docker/postgres12/.pgpass /home/postgres/
RUN chmod 0775 -R /home/postgres/
RUN chown postgres:postgres -R /home/postgres/

#USER root
#ADD ./src/database/dbInstall/products_dump_structure_only.sql /var/tmp/
#ADD ./src/database/dbInstall/update_db_structure.sql /var/tmp/
#ADD ./src/database/dbInstall/update_insert_jrc_data.sql /var/tmp/
#ADD ./src/database/dbInstall/create_table_db_version.sql /var/tmp/

#ADD ./build-docker/postgres12/estation2-docker-entrypoint.sh /root/estation2-docker-entrypoint.sh
#RUN chmod 0775 /root/estation2-docker-entrypoint.sh

ADD ./build-docker/postgres12/setup_estationdb.sh /root/setup_estationdb.sh
RUN chmod 0775 /root/setup_estationdb.sh

# ENTRYPOINT presumes the container runs as an executable and runs the command before the container starts!
# The postgres container restarts continiously!
#ENTRYPOINT ["/root/estation2-docker-entrypoint.sh"]