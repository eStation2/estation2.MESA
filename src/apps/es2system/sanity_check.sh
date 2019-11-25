#!/bin/sh
# ES2-478: sanity check on the ingested/derived products

# Check (ONLY) the files under /data/processing 
if [[ $1 == 'test' ]]; then
find /data/processing -type f -name '[1-2][0-9]*.tif' -print0 | while IFS= read -r -d '' file; do gdalinfo "$file" > /dev/null 2>/dev/null; if [[ $? == 1 ]]; then printf '%s\n' "$file"; fi; done
fi

# Check the files under /data/processing and move under /data/wrong_files (temporary -> to be deleted)
if [[ $1 == 'move' ]]; then
find /data/processing -type f -name '[1-2][0-9]*.tif' -print0 | while IFS= read -r -d '' file; do gdalinfo "$file" > /dev/null 2>/dev/null; if [[ $? == 1 ]]; then mv "$file" /data/wrong_files/; fi; done
fi

# Remove the files under /data/processing and remove
if [[ $1 == 'remove' ]]; then
find /data/processing -type f -name '[1-2][0-9]*.tif' -print0 | while IFS= read -r -d '' file; do gdalinfo "$file" > /dev/null 2>/dev/null; if [[ $? == 1 ]]; then rm "$file" ; fi; done
fi

# Parse the contents of /data/wrong_files/ and check if recomputed ok
if [[ $1 == 're-test' ]]; then
files=($(ls /data/wrong_files/ | sort))
for myfile in ${files[@]} 
do
echo "Looking for file:" $myfile 
find /data/processing/ -name $myfile -print0 | while IFS= read -r -d '' file; do gdalinfo $file >/dev/null 2> /dev/null; 
if [[ $? == 0 ]]; then 
echo "File recomputed OK:" $file; 
else
echo "File still wrong  :" $file; 
fi 
done
done
fi


