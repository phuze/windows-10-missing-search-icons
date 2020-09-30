# Repair Tool
# for Microsoft Windows 10
# in regards to the missing search icons
#
# Author: Brendon LaRusic
# Email: brendon@larusic.ca
# Created: January 5th, 2020

from distutils.dir_util import copy_tree as copyDirectory
from pathlib import Path
import shutil
import hashlib
import json
import sys
import os

def main():
    # get the windows username
    print('fetching username...')
    username = os.getlogin()

    # construct the path to the cortana cache
    appName = 'Microsoft.Windows.Search_cw5n1h2txyewy'
    iconCache = 'C:\\Users\\'+username+'\\AppData\\Local\\Packages\\'+appName+'\\LocalState\\AppIconCache\\100'

    # the directory this script is in
    runDir = os.path.dirname(os.path.abspath( __file__ ))

    # remove existing `_reuslt` directory
    shutil.rmtree(runDir + '\\_output', ignore_errors=True)
  
    # define sorting folders
    rawStore = runDir + '\\_output\\raw'
    jpgStore = runDir + '\\_output\\jpg'
    corruptStore = runDir + '\\_output\\corrupt'
    fixedStore = runDir + '\\_output\\fixed'

    # copy cortana icon cache to the sorting folders
    print('copying files...')
    copyDirectory(iconCache, rawStore)
    copyDirectory(iconCache, jpgStore)
    copyDirectory(iconCache, corruptStore)

    # append .jpg to end of files
    print('renaming files...')
    for filename in os.listdir(jpgStore):
        os.rename(jpgStore+'\\'+filename, jpgStore+'\\'+filename + '.jpg')

    # identify the corrupted icons
    print('identifying corrupt icons...')
    for filename in os.listdir(corruptStore):
        match1 = match2 = match3 = None
        match1 = open(corruptStore+'\\'+filename,'rb').read() == open('toolkit\\compare1','rb').read()
        match2 = open(corruptStore+'\\'+filename,'rb').read() == open('toolkit\\compare2','rb').read()
        match3 = open(corruptStore+'\\'+filename,'rb').read() == open('toolkit\\compare3','rb').read()
        if match1 or match2 or match3:
            print('corrupt icon found: ~\\'+filename)
        else:
            os.remove(corruptStore+'\\'+filename)

    # load known icon fixes
    print('repairing known icons...')
    knownIcons = json.load(open('toolkit\\repairs.json'))
   
    # repair icons
    for icon in knownIcons['repairs']:

        # create `fixed` directory
        if not os.path.isdir(fixedStore):
            os.mkdir(fixedStore)
        
        # delete the corrupted file
        exists = os.path.isfile(corruptStore+'\\'+icon['corrupt'])
        if exists:           
            # copy the icon fix to the `fixed` directory
            # keeping the same filename as the corrupted file
            shutil.copyfile('icons\\'+icon['repair'], fixedStore+'\\'+icon['corrupt'])

            # delete the corrupted file
            os.remove(corruptStore+'\\'+icon['corrupt'])

            print('repaired icon: ' + icon['title'])

    # finished
    print('---------')
    print('finished!')
		
if __name__ == '__main__':
    main()