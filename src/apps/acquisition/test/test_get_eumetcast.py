
from apps.acquisition import get_eumetcast
import unittest
from database import querydb
from database import query_db_filesys


class TestGetEumetcast(unittest.TestCase):

    #   ---------------------------------------------------------------------------
    #   Test get_eumetcast_info()
    #   ---------------------------------------------------------------------------
    def TestGetEumetcastInfo(self):
        db = querydb.db
        data_acquisitions = query_db_filesys.get_data_acquisitions(echo=True, toJSON=False)

        for row in data_acquisitions:
            print row.data_source_id
            # Retrieve datetime of latest acquired file and lastest datetime
            # the acquisition was active of a specific eumetcast id
            acq_dates = get_eumetcast.get_eumetcast_info(row.data_source_id)
            if acq_dates:
                for key in acq_dates.keys():
                    print "key: %s , value: %s" % (key, acq_dates[key])
                #print "time_latest_copy: "+acq_dates['time_latest_copy']
                #print "time_latest_exec: "+acq_dates['time_latest_exec']
            else:
                print "Datasource " + row.data_source_id + " has not been activated!"
            #logger.info('Datetime latest file: '+acq_dates)
            #logger.info('Datetime last active: '+acq_dates)

        self.assertEqual(1, 1)

