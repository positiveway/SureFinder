#!/usr/bin/env python3.6
# sudo required

import subprocess
import urllib.request

import os

download_dir = os.path.expandvars('$HOME/Downloads')
unpack_dir = '/usr/bin'

download_path = os.path.join(download_dir, 'chromedriver.zip')

version = '2.35'
driver_url = 'https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip'.format(version)

urllib.request.urlretrieve(driver_url, download_path)

subprocess.run(['sudo', 'unzip', '-f', download_path, '-d', unpack_dir])
