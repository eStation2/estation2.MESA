from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import httplib2
import os, io

from apiclient import discovery
from apiclient import http
from apiclient import errors

import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print ('Storing credentials to ' + credential_path)
    return credentials

def download_file(service, file_id, local_fd):
  """Download a Drive file's content to the local filesystem.

  Args:
    service: Drive API Service instance.
    file_id: ID of the Drive file that will downloaded.
    local_fd: io.Base or file object, the stream that the Drive file's
        contents will be written to.
  """
  request = service.files().get_media(fileId=file_id)
  fh = io.BytesIO()
  downloader = http.MediaIoBaseDownload(local_fd, request)
  done = False
  while done is False:
    status, done = downloader.next_chunk()
    print ("Download %d%%." % int(status.progress() * 100))

def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)

    output_dir = '/data/native/JRC_WBD/'

    # Get all files named as 'JRC_EXPORT'
    results = service.files().list(q="title contains 'JRC_EXPORT_'", maxResults=1000).execute()
    items = results.get('items', [])
    if not items:
        print ('No directory found.')
        return 1
    for jrc_file in items:

        # Get filename and folder ID
        filename = str(jrc_file['title'])
        print ("Processing filename = %s" % filename)
        #print ("Processing fileID = %s" % jrc_file['id'])
        parents = jrc_file['parents']
        # print ("Parent dir ID = %s" % parents[0]['id'])

        # Get date folder metadata
        date_folder = service.files().get(fileId=parents[0]['id']).execute()
        print ("File is in directory = %s" % date_folder['title'])
        date_string = str(date_folder['title']).replace('_','')+'01'

        folder_parents = date_folder['parents']

        # Get region folder metadata
        region_folder_id = folder_parents[0]['id']
        region_folder = service.files().get(fileId=region_folder_id).execute()
        #print ("Region directory is = %s" % region_folder['title'])

        # Selection criteria and output filename
        if region_folder['title'] == '2WAF':

            # Get from filename
            base_filename = os.path.splitext(filename)[0]
            tile_ext =  base_filename.split('-')[1]+'-'+base_filename.split('-')[2]

            out_filename =  'JRC-WBD_'+\
                            date_string +'_'+\
                            tile_ext+'.tif'
            print ("Output filename = %s" % out_filename)

            # Download the file
            full_filename = output_dir+os.path.sep+out_filename

            if not os.path.isfile(full_filename):
                try:
                    file_fd = io.FileIO(full_filename, mode='w', closefd=True)
                    download_file(service, jrc_file['id'],file_fd)
                    file_fd.close()
                except:
                    print ("Error in downloading file :  %s " % out_filename)
                    os.remove(out_filename)
            else:
                print ("File already exists:  %s " % out_filename)
                pass

if __name__ == '__main__':
    main()