#!/usr/bin/python

from docker import Client
from lib.python import es_logging as log

logger = log.my_logger(__name__)


def install_update_db():
    c = Client(base_url='unix://var/run/docker.sock')
    command = ["/root/setup_estationdb.sh"]
    commandid = c.exec_create('postgres', command)
    status = c.exec_start(commandid)
    logger.info("install_update_db:\n %s" % status)
