# -*- coding: utf-8 -*-
#
# Kodi repository publish tool
#
# This tool publishes the src files for the repository into
# a valid repository package.
# 

# --- Python standard library ---
from __future__ import unicode_literals
from __future__ import division

import os
import glob
import hashlib
import shutil
import logging
import shutil
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

def build(addon_name: str, working_directory: str, source_path:str, dest_path:str):

    addon_xml_file = os.path.join(working_directory, source_path, addon_name, 'addon.xml')
    tree = ET.parse(addon_xml_file)
    addon_xml = tree.getroot()
    version = addon_xml.get('version')
    
    filename = f'{addon_name}-{version}.zip'
    
    output_zip_name  = os.path.join(working_directory, source_path, f'{addon_name}-{version}')
    output_file_name = os.path.join(working_directory, source_path, filename)
    directory_to_zip = os.path.join(working_directory, source_path)
    directory_to_mve = os.path.join(working_directory, source_path, addon_name)
    output_file_dest = os.path.join(working_directory, dest_path, addon_name, filename)
    directory_dest   = os.path.join(working_directory, dest_path, addon_name)
    addons_xml_path  = os.path.join(working_directory, dest_path, 'addons.xml')

    print(f'Zipping files in {directory_to_zip} into file {output_file_name}')
    shutil.make_archive(output_zip_name, 'zip', root_dir=directory_to_zip, base_dir=addon_name, verbose=True)

    print(f'Moving zip file to {output_file_dest}')
    os.replace(output_file_name, output_file_dest)

    print(f'Copying src files to {directory_dest}')
    source_files = glob.glob(f'{directory_to_mve}{os.sep}*.*', recursive=True)
    for source_file in source_files:
        dest_file = source_file.replace(directory_to_mve, directory_dest)
        print(f'Source: {source_file} to des: {dest_file}')
        shutil.copy(source_file, dest_file)
    
    print(f'Hashing {output_file_dest}')
    hash_file(output_file_dest)

    print('Creating new addons.xml for repository.')
    addons_element = ET.Element("addons")
    addons_element.append(addon_xml)

    xml_data = ET.tostring(addons_element, encoding='unicode')
    with open(addons_xml_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(str(xml_data))

    print(f'Hashing {addons_xml_path}')
    hash_file(addons_xml_path)

    print('Done')

def hash_file(fname):
    dest_file = f'{fname}.md5'
    md5_hash = md5(fname)
    with open(dest_file, 'w') as f:
        f.write(md5_hash)

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

try:
    working_directory    = os.getenv('PWD')
    addon_name           = os.getenv('ADDON_NAME')

    source_path          = os.getenv('REPOSITORY_SRC')
    dest_path            = os.getenv('REPOSITORY_DST')
    
    if not working_directory.endswith(os.path.sep):
        working_directory = f'{working_directory}{os.path.sep}'

    build(addon_name, working_directory, source_path, dest_path)
except Exception as ex:
    logger.fatal('Exception in tool', exc_info=ex)