#!/bin/bash
############################################################################
# Functions
############################################################################
function Geoportal_Start()
{
        python /var/www/eStation2/apps/es2system/GeoPortal/service_geoportal.py start
}
#---------------------------------------------------------------------------
function Geoportal_Stop()
{
        python /var/www/eStation2/apps/es2system/GeoPortal/service_geoportal.py stop
}
#---------------------------------------------------------------------------
function Geoportal_Status()
{
        python /var/www/eStation2/apps/es2system/GeoPortal/service_geoportal.py status
}

#---------------------------------------------------------------------------

############################################################################
# Main
############################################################################

case "$1" in
    start)
        Geoportal_Start
        ;;

    stop)
        Geoportal_Stop
       ;;

    restart)
        Geoportal_Stop
        Geoportal_Start
        ;;

    status)
        Geoportal_Status
        ;;

    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac


