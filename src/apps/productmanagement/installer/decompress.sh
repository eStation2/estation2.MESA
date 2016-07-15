#!/bin/bash
echo ""
echo "Self Extracting Archive for eStation 2.0"
echo ""

if [[ `id -un` != 'analyst' ]]; then
    zenity --error --title="Wrong User" --text="You must be analyst [Thematic user] to run the extraction"
    exit
fi

LOGFILE=/eStation2/log/request.archive.decompress.log

BASE_DATA_DIR='/data/processing/'
echo " `date +%Y-%m-%d_%H:%M:%S` WARNING: the script considers data are under: ${BASE_DATA_DIR}" >> $LOGFILE

BASENAME=`basename $0`
echo " `date +%Y-%m-%d_%H:%M:%S` Working on Archive $BASENAME" >> $LOGFILE

export TMPDIR=`mktemp -d /tmp/eStation2/selfextract.archive.XXXXXX`

ARCHIVE=`awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' $0`

tail -n+$ARCHIVE $0 | tar xzv -C ${TMPDIR} >> /dev/null

CDIR=`pwd`
cd $TMPDIR
if [[ `find ./ -name *.tif -print | wc | awk {'print $1'} ` -gt 20 ]]; then
    find ./ -name *.tif -print | head -20 > message.txt
    echo "\n .... and additional files ..." >> message.txt
else
    find ./ -name *.tif -print > message.txt
fi

zenity --question --title="Extract files" --text="The following files will be extracted:\n\n `cat message.txt`" --no-wrap
if [[ $? -eq 0 ]]; then
    files=($(find ./ -name "*.tif"))
    for file in ${files[@]}
    do
        # Ensure target subdir exists
	    subdir=`dirname $file`
	    mkdir -p /data/processing/$subdir

	    echo "  --> Moving file: `basename $file`"  >> $LOGFILE
	    mv $file /data/processing/$file
    done
    zenity --info --title='Exit' --text="Files have been extracted to ${BASE_DATA_DIR}"
else
    zenity --info --title='Exit' --text='Exit without extracting archive contents'
fi
cd $CDIR
rm -rf $TMPDIR
exit 0

__ARCHIVE_BELOW__
