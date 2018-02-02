#!/usr/bin/env python3
# sudo required

import urllib.request
import zipfile

import os

download_dir = os.path.expandvars('$HOME/Downloads')
file_path = os.path.join(download_dir, 'chromedriver.zip')

dest_dir = '/usr/bin'

version = '2.35'
driver_url = 'https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip'.format(version)

urllib.request.urlretrieve(driver_url, file_path)

with zipfile.ZipFile(file_path, "r") as zip_ref:
    zip_ref.extractall(dest_dir)
