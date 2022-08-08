#!/bin/python

import os
import requests
import xml.etree.ElementTree as ET

user = 'kubeinit'
password = os.environ.get('OPEN_BUILD_SERVICE')
url = "https://api.opensuse.org/build/home:kubeinit/_result"
r = requests.get(url, auth=(user, password))
build_status = r.text
tree = ET.fromstring(build_status)
print(build_status)
newsitems = []
for item in tree.findall('./result'):
    for child in item:
        if child.attrib['code'] == 'succeeded':
            print('The package: ' + child.attrib['package'] + " is OK")
        elif child.attrib['code'] == 'excluded':
            print('The package: ' + child.attrib['package'] + " is excluded")
        else:
            print('ERROR: Check!!! -- https://build.opensuse.org/project/monitor/home:kubeinit --')
            print(item.attrib['project'])
            print(item.attrib['repository'])
            print(item.attrib['arch'])
            print(item.attrib['code'])
            print(item.attrib['state'])
            print(child.attrib['package'])
            print(child.attrib['code'])
            sys.exit('FATAL')

