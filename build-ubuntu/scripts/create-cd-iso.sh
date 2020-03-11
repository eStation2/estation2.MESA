#!/bin/bash
# this script is creating a new iso image in $CD_ISO_IMAGE
# starting from files in $CD_BUILD_DIR

. ./config

mkisofs -r -V "e-Station-2" \
            -cache-inodes -joliet-long\
            -J -l -b isolinux/isolinux.bin \
            -c isolinux/boot.cat -no-emul-boot \
            -boot-load-size 4 -boot-info-table \
            -o $CD_ISO_IMAGE $CD_BUILD_DIR
