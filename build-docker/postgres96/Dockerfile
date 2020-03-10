FROM kartoza/postgis:9.6-2.4
# FROM d-registry.jrc.it:5000/public/postgis:9.6-2.4
ADD pg_hba.conf /etc/postgresql/9.6/main/
RUN chown postgres:postgres /etc/postgresql/9.6/main/pg_hba.conf
RUN chown -R postgres:postgres /var/log/postgresql
RUN chown -R postgres:postgres /var/lib/postgresql 

# ADD .pgpass /home/root/
ADD products_dump_structure_only.sql /var/tmp/
ADD update_db_structure.sql /var/tmp/
ADD online_old_h05estationdru7_data.sql /var/tmp/
ADD update_insert_jrc_data.sql /var/tmp/
# ADD docker-entrypoint.sh /docker-entrypoint.sh
# ADD setup_estationdb.sh /setup_estationdb.sh

RUN mkdir /var/log/eStation2/
# RUN chmod 0600 /home/root/.pgpass
# RUN chmod +x /docker-entrypoint.sh
# RUN ln -s /usr/local/bin/docker-entrypoint.sh /

# USER postgres

# ENTRYPOINT /docker-entrypoint.sh
# ENTRYPOINT ["docker_entrypoint.sh"]

# CMD ["postgres"]