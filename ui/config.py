#!/usr/bin/env python

"""
Copyright 2019 Kubeinit (kubeinit.com).

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
from os import environ
# import secrets


class Config(object):
    """
    Get the global config.

    This method gets the global configuration
    """

    basedir = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = "KeYkEyKeY"  # secrets.token_urlsafe(16)

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,
                                                          'database.db')

    # For 'in memory' database, please use:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # THEME SUPPORT
    #  if set then url_for('static', filename='', theme='')
    #  will add the theme name to the static URL:
    #    /static/<DEFAULT_THEME>/filename
    # DEFAULT_THEME = "themes/dark"
    DEFAULT_THEME = None

    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    """
    Get the production config.

    This method gets the prod configuration
    """

    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        environ.get('DATABASE_USER', 'kuebinit'),
        environ.get('DATABASE_PASSWORD', 'kuebinit'),
        environ.get('DATABASE_HOST', 'localhost'),
        environ.get('DATABASE_PORT', 5432),
        environ.get('DATABASE_NAME', 'kuebinit')
    )


class DebugConfig(Config):
    """
    Enable the debug config.

    This is a main class
    """

    DEBUG = True


config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
