from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
__author__ = 'analyst'
#
#	purpose: Run the script to copy data from an external disk to /data/processing
#	author:  M.Clerici
#	date:	 13.02.2019
#   descr:	 To be used for feeding an offline computer (e.g. for Training) with a subset from a disk
#
#	history: 1.0
#
import sys, os
import glob
from lib.python import es_logging as log
logger = log.my_logger('apps.es2system.ingest_archive')

def copy_data_disk(input_dir=None, dry_run=False):

    target_dir = '/data/processing/exchange/test_data/'

#   Define the list  products/version/mapsets

    prod_list = []

    prod_list.append({'prod'    :'arc2-rain',
                      'version' :'2.0',
                      'mapset'  : 'ARC2-Africa-11km',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'chirps-dekad',
                      'version' :'2.0',
                      'mapset'  : 'CHIRPS-Africa-5km',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'cpc-sm',
                      'version' :'1.0',
                      'mapset'  : 'CPC-Africa-50km',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'ecmwf-evpt',
                      'version' :'OPE',
                      'mapset'  : 'ECMWF-Africa-25km',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'ecmwf-rain',
                      'version' :'OPE',
                      'mapset'  : 'ECMWF-Africa-25km',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'fewsnet-rfe',
                      'version' :'2.0',
                      'mapset'  : 'FEWSNET-Africa-8km',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'gsod-rain',
                      'version' :'1.0',
                      'mapset'  : 'SPOTV-SADC-1km',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'lsasaf-et',
                      'version' :'undefined',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'lsasaf-lst',
                      'version' :'undefined',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'msg-mpe',
                      'version' :'undefined',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'modis-firms',
                      'version' :'v6.0',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[6789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'modis-firms',
                      'version' :'v6.0',
                      'mapset'  : 'SPOTV-Africa-10km',
                      'regex'   : '201[6789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'tamsat-rfe',
                      'version' :'2.0',
                      'mapset'  : 'TAMSAT-Africa-4km',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'vgt-dmp',
                      'version' :'V2.0',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[6789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'vgt-fapar',
                      'version' :'V2.0',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[6789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'vgt-fcover',
                      'version' :'V2.0',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[6789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'vgt-lai',
                      'version' :'V2.0',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[6789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'vgt-ndvi',
                      'version' :'sv2-pv2.2',
                      'mapset'  : 'SPOTV-Africa-1km',
                      'regex'   : '201[6789]*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    prod_list.append({'prod'    :'wd-gee',
                      'version' :'1.0',
                      'mapset'  : 'WD-GEE-ECOWAS-AVG',
                      'regex'   : '201*',
                      'regex2'  : '[0-9][0-9][0-9][0-9]_*'})

    # prod_list = []
    # prod_list.append({'prod'    :'vgt-ndvi',
    #                   'version' :'sv2-pv2.2',
    #                   'mapset'  : 'SPOTV-Africa-1km',
    #                   'regex'   : '201[6789]*',
    #                   'regex2'  : '[0-9][0-9][0-9][0-9]_*'})


    logger.info("Entering routine %s" % 'ingest_historical_archives')

    for prod in prod_list:

        sub_path='{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}'.format(
                prod['prod'],os.path.sep,
                prod['version'], os.path.sep,
                prod['mapset'], os.path.sep,
                '*', os.path.sep,
                '*', os.path.sep,
                prod['regex'], '*')
        full_path=input_dir+sub_path
        files = glob.glob(full_path)

        for myfile in files:
            target_file=myfile.replace(input_dir, target_dir)
            os.system('mkdir -p '+os.path.dirname(target_file))
            if not os.path.exists(target_file):
                os.system('cp ' + myfile + ' ' + target_file )
                print ('Copied file: '+target_file)
            # break

        if prod['regex2'] != '':
            sub_path = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}'.format(
                prod['prod'], os.path.sep,
                prod['version'], os.path.sep,
                prod['mapset'], os.path.sep,
                '*', os.path.sep,
                '*', os.path.sep,
                prod['regex2'], '*')
            full_path = input_dir + sub_path
            files = glob.glob(full_path)
            for myfile in files:
                target_file=myfile.replace(input_dir, target_dir)
                os.system('mkdir -p ' + os.path.dirname(target_file))
                if not os.path.exists(target_file):
                    os.system('cp ' + myfile + ' ' + target_file )
                    print ('Copied file: '+target_file)
                # break

if __name__=='__main__':

    # input_dir = str(sys.argv[0])
    input_dir = '/data/processing/'
    result = copy_data_disk(input_dir=input_dir)