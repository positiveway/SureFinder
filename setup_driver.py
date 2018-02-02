#!/usr/bin/env python3
# sudo required

import urllib.request
import zipfile

import os
import stat

download_dir = os.path.expandvars('$HOME/Downloads')
unpack_dir = '/usr/bin'

download_path = os.path.join(download_dir, 'chromedriver.zip')
unpack_path = os.path.join(unpack_dir, 'chromedriver')

version = '2.35'
driver_url = 'https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip'.format(version)

urllib.request.urlretrieve(driver_url, download_path)

with zipfile.ZipFile(download_path, "r") as zip_ref:
    zip_ref.extractall(unpack_dir)

st = os.stat(unpack_path)
os.chmod(unpack_path, st.st_mode | stat.S_IEXEC)
