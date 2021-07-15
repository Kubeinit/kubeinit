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

import os
import re
from importlib import import_module
from logging import ERROR, basicConfig, getLogger
from os import path

from flask import Flask, url_for

# from flask_login import LoginManager

app = Flask(__name__, static_folder='base/static')


def register_blueprints(app):
    """
    Register the blueprints.

    This method will register the blueprints
    """
    pattern = re.compile("^([a-z]+)+$")

    to_register = []
    for module_name in next(os.walk('./app'))[1]:
        if (pattern.match(module_name)):
            to_register.append(module_name)

    for module_name in to_register:
        print("Registering: %s" % (module_name))
        module = import_module('app.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)
        if module_name == "run":
            print("asdf")
            print(dir(module.blueprint))


def configure_logs(app):
    """
    Configure logs.

    This method will return the logger
    """
    # soft logging
    try:
        # TODO:FIXME:CCAMACHO
        # Having the logger in the console will make it explode
        basicConfig(filename='error.log', level=ERROR)
        logger = getLogger()
        logger.disabled = True
        # logger.addHandler(StreamHandler())
    except Exception:
        pass


def apply_themes(app):
    """
    Add support for themes.

    If DEFAULT_THEME is set then all calls to
      url_for('static', filename='')
      will modfify the url to include the theme name

    The theme parameter can be set directly in url_for as well:
      ex. url_for('static', filename='', theme='')

    If the file cannot be found in the /static/<theme>/ location then
      the url will not be modified and the file is expected to be
      in the default /static/ location
    """
    @app.context_processor
    def override_url_for():
        """
        Override the URL.

        This method will override the URLs
        """
        return dict(url_for=_generate_url_for_theme)

    def _generate_url_for_theme(endpoint, **values):
        """
        Generate the URLs.

        This method will generate the URLs
        """
        if endpoint.endswith('static'):
            themename = values.get('theme', None) or \
                app.config.get('DEFAULT_THEME', None)
            if themename:
                theme_file = "{}/{}".format(themename,
                                            values.get('filename', ''))
                if path.isfile(path.join(app.static_folder, theme_file)):
                    values['filename'] = theme_file
        return url_for(endpoint, **values)


def render_menu():
    """Render the menu."""
    # We only support tree main categories
    pattern = re.compile("^([a-z]+)+$")
    to_render = []
    for module_name in next(os.walk('./app'))[1]:
        if (pattern.match(module_name) and module_name != 'home' and module_name != 'base'):
            to_render.append(module_name)
    menu = [[], [], []]
    for module_name in to_render:
        module = import_module('app.{}'.format(module_name))
        item = {'position': module.get_position(),
                'category': module.get_category(),
                'name': module.get_name(),
                'icon': module.get_icon(),
                'endpoint': module.get_endpoint(),
                }
        menu[item['category']].append(item)

    cat0 = sorted(menu[0], key=lambda k: k['position'], reverse=False)
    cat1 = sorted(menu[1], key=lambda k: k['position'], reverse=False)
    cat2 = sorted(menu[2], key=lambda k: k['position'], reverse=False)

    return [cat0, cat1, cat2]


def create_app(config, selenium=False):
    """
    Create the app.

    This method will create the app
    """
    # app = Flask(__name__, static_folder='base/static')
    app.config.from_object(config)
    if selenium:
        app.config['LOGIN_DISABLED'] = True
    configure_logs(app)
    apply_themes(app)
    register_blueprints(app)
    app.jinja_env.globals.update(render_menu=render_menu)
    return app
