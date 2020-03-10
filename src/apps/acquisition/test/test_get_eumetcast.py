from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from future import standard_library
standard_library.install_aliases()
from builtins import str
import unittest
import pycurl
import io
import io
from apps.acquisition.get_eumetcast import *
from database import querydb

#
class TestGetEumetcast(unittest.TestCase):
#
#     #   ---------------------------------------------------------------------------
#     #   Test get_eumetcast_info()
#     #   ---------------------------------------------------------------------------
#     def TestGetEumetcastInfo(self):
#         db = querydb.db
#         data_acquisitions = querydb.get_dataacquisitions(toJSON=False)
#
#         for row in data_acquisitions:
#             print row.data_source_id
#             # Retrieve datetime of latest acquired file and lastest datetime
#             # the acquisition was active of a specific eumetcast id
#             acq_dates = get_eumetcast.get_eumetcast_info(row.data_source_id)
#             if acq_dates:
#                 for key in acq_dates.keys():
#                     print "key: %s , value: %s" % (key, acq_dates[key])
#                 #print "time_latest_copy: "+acq_dates['time_latest_copy']
#                 #print "time_latest_exec: "+acq_dates['time_latest_exec']
#             else:
#                 print "Datasource " + row.data_source_id + " has not been activated!"
#             #logger.info('Datetime latest file: '+acq_dates)
#             #logger.info('Datetime last active: '+acq_dates)
#
#         self.assertEqual(1, 1)

    def test_GetEumetcats_PC2_nodir(self):

        remote_url='ftp://mesa-pc1//space/efts/fromTellicast/forEstation/'
        usr_pwd='mesadata:mesadata'
        d = pycurl.Curl()
        response = io.StringIO()
        d.setopt(pycurl.URL, remote_url)
        d.setopt(pycurl.USERPWD, usr_pwd)
        d.setopt(pycurl.FOLLOWLOCATION, 1)
        d.setopt(pycurl.WRITEFUNCTION, response.write)
        d.perform()
        d.close()
        current_list = []
        content=response.getvalue()
        lines = content.split('\n')
        for line in lines:
            check_line = len(str(line))
            if check_line is not 0:
                line_dir=line.split()[-1]
                current_list.append(line_dir)
        print (current_list)
        return current_list


    def test_GetEumetcats_PC2_homedir(self):
        filter_expression_jrc='/data/processing/*'
        ftp_eumetcast_url='ftp://mesa-pc2'
        ftp_eumetcast_userpwd='root:rootroot'
        current_list = get_list_matching_files_dir_ftp(ftp_eumetcast_url, ftp_eumetcast_userpwd, filter_expression_jrc)


    def test_GetEumetcast_Archives(self):

        print ('Start Test')
        get_archives_eumetcast()
        print ('Test Finished')
