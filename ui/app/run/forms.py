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


from flask_wtf import FlaskForm

from wtforms import StringField, TextField  # ValidationError
from wtforms.validators import DataRequired


class RunForm(FlaskForm):
    """
    Get the run form.

    This class renders the run form
    """

    namespace = TextField('Namespace',
                          id='namespace',
                          validators=[DataRequired()])
    collection = TextField('Collection',
                           id='collection',
                           validators=[DataRequired()])
    role = TextField('Role',
                     id='role',
                     validators=[DataRequired()])
    source = TextField('Source',
                       id='source')
    extra_vars = StringField('Extra vars',
                             id='extra_vars',
                             default='{}')
