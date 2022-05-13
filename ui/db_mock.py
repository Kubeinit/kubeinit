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

from datetime import date
from os import environ
from sys import exit

from app import create_app

from config import config_dict

from models import DataCenter, db


get_config_mode = environ.get('KUBEINIT_CONFIG_MODE', 'Debug')

try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid KUBEINIT_CONFIG_MODE environment variable entry.')

app = create_app(config_mode)
app.app_context().push()

db.drop_all(app=app)
db.create_all(app=app)

cluster_1 = DataCenter(availability_zone='AZ1',
                       airport_name='MAD',
                       name='MAD-1',
                       created=date.today(),
                       location='Madrid')

cluster_2 = DataCenter(availability_zone='AZ1',
                       airport_name='MAD',
                       name='MAD-2',
                       created=date.today(),
                       location='Madrid')

cluster_3 = DataCenter(availability_zone='AZ1',
                       airport_name='MAD',
                       name='MAD-3',
                       created=date.today(),
                       location='Madrid')

cluster_4 = DataCenter(availability_zone='AZ1',
                       airport_name='MAD',
                       name='MAD-4',
                       created=date.today(),
                       location='Madrid')

db.session.add(cluster_1)
db.session.add(cluster_2)
db.session.add(cluster_3)
db.session.add(cluster_4)

db.session.commit()
