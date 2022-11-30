#!/bin/python3

"""
Copyright kubeinit contributors.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import os
import sys
import xml.etree.ElementTree as ETree

import requests

user = os.environ.get("OPEN_BUILD_SERVICE_USER")
password = os.environ.get("OPEN_BUILD_SERVICE_PASSWORD")
url = "https://api.opensuse.org/build/home:kubeinit/_result"
r = requests.get(url, auth=(user, password))
build_status = r.text
print(build_status)
if str(r.status_code) != "200":
    sys.exit('FATAL: This should return a 200')
tree = ETree.fromstring(build_status)
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
