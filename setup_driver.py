import subprocess
import urllib.request

import os

download_dir = os.path.expandvars('$HOME/Downloads')

file_path = os.path.join(download_dir, 'chromedriver.zip')
unpack_dir = '/usr/bin'

version = '2.35'
driver_url = 'https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip'.format(version)

urllib.request.urlretrieve(driver_url, file_path)

subprocess.run(['sudo', 'unzip', '-f', file_path, '-d', unpack_dir])
