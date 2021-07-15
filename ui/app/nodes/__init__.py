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


from flask import Blueprint

blueprint = Blueprint(
    'nodes_blueprint',
    __name__,
    url_prefix='/nodes',
    template_folder='templates',
    static_folder='static'
)


def get_position():
    """Get the position."""
    return 3


def get_category():
    """Get the category."""
    return 0


def get_name():
    """Get the name."""
    return "Nodes"


def get_icon():
    """Get the icon."""
    return "fa-server"


def get_endpoint():
    """Get the endpoint."""
    return "nodes_blueprint.nodes"
