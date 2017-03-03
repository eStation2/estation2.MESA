#!/bin/bash
#
#   Script to manage the MPE .tar archives downloaded from EUMETCast Data Centre
#   Archives should already have been renamed like YYYY-QN-
#

base_dir='/data/native/DISK_MSG_MPE/'
report=${base_dir}'Report_MPE.txt'
files=($(ls ${base_dir}*tar))
rm ${report}
for file in ${files[@]}
do
    basename=$(basename $file)
    subdir=$(echo ${basename:0:7})
    mkdir -p ${base_dir}$subdir
    echo "Uncompressing file ${file} ..."
    #tar -xf $file -C ${base_dir}$subdir/
    # Report on the number of files
    num=($(ls ${base_dir}$subdir/*gz | wc))
    echo "Number of files for ${subdir} is: ${num[0]}" >> $report
done


