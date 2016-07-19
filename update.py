import os
import os.path
from subprocess import call
import urllib2
import json
import zipfile

github_url_base = "https://api.github.com"
latest_release_url = github_url_base + "/repos/wavesonics/adventurephotoframe/releases/latest"

version_file_name = '/app/config/VERSION'
CURRENT_VERSION = None
if os.path.isfile(version_file_name):
	with open(version_file_name, 'r') as version_file:
		CURRENT_VERSION = int(version_file.read())
		
if CURRENT_VERSION is not None:
	print "Current version: " + str(CURRENT_VERSION)
else:
	print "Current version: ---"

up_to_date = True
	
print "Checking for newer version..."
print latest_release_url

update_url = None

# Find the latest update
release_json = urllib2.urlopen(latest_release_url).read()
if release_json:
	release_info = json.loads(release_json)
	if release_info.get('tag_name'):
		latest_version = int(release_info['tag_name'])
		if CURRENT_VERSION is None or CURRENT_VERSION < latest_version:
			CURRENT_VERSION = latest_version
			up_to_date = False
			print "Found newer version: " + str(latest_version)
			if release_info.get('assets'):
				assets = release_info['assets']
				if len(assets) > 0 and assets[0].get('browser_download_url'):
					update_url = assets[0].get('browser_download_url')
		else:
			print "Already up to date"

if not up_to_date:
	# Download the update files
	temp_file_name = "/app/update/update.tmp"
	filename = "/app/update/update.zip"

	print "Downloading update..."

	print update_url

	with open(temp_file_name, 'wb') as f:
		f.write(urllib2.urlopen(update_url).read())
		if os.path.getsize(temp_file_name) > 0:
			print 'File download complete, move to complete'
			os.rename(temp_file_name, filename)
		else:
			print 'File download FAILED, delete temp'
			os.remove(temp_file_name)
			
	# Unzip and release update
	if os.path.isfile(filename):
		print "Extracting update..."
		zip = zipfile.ZipFile(filename)
		zip.extractall('/app')
		
		try:
			os.remove(filename)
		except OSError:
			print 'Failed to delete update file'
		
		print "Writing version file..."
		with open(version_file_name, "w") as version_file:
			version_file.write(str(CURRENT_VERSION))

		print "Update complete, rebooting."
		call(["/app/reboot.sh", ""])

	else:
		print "Download failed."
	
print "Complete."
