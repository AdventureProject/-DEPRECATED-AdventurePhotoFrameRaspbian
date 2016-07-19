import os
import os.path
import urllib2
import urllib

def get_file_contents(file_path):
    contents = None
    with open(file_path, 'r') as file:
        contents = file.read()
    return contents

print('Health check in...')

version = get_file_contents('/app/config/VERSION')
if version is None:
    version = 0

errors = get_file_contents('/app/logs/app_errors.log')
data = urllib.urlencode({'errors' : errors})

PHOTO_FRAME_ID = get_file_contents( '/app/config/PHOTO_FRAME_ID' )
if PHOTO_FRAME_ID is None:
	log('WARNING: PhotoFrame ID is missing!')
else:
    url = 'http://wethinkadventure.rocks/health/' + PHOTO_FRAME_ID + '?version=' + version
    print(url)
    request = urllib2.Request(url, data)
    response = urllib2.urlopen(request)
    
    print(response.read())
