FROM kartoza/postgis:12.0
# FROM d-registry.jrc.it:5000/public/postgis:12.0
ADD pg_hba.conf /etc/postgresql/12/main/
RUN chown postgres:postgres /etc/postgresql/12/main/pg_hba.conf
RUN chown postgres.postgres /var/log/postgresql

# ADD .pgpass /home/root/
ADD products_dump_structure_only.sql /var/tmp/
ADD update_db_structure.sql /var/tmp/
ADD update_insert_jrc_data.sql /var/tmp/
#ADD docker-entrypoint.sh /docker-entrypoint.sh
#ADD setup_estationdb.sh /setup_estationdb.sh


RUN mkdir /var/log/eStation2/
# RUN export PGPASSWORD='mesadmin';
# RUN chmod 0600 /home/root/.pgpass
# RUN psql -h postgres -U estation -d estationdb -f /var/tmp/products_dump_structure_only.sql >/var/log/postgresql/products_dump_structure_only.log 2>/var/log/postgresql/products_dump_structure_only.err
# RUN psql -h postgres -U estation -d estationdb -f /var/tmp/update_db_structure.sql >/var/log/postgresql/update_db_structure.log 2>/var/log/postgresql/update_db_structure.err
# RUN psql -h postgres -U estation -d estationdb -f /var/tmp/update_insert_jrc_data.sql >/var/log/postgresql/update_insert_jrc_data.log 2>/var/log/postgresql/update_insert_jrc_data.err


# RUN chmod 0600 /home/root/.pgpass
# RUN chmod +x /docker-entrypoint.sh
# RUN ln -s /usr/local/bin/docker-entrypoint.sh /

# USER postgres

# ENTRYPOINT ./docker-entrypoint.sh
# ENTRYPOINT ["docker_entrypoint.sh"]

# CMD ["postgres"]