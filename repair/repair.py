# Repair Tool
# for Microsoft Windows 10
# in regards to the missing search icons
#
# Author: Brendon LaRusic
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

    # remove existing `_output` directory from previous runs
    shutil.rmtree(runDir + '\\_output', ignore_errors=True)
  
    # define sorting folders
    rawStore = runDir + '\\_output\\raw'
    jpgStore = runDir + '\\_output\\jpg'
    fixedStore = runDir + '\\_output\\fixed'
    toolkit = runDir + '\\toolkit'
    iconsStore = runDir + '\\icons'

    # copy cortana icon cache to the sorting folders
    print('copying files...')
    copyDirectory(iconCache, rawStore)
    copyDirectory(iconCache, jpgStore)

    # append .jpg to end of files
    print('renaming files...')
    for filename in os.listdir(jpgStore):
        os.rename(jpgStore+'\\'+filename, jpgStore+'\\'+filename + '.jpg')

    # read contents of all example corrupt files into a dictionary in memory for later comparison
    print('reading example corrupt files...')
    corruptFileExamplesDict = {}
    for filename in os.listdir(toolkit):
        if 'compare' in filename:
            with open(toolkit+'\\'+filename, 'r', errors='ignore') as f:
                corruptFileExamplesDict[filename] = f.read()
    
    # read the contents of rawStore into a dictionary in memory for later comparison
    print('reading raw files...')
    rawFilesDict = {}
    for filename in os.listdir(rawStore):
        with open(rawStore+'\\'+filename, 'r', errors='ignore') as f:
            rawFilesDict[filename] = f.read()

    # delete each raw file from disk for each file whose contents doesn't match any of the example file contents in the corruptFileExamples dictionary
    print('comparing file contents of example corrupt files and raw files...')
    for filename in rawFilesDict:
        if rawFilesDict[filename] not in corruptFileExamplesDict.values():
            os.remove(rawStore+'\\'+filename)

    # load known icon fixes
    print('repairing known icons...')
    knownIcons = json.load(open(toolkit+'\\repairs.json'))
   
    # repair icons
    for icon in knownIcons['repairs']:
        # create `fixed` directory
        if not os.path.isdir(fixedStore):
            os.mkdir(fixedStore)
        
        # delete the corrupted file
        exists = os.path.isfile(rawStore+'\\'+icon['corrupt'])
        if exists:           
            # copy the icon fix to the `fixed` directory keeping the same filename as the corrupted file
            shutil.copy(iconsStore+'\\'+ icon['repair'], fixedStore+'\\'+icon['corrupt'])

            # delete the corrupted file
            os.remove(rawStore+'\\'+icon['corrupt'])

            print('repaired icon: ' + icon['title'])
    
    # override icon cache with the fixed files
    print('overwriting icon cache...')
    copyDirectory(fixedStore, iconCache)

    # finished
    print('---------')
    print('finished!')
		
if __name__ == '__main__':
    main()
