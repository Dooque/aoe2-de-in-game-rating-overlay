# -*- coding: utf-8 -*-
#!/usr/bin/python3

#
# python -m pysimplegui-exemaker.pysimplegui-exemaker
#

import os
import requests
import shutil
import sys
import zipfile

# If executable name ends with .py extension is because we're running it from source code.
DEBUG = sys.argv[0].endswith('.py')
DEBUG_FILE = 'aoe2de-igro.log'
def DebugMsg(msg):
    if DEBUG:
        print(msg)
    else:
        with open(DEBUG_FILE, 'a') as file:
            file.write(msg + '\r\n')

DebugMsg('¡Starting Update!')

EXEC_FILE = '18be0bfe0ac4c030e8c559ae0acec43d.exe'
HASH_NUMBER = '901014CF3D89AF19EBB94C5E06A768D63EDEF307E3C0A78F110810D0586B1604'
#VERSION_FILE_URL = 'https://raw.github.com/Dooque/aoe2-de-in-game-rating-overlay/develop/VERSION'
VERSION_FILE_URL = 'https://raw.github.com/Dooque/aoe2-de-in-game-rating-overlay/test/VERSION'
VERSION_FILE_CURRENT = './VERSION'

#DOWNLOAD_URL = 'https://github.com/Dooque/aoe2-de-in-game-rating-overlay/archive/refs/tags/{version}.zip'
DOWNLOAD_URL = 'https://raw.github.com/Dooque/aoe2-de-in-game-rating-overlay/test/{version}.zip'

def update(new_version):
    os.mkdir('./tmp')
    response = requests.get(DOWNLOAD_URL.format(version=new_version))
    with open('./tmp/{version}.zip'.format(version=new_version), 'wb') as zip_file:
        zip_file.write(response.content)
    with zipfile.ZipFile('./tmp/{version}.zip'.format(version=new_version), 'r') as zip_file:
        zip_file.extractall('./tmp/')
    src_file = './tmp/aoe2-de-in-game-rating-overlay-{version}/{exe}'.format(version=new_version[1:], exe=EXEC_FILE)
    dst_file = './{exe}'.format(exe=EXEC_FILE)
    os.remove(dst_file)
    shutil.move(src_file, dst_file)

if __name__ == '__main__':
    version_file = open(VERSION_FILE_CURRENT)
    current_version = version_file.read()
    version_file.close()
    new_version = requests.get(VERSION_FILE_URL).text
    if DEBUG:
        os.system('python aoe2de-in-game-rating-overlay.py {hash} 0'.format(hash=HASH_NUMBER))
    else:
        if current_version != new_version:
            update(new_version)
            os.system('{exec} {hash} 1'.format(exec=EXEC_FILE, hash=HASH_NUMBER))
        else:
            os.system('{exec} {hash} 0'.format(exec=EXEC_FILE, hash=HASH_NUMBER))

