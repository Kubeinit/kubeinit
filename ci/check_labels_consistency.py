#!/usr/bin/env python

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

import re

from kubeinit_ci_utils import get_periodic_jobs_labels

import requests

url = 'https://api.github.com/repos/kubeinit/kubeinit/labels'

params = dict(
    page=1,
    per_page=100
)

resp = requests.get(url=url, params=params)
data = resp.json()
github_public_labels = []
for label in data:
    label_name = label['name']
    if re.match(r"[a-z|0-9|\.]+-[a-z]+-[0-9]-[0-9]-[0-9]-[c|h]",
                label_name):
        github_public_labels.append(label_name)

print("'check_labels_consistency.py' ==> Pull labels list from the periodic jobs definition")
ci_labels = get_periodic_jobs_labels()

github_public_labels.sort()
ci_labels.sort()

if(github_public_labels == ci_labels):
    print("Both CI labels list match")
else:
    print("'check_labels_consistency.py' ==> There is a mismatch between the labels tested in the periodic jobs")
    print("'check_labels_consistency.py' ==> and the available GitHub labels for running the CI jobs.")
    print("'check_labels_consistency.py' ==> the difference is:")
    print(set(github_public_labels).symmetric_difference(set(ci_labels)))
    raise Exception("'check_labels_consistency.py' ==> STOP!")
