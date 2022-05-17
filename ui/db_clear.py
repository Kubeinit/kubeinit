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


from os import environ
from sys import exit

from app import create_app

from config import config_dict

from models import db


get_config_mode = environ.get('KUBEINIT_CONFIG_MODE', 'Debug')

try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid KUBEINIT_CONFIG_MODE environment variable entry.')

app = create_app(config_mode)
app.app_context().push()

db.drop_all(app=app)
db.create_all(app=app)
