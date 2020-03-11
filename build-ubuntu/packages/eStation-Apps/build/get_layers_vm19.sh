#!/bin/bash
# Copy Layers from dev machine (they are not under git)
scp -r /srv/www/eStation2_Layers/*  esuser@h05-dev-vm26:/home/esuser/eStation2/eStation2_Layers/
